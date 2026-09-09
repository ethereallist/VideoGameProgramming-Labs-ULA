import pygame
import settings


class Rockets:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.width = 4
        self.height = 10
        self.vy = -300
        self.active = True

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def update(self, dt: float) -> None:
        self.y += self.vy * dt
        if self.y < 0:
            self.active = False

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["rocket"], self.get_collision_rect())
