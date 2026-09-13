"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

This file contains the class Fireball: the Boss's slow projectile. It is
aimed once, at creation time, toward the point the player occupied at that
moment -- it does not home in on the player afterward -- and travels in a
straight line until it leaves the room.
"""

import math

import pygame

import settings

_SPEED = 35


class Fireball:
    def __init__(self, x: float, y: float, target_x: float, target_y: float) -> None:
        self.width = 8
        self.height = 8
        self.x = x - self.width / 2
        self.y = y - self.height / 2
        self.dead = False

        # Only Fireballs deal damage to the player; arrows never do (see
        # Room.update, which checks this flag before resolving a hit).
        self.damages_player = True

        dx = target_x - x
        dy = target_y - y
        distance = math.hypot(dx, dy) or 1
        self.vx = dx / distance * _SPEED
        self.vy = dy / distance * _SPEED

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def update(self, dt: float) -> None:
        if self.dead:
            return

        self.x += self.vx * dt
        self.y += self.vy * dt

        room_left = settings.MAP_RENDER_OFFSET_X
        room_top = settings.MAP_RENDER_OFFSET_Y
        room_right = settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH * settings.TILE_SIZE
        room_bottom = settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT * settings.TILE_SIZE

        if (
            self.x < room_left
            or self.x + self.width > room_right
            or self.y < room_top
            or self.y + self.height > room_bottom
        ):
            self.dead = True

    def render(
        self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0
    ) -> None:
        surface.blit(
            settings.TEXTURES["fireball"],
            (self.x + offset_x, self.y + offset_y),
            settings.frame("fireball", 1),
        )

    def collides(self, target) -> bool:
        return self.get_collision_rect().colliderect(target.get_collision_rect())
