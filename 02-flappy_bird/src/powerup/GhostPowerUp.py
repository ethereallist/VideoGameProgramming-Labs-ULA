from typing import TYPE_CHECKING

from src.powerup import PowerUp
from typing import TypeVar, Any
if TYPE_CHECKING:
    from src.states.PlayingState import PlayingState
from pygame import mixer
import settings


class GhostPowerUp(PowerUp):

    def take(self, play_state: "PlayingState") -> None:
        play_state.bird.ghost_mode = True
        play_state.bird.ghost_mode_timer = 5.0
        mixer.music.stop()
        settings.SOUNDS["music"].stop()
        settings.SOUNDS["music"].play()