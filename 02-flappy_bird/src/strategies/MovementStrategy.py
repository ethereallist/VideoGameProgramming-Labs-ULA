import settings

class MovementStrategy:
    def __init__(self) -> None:
        self.is_right = False
        self.is_left = False
        self.is_jumping = False
    def move(self, bird, dt) -> None:
        raise NotImplementedError
    def direction(self, key, bird) -> None:
        raise NotImplementedError

class HardMovement(MovementStrategy):
    def move(self, bird, dt) -> None:
        if self.is_right:
            bird.x += settings.GRAVITY * dt
        elif self.is_left:
            bird.x -= settings.GRAVITY * dt

    def direction(self, key, bird) -> None:
        if key == "right_arrow":
            self.is_right = True
        elif key == "left_arrow":
            self.is_left = True
        elif key == "jump":
            self.is_jumping = True
            bird.jump()

class NormalMovement(MovementStrategy):
    def move(self, bird, dt) -> None:
        pass

    def direction(self, key, bird) -> None:
        if key == "jump":
            bird.jump()

