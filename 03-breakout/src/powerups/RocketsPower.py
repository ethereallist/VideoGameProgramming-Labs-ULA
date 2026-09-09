"""
ISPPV1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the base class PowerUp as an abstract class.
"""

from typing import TypeVar, Any

import pygame

import settings

from src.powerups.PowerUp import PowerUp

class RocketsPower(PowerUp):
    """
    The rockets power-up that allows the player to shoot rockets.
    """

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 7)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        play_state.rocket_active = True
        play_state.cannons_active = True
        self.active = False

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["rocket_icon"], self.get_collision_rect())
