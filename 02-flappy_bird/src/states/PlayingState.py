"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class PlayingState.
"""

from typing import Optional

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.Bird import Bird
from src.World import World
from src.strategies import NormalCollision, NormalMovement, NormalObstacle, HardObstacle, HardMovement, HardCollision

class PlayingState(BaseState):
    def enter(self, world: Optional[World] = None, hard_mode: bool = False) -> None:
        self.world = world if world is not None else World()
        self.world.reset(True)
        self.bird = Bird(
            settings.VIRTUAL_WIDTH / 2 - settings.BIRD_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2 - settings.BIRD_HEIGHT / 2,
            settings.BIRD_WIDTH,
            settings.BIRD_HEIGHT,
        )
        self.score = 0
        self.hard_mode = hard_mode

        if self.hard_mode:
            self.movement_strategy = HardMovement()
            self.obstacle_strategy = HardObstacle()
            self.collision_strategy = HardCollision()
        else:
            self.collision_strategy = NormalCollision()
            self.movement_strategy = NormalMovement()
            self.obstacle_strategy = NormalObstacle()


    def update(self, dt: float) -> None:
        self.bird.update(dt)
        self.world.update(dt)
        self.obstacle_strategy.generate_obstacle(self.world, dt)

        for logPair in self.world.logs:
            if logPair.collides(self.bird.get_rect()):
                self.collision_strategy.on_collision(self.bird, logPair, self)

        for power_up in self.world.powerups:
            if power_up.collides(self.bird.get_rect()):
                power_up.take(self)
                self.world.powerups.remove(power_up)
                break

        if self.world.update_scored(self.bird.get_rect()):
            self.score += 1
            settings.SOUNDS["score"].play()

        self.movement_strategy.move(self.bird, dt)

        self.bird.ghost_mode_timer -= dt

        if self.bird.ghost_mode_timer <= 0 and self.bird.ghost_mode:
            self.bird.ghost_mode = False
            settings.SOUNDS["music"].stop()
            pygame.mixer.music.play(loops=-1)

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        self.bird.render(surface)
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["flappy"],
            20,
            10,
            settings.COLOR_WHITE,
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "jump" and input_data.pressed:
            self.movement_strategy.direction(input_id, self.bird)

        if input_id == "space" and input_data.pressed:
            self.state_machine.change("pause")

        if input_id == "right_arrow" and input_data.pressed:
            self.movement_strategy.direction(input_id, self.bird)

        if input_id == "right_arrow" and input_data.released:
            self.movement_strategy.is_right = False

        if input_id == "left_arrow" and input_data.pressed:
            self.movement_strategy.direction(input_id, self.bird)

        if input_id == "left_arrow" and input_data.released:
            self.movement_strategy.is_left = False
