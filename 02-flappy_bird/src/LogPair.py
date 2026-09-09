"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class LogPair: a top log
(rendered flipped upside down) and a bottom log, LOGS_GAP pixels
apart, that scroll left together and score once the bird passes them.
"""

import pygame

import settings

import math


class LogPair:
    def __init__(self, x: float, y: float, is_special: bool = False) -> None:
        self.x: float = x
        self.y: float = y
        self.scored: bool = False
        self.is_special = is_special
        self.log_gap = 0
        self.acc_time: float = 0.0
        self.time_to_spawn_logs_hard = 0.0

    def get_top_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y - self.log_gap / 2), settings.LOG_WIDTH, settings.LOG_HEIGHT)

    def get_bottom_rect(self) -> pygame.Rect:
        return pygame.Rect(
            round(self.x),
            round(self.y + self.log_gap / 2 + settings.LOG_HEIGHT),

            settings.LOG_WIDTH,
            settings.LOG_HEIGHT,
        )

    def collides(self, rect: pygame.Rect) -> bool:
        return self.get_top_rect().colliderect(rect) or self.get_bottom_rect().colliderect(rect)

    def update(self, dt: float) -> None:
        self.x += -settings.MAIN_SCROLL_SPEED * dt
        self.acc_time += dt
        if self.is_special:
            self.log_gap = 45 + 45 * math.cos(0.35 * self.acc_time)
        else:
            self.log_gap = settings.LOGS_GAP

    def is_out_of_game(self) -> bool:
        return self.x < -settings.LOG_WIDTH

    def update_scored(self, rect: pygame.Rect) -> bool:
        if self.scored:
            return False

        if rect.left > self.x + settings.LOG_WIDTH:
            self.scored = True
            return True

        return False

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["log_inverted"], self.get_top_rect())
        surface.blit(settings.TEXTURES["log"], self.get_bottom_rect())
