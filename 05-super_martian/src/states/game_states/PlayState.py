"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

from typing import Dict, Any

import pygame

from gale.camera import Camera
from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer
from gale.tilemap import CollisionType, collision_type_at

import settings
from src.Clock import Clock
from src.GameLevel import GameLevel
from src.Player import Player

def _find_spawn_y(tilemap, col: int, entity_height: int) -> float:
        """
        Recorre la columna col de arriba hacia abajo buscando el primer tile
        sólido/plataforma en la capa 'ground', y devuelve el y justo encima de
        su superficie — funciona para cualquier diseño de nivel, en vez de
        asumir una fila de piso fija.
        """
        for row in range(tilemap.rows):
            if collision_type_at(tilemap, "ground", row, col) != CollisionType.NONE:
                return row * tilemap.tile_height - entity_height

        return 0.0

class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params.get("level", 1)
        fresh_level = enter_params.get("game_level") is None
        self.game_level = enter_params.get("game_level")
        if self.game_level is None:
            self.game_level = GameLevel(
                self.level, on_level_complete=self._on_level_complete
            )
            pygame.mixer.music.load(
                settings.BASE_DIR / "assets" / "sounds" / "music_grassland.ogg"
            )
            pygame.mixer.music.play(loops=-1)

        self.tilemap = self.game_level.tilemap
        # Resting exactly on the ground tile's surface rather than a few
        # pixels into it, so gale.tilemap's one-way platform collision
        # (which requires the entity to already be at/above the surface)
        # picks it up on the very first frame instead of falling through.
        spawn_y = _find_spawn_y(self.tilemap, 0, 20)
        self.player = enter_params.get("player")
        if self.player is None:
            self.player = Player(0, spawn_y, self.game_level)
            self.player.change_state("idle")
        elif fresh_level:
            # Reused player crossing into a brand new level: keep their
            # score/coins, but reset position/velocity for the new map.
            self.player.x, self.player.y = 0, spawn_y
            self.player.vx, self.player.vy = 0, 0
            self.player.game_level = self.game_level
            self.player.tilemap = self.tilemap
            self.player.change_state("idle")

        self.camera = enter_params.get("camera")

        if self.camera is None or fresh_level:
            self.camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
            self.camera.follow(self.player, rate=settings.CAMERA_FOLLOW_RATE)
            self.camera.bounds = self.game_level.get_rect()
            self.camera.x, self.camera.y = self.player.x, self.player.y
            self.camera.update(0)

        self.clock = enter_params.get("clock")
        self.level_complete = False

        if self.clock is None or fresh_level:
            self.clock = Clock(30)

            def countdown_timer():
                if self.level_complete:
                    return

                self.clock.count_down()

                if 0 < self.clock.time <= 5:
                    settings.SOUNDS["timer"].play()

                if self.clock.time == 0:
                    self.player.change_state("dead")

            Timer.every(1, countdown_timer)
        else:
            Timer.resume()

        # Fade transition: fresh levels fade in from black; resuming from
        # pause shows the scene immediately with no overlay.
        self.fade_surface = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )
        self.fade_surface.fill((0, 0, 0, 255))

        if fresh_level:
            self.fade_alpha = 255.0
            Timer.tween(
                0.6, [(self, {"fade_alpha": 0.0})], ease_function_name="out_quad"
            )
        else:
            self.fade_alpha = 0.0

    def _on_level_complete(self) -> None:
        self.level_complete = True
        Timer.tween(
            1.0,
            [(self, {"fade_alpha": 255.0})],
            ease_function_name="in_quad",
            on_finish=self._go_to_next_level,
        )

    def _go_to_next_level(self) -> None:
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        Timer.clear()
        next_level = self.level + 1

        if next_level > settings.NUM_LEVELS:
            self.state_machine.change("game_over", self.player, victory=True)
        else:
            self.player.score = 0
            self.state_machine.change("play", level=next_level, player=self.player)

    def update(self, dt: float) -> None:
        if self.player.is_dead:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            Timer.clear()
            self.state_machine.change("game_over", self.player, level=self.level)

        self.player.update(dt)

        if self.player.y >= self.tilemap.pixel_height:
            self.player.change_state("dead")

        self.camera.update(dt)
        self.game_level.update(dt, self.player)

        if not self.level_complete:
            for creature in self.game_level.creatures:
                if self.player.collides(creature):
                    self.player.change_state("dead")

            for item in self.game_level.items:
                if not item.active or not item.collidable:
                    continue

                if self.player.collides(item):
                    item.on_collide(self.player)
                    item.on_consume(self.player)

    def render(self, surface: pygame.Surface) -> None:
        self.game_level.render(surface, self.camera)
        self.player.render(surface, self.camera)

        render_text(
            surface,
            f"Score: {self.player.score}",
            settings.FONTS["small"],
            5,
            5,
            (255, 255, 255),
            shadowed=True,
        )

        render_text(
            surface,
            f"Time: {self.clock.time}",
            settings.FONTS["small"],
            settings.VIRTUAL_WIDTH - 60,
            5,
            (255, 255, 255),
            shadowed=True,
        )

        if self.fade_alpha > 0:
            self.fade_surface.set_alpha(round(self.fade_alpha))
            surface.blit(self.fade_surface, (0, 0))

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "pause" and input_data.pressed:
            Timer.pause()
            self.state_machine.change(
                "pause",
                level=self.level,
                camera=self.camera,
                game_level=self.game_level,
                player=self.player,
                clock=self.clock,
            )
        else:
            self.player.on_input(input_id, input_data)
