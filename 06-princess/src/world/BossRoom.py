"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

This file contains the class BossRoom: a Room specialization used for the
dungeon's boss encounter. No creatures, pots, switches, or chest -- just
the Boss, standing opposite the single doorway (the one the player just
walked in through). That doorway starts closed, like any freshly-entered
room, and the Boss reopens it once defeated.
"""

from typing import Callable, List, TypeVar

import settings
from src.Boss import Boss
from src.world.Doorway import Doorway
from src.world.Room import Room

_OPPOSITE = {"top": "bottom", "bottom": "top", "left": "right", "right": "left"}


class BossRoom(Room):
    def __init__(
        self,
        player: TypeVar("Player"),
        on_game_over: Callable[[], None],
        entrance_direction: str,
    ) -> None:
        self._entrance_direction = entrance_direction
        super().__init__(player, on_game_over)
        self._spawn_boss()

    def _generate_entities(self) -> None:
        # The boss is added after doorways exist (see __init__/_spawn_boss),
        # not here -- it needs to know where the entrance is to stand
        # opposite it.
        self.entities = []

    def _generate_objects(self) -> None:
        # No pots, switches, hearts, or chest in the boss room.
        self.objects = []

    def _generate_doorways(self) -> List[Doorway]:
        return [Doorway(self._entrance_direction, False, self)]

    def _spawn_boss(self) -> None:
        exit_side = _OPPOSITE[self._entrance_direction]
        x, y = self._position_for(exit_side)
        boss = Boss(x, y, on_defeated=self._on_boss_defeated)
        self.entities.append(boss)

    def _on_boss_defeated(self) -> None:
        self.doorways[0].open = True
        settings.SOUNDS["door"].play()

    def _position_for(self, side: str):
        center_x = (
            settings.MAP_RENDER_OFFSET_X
            + settings.MAP_WIDTH // 2 * settings.TILE_SIZE
            - 8
        )
        center_y = (
            settings.MAP_RENDER_OFFSET_Y
            + settings.MAP_HEIGHT // 2 * settings.TILE_SIZE
            - 8
        )

        if side == "left":
            return settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE * 2, center_y
        if side == "right":
            return (
                settings.MAP_RENDER_OFFSET_X
                + settings.MAP_WIDTH * settings.TILE_SIZE
                - settings.TILE_SIZE * 2
                - 16,
                center_y,
            )
        if side == "top":
            return center_x, settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE * 2
        return (
            center_x,
            settings.MAP_RENDER_OFFSET_Y
            + settings.MAP_HEIGHT * settings.TILE_SIZE
            - settings.TILE_SIZE * 2
            - 16,
        )
