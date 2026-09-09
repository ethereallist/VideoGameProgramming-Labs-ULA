
from typing import TypeVar, Any

import pygame

import settings

from src.LogPair import LogPair


class PowerUp:
    """
    The base power-up.
    """

    def __init__(self, x: int, y: int, log_pair: LogPair) -> None:
        self.x = x
        self.y = y
        self.active = True
        self.rect_ref = log_pair

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, 16, 16)

    def collides(self, obj: Any) -> bool:
        return self.get_collision_rect().colliderect(obj)

    def update(self, dt: float) -> None:
        top_ref = self.rect_ref.get_top_rect()
        self.x = top_ref.centerx
        self.y = top_ref.bottom + settings.LOGS_GAP / 2

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["powerup"], self.get_collision_rect())

    def take(self, play_state: TypeVar("playing")) -> None:
        raise NotImplementedError
