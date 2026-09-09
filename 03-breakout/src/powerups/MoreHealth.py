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

class MoreHealth(PowerUp):
    """
    A heart power-up that increases the player's lives.
    """

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 2)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        play_state.more_health_active = True
        if play_state.lives < 3:
            play_state.lives += 1
        self.active = False
        settings.SOUNDS["life"].play()

