"""

Author: Rosa Rosales
rosamilib@gmail.com

This file contains the class BaseStrategy
"""

import settings

import pygame

class CollisionStrategy:

    def on_collision(self, bird, obstacle, state) -> None:
        raise NotImplementedError

class HardCollision(CollisionStrategy):

    def on_collision(self, bird, obstacle, state) -> None:
        if obstacle.is_special:
            settings.SOUNDS["explosion"].play()
            settings.SOUNDS["ouch"].play()
            state.state_machine.change("count_down", hard_mode=True)
        elif bird.ghost_mode:
            return
        else:
            settings.SOUNDS["hurt"].play()
            state.state_machine.change("count_down", hard_mode=True)

class NormalCollision(CollisionStrategy):

    def on_collision(self, bird, obstacle, state) -> None:
        settings.SOUNDS["hurt"].play()
        state.state_machine.change("count_down", hard_mode=False)

