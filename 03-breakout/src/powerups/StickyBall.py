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


class StickyBall(PowerUp):
    """
    The sticky ball power-up.
    """

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 7)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        play_state.sticky_ball_active = True
        self.active = False
        play_state.sticky_timer = 10.0
