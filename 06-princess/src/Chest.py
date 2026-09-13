"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

This file contains the class Chest: a one-time pickup that grants the
player a Bow the first time they interact with it while standing next to
it. Only one ever spawns across the whole dungeon (see Dungeon._create_room).
"""

from typing import Any

import pygame

import settings
from src.Bow import Bow


class Chest:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.opened = False

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def open(self, player: Any) -> None:
        if self.opened:
            return

        self.opened = True
        player.bow = Bow()
        settings.SOUNDS["door"].play()

    def render(
        self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0
    ) -> None:
        frame = 2 if self.opened else 1
        surface.blit(
            settings.TEXTURES["chest"],
            (self.x + offset_x, self.y + offset_y),
            settings.frame("chest", frame),
        )
