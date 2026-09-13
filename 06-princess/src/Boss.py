"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

This file contains the class Boss. It is immune to sword hits by default;
getting struck by an arrow (Room.update passes source="arrow") drops that
immunity for a few seconds, during which the sword can finally hurt it.
It never moves -- it just stands opposite the boss room's doorway and
periodically lobs a slow Fireball at wherever the player was standing.
"""

from typing import Callable, Dict, Any

from src.Entity import Entity
from src.Fireball import Fireball
from src.states.entity.EntityIdleState import EntityIdleState

_ATTACK_INTERVAL = 2.5
_VULNERABLE_DURATION = 4.0

_ANIMATION_DEFS: Dict[str, Dict[str, Any]] = {
    "idle-left": {"frames": [23]},
    "idle-right": {"frames": [35]},
    "idle-down": {"frames": [11]},
    "idle-up": {"frames": [47]},
}


class Boss(Entity):
    def __init__(self, x: float, y: float, on_defeated: Callable[[], None]) -> None:
        super().__init__(
            x=x,
            y=y,
            width=16,
            height=16,
            walk_speed=0,
            health=20,
            animation_defs=_ANIMATION_DEFS,
            states={},
        )
        self.direction = "down"
        self.on_defeated = on_defeated

        self.sword_immune = True
        self.vulnerable_timer = 0.0
        self.attack_timer = 0.0
        self._defeated_notified = False

        self.state_machine.states = {
            "idle": lambda sm: EntityIdleState(self, sm),
        }
        self.change_state("idle")

    def damage(self, dmg: int, source: str = "melee") -> None:
        if source == "sword" and self.sword_immune:
            # Immune to the sword until an arrow lands.
            return

        super().damage(dmg)

        if source == "arrow":
            self.sword_immune = False
            self.vulnerable_timer = 0.0

        if self.health <= 0 and not self._defeated_notified:
            self._defeated_notified = True
            self.on_defeated()

    def update(self, dt: float) -> None:
        super().update(dt)

        if not self.sword_immune:
            self.vulnerable_timer += dt

            if self.vulnerable_timer >= _VULNERABLE_DURATION:
                self.sword_immune = True
                self.vulnerable_timer = 0.0

    def process_ai(self, room, dt: float) -> None:
        self.attack_timer += dt

        if self.attack_timer >= _ATTACK_INTERVAL:
            self.attack_timer = 0.0
            target_x = room.player.x + room.player.width / 2
            target_y = room.player.y + room.player.height / 2
            room.projectiles.append(
                Fireball(
                    self.x + self.width / 2, self.y + self.height / 2, target_x, target_y
                )
            )
