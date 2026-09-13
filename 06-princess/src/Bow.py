"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

This file contains the class Bow. It fires arrows using the Factory Method
pattern: fire() is the factory method, building and returning a brand new
Projectile (the product) every time it's called, without the caller (the
player states) needing to know how an arrow is put together.
"""

from typing import Any

import pygame

import settings
from src.Projectile import Projectile


class _Arrow:
    """The flying visual for an arrow; the object a Projectile wraps."""

    def __init__(self, x: float, y: float, width: float, height: float) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def render(
        self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0
    ) -> None:
        surface.blit(
            settings.TEXTURES["bow"],
            (self.x + offset_x, self.y + offset_y),
            settings.frame("bow", 1),
        )


class Bow:
    def fire(self, player: Any) -> Projectile:
        """
        Factory method: builds a new arrow Projectile fired from the
        player's position, aimed in the direction they're currently facing.
        """
        direction = player.direction

        if direction in ("left", "right"):
            width, height = 8, 4
            y = player.y + player.height / 2 - height / 2
            x = player.x - width if direction == "left" else player.x + player.width
        else:
            width, height = 4, 8
            x = player.x + player.width / 2 - width / 2
            y = player.y - height if direction == "up" else player.y + player.height

        arrow = _Arrow(x, y, width, height)
        return Projectile(arrow, direction)
