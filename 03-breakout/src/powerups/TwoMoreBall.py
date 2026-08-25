"""
ISPPV1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the specialization of PowerUp to add two more ball to the game.
"""

import random
from typing import TypeVar

from gale.factory import Factory

import settings
from src.Ball import Ball
from src.powerups.PowerUp import PowerUp


class TwoMoreBall(PowerUp):
    """
    Power-up to add two more ball to the game.
    """

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 8)
        self.ball_factory = Factory(Ball)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        paddle = play_state.paddle

        if play_state.balls:
            reference_ball = play_state.balls[0]

            ball1 = self.ball_factory.create(reference_ball.x, reference_ball.y)
            ball1.vx = random.randint(-80, 80)
            ball1.vy = random.randint(-170, -100)
            ball1.is_stuck = False

            ball2 = self.ball_factory.create(reference_ball.x, reference_ball.y)
            ball2.vx = random.randint(-80, 80)
            ball2.vy = random.randint(-170, -100)
            ball2.is_stuck = False  # <--- Nos aseguramos NO nazca pegada

            play_state.balls.extend([ball1, ball2])


        self.active = False
