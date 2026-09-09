"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class PauseState.
"""

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.World import World


class PauseState(BaseState):
    def enter(self) -> None:
        self.world = World()
        pygame.mixer.music.stop()

    def update(self, dt: float) -> None:
        self.world.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        render_text(
            surface,
            "PAUSE",
            settings.FONTS["flappy"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 3,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )
        render_text(
            surface,
            "Press Space to resume",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH / 2,
            2 * settings.VIRTUAL_HEIGHT / 3,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "space" and input_data.pressed:
            self.state_machine.change("playing", world=self.world)

    def on_exit(self) -> None:
        pygame.mixer.music.play(loops=-1)
