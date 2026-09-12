"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class GameLevel.
"""

import random
from typing import Any, Dict, Optional, Callable

import pygame

from gale.tilemap import CollisionType, collision_type_at, load_tiled_map
from gale.timer import Timer

import settings
from src.Creature import Creature
from src.FlyingCreature import FlyingCreature
from src.GameEntity import GameEntity
from src.GameItem import GameItem
from src.definitions import creatures, items


class GameLevel:
    def __init__(self, num_level: int, on_level_complete: Optional[Callable[[], None]] = None) -> None:
        self.tilemap = load_tiled_map(settings.TILEMAPS[num_level])
        self.creatures = []
        self.items = []
        self.on_level_complete = on_level_complete
        self.key_block = self._load_key_block()

        for obj in self.tilemap.object_layers.get("creatures", []):
            self.add_creature(
                {
                    "tile_index": obj.properties["tile_index"],
                    "x": obj.x,
                    "y": obj.y,
                    "width": obj.width,
                    "height": obj.height,
                }
            )

        for obj in self.tilemap.object_layers.get("coins", []):
            self.add_item(
                {
                    "item_name": "coins",
                    "frame_index": obj.properties["frame_index"],
                    "x": obj.x,
                    "y": obj.y,
                    "width": obj.width,
                    "height": obj.height,
                }
            )



        self._schedule_flying_creature_spawn()

    def add_item(self, item_data: Dict[str, Any]) -> None:
        item_name = item_data.pop("item_name")
        definition = items.ITEMS[item_name][item_data["frame_index"]]
        definition.update(item_data)
        self.items.append(GameItem(**definition))

    def add_creature(self, creature_data: Dict[str, Any]) -> None:
        definition = creatures.CREATURES[creature_data["tile_index"]]
        self.creatures.append(
            Creature(
                creature_data["x"],
                creature_data["y"],
                creature_data["width"],
                creature_data["height"],
                self,
                **definition,
            )
        )

    def _load_key_block(self) -> Optional[Dict[str, Any]]:
        objs = self.tilemap.object_layers.get("key_block", [])

        if not objs:
            return None

        obj = objs[0]
        row, col = self.tilemap.tile_at(obj.x, obj.y)

        return {
            "row": row,
            "col": col,
            "x": col * self.tilemap.tile_width,
            "y": row * self.tilemap.tile_height,
            # +1 porque las properties del tile se guardan con el id
            # 0-based del tileset, pero la grilla de la capa de tiles
            # guarda el gid, que es 1-based (el tileset de este mapa
            # arranca en firstgid=1).
            "gid": obj.properties["tile_index"] + 1,
            "target_score": obj.properties["target_score"],
            "spawned": False,
            "triggered": False,
        }

    def _update_key_block(self, player: Any) -> None:
        kb = self.key_block

        if kb is None or kb["triggered"]:
            return

        if not kb["spawned"]:
            if player.score >= kb["target_score"]:
                kb["spawned"] = True
                self.tilemap.set_gid("ground", kb["row"], kb["col"], kb["gid"])
            return

        if not player.hit_ceiling:
            return

        block_rect = pygame.Rect(
            kb["x"], kb["y"], self.tilemap.tile_width, self.tilemap.tile_height
        )

        if player.get_collision_rect().colliderect(block_rect.inflate(0, 4)):
            kb["triggered"] = True
            self._spawn_key(kb)

    def _spawn_key(self, kb: Dict[str, Any]) -> None:
        key_item = GameItem(
            x=kb["x"],
            y=kb["y"],
            width=16,
            height=16,
            texture_id="key",
            frame_index=0,
            collidable=False,
            consumable=True,
            on_consume=self._consume_key,
        )
        self.items.append(key_item)

        final_y = kb["y"] + self.tilemap.tile_height

        def enable_pickup() -> None:
            key_item.collidable = True

        Timer.tween(
            0.5,
            [(key_item, {"y": final_y})],
            ease_function_name="out_bounce",
            on_finish=enable_pickup,
        )

    def _consume_key(self, key_item: GameItem, player: Any) -> None:
        settings.SOUNDS["level_complete"].play()

        if self.on_level_complete is not None:
            self.on_level_complete()


    def _schedule_flying_creature_spawn(self) -> None:
        delay = random.uniform(
            settings.FLYING_CREATURE_MIN_SPAWN_DELAY,
            settings.FLYING_CREATURE_MAX_SPAWN_DELAY,
        )
        Timer.after(delay, self._spawn_flying_creature)

    def _pick_open_row(self, col: int) -> Optional[int]:
        """
        Scans column col from the top down and returns a random row
        strictly above the first solid/platform tile found there (with one
        extra row of buffer so the creature is unambiguously flying in open
        air, not skimming the surface), or None if the column has no clear
        row at all to spawn in.
        """
        first_solid_row = self.tilemap.rows

        for row in range(self.tilemap.rows):
            if (
                collision_type_at(self.tilemap, GameEntity.COLLISION_LAYER, row, col)
                != CollisionType.NONE
            ):
                first_solid_row = row
                break

        max_row = first_solid_row - 2

        if max_row < 0:
            return None

        return random.randint(0, max_row)

    def _spawn_flying_creature(self) -> None:
        from_left = random.choice([True, False])
        col = 0 if from_left else self.tilemap.cols - 1
        row = self._pick_open_row(col)

        if row is not None:
            definition = random.choice(creatures.FLYING_CREATURES)
            x = 0 if from_left else self.tilemap.pixel_width - 16
            y = row * self.tilemap.tile_height
            direction = "right" if from_left else "left"
            self.creatures.append(
                FlyingCreature(x, y, 16, 16, self, direction, **definition)
            )

        self._schedule_flying_creature_spawn()

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(0, 0, self.tilemap.pixel_width, self.tilemap.pixel_height)

    def update(self, dt: float, player: Optional[Any] = None) -> None:
        for creature in self.creatures:
            creature.update(dt)

        # Remove dead creatures
        self.creatures = [
            creature for creature in self.creatures if not creature.is_dead
        ]

        if player is not None:
            self._update_key_block(player)

    def render(self, surface: pygame.Surface, camera: Any) -> None:
        self.tilemap.render(surface, camera)
        for creature in self.creatures:
            creature.render(surface, camera)
        for item in self.items:
            if item.active:
                item.render(surface, camera)
