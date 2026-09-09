import settings
import random

class ObstacleStrategy:
    def generate_obstacle(self, world, dt) -> None:
        raise NotImplementedError

class NormalObstacle(ObstacleStrategy):
    def generate_obstacle(self, world, dt) -> None:
        if world.generate_logs:
            world.logs_spawn_timer += dt

            if world.logs_spawn_timer >= settings.TIME_TO_SPAWN_LOGS:
                world.logs_spawn_timer = 0.0
                y = max(-settings.LOG_HEIGHT + 10, min(world.last_log_y + random.randint(-20, 20), settings.VIRTUAL_HEIGHT + 90 - settings.LOG_HEIGHT))
                world.last_log_y = y
                world.logs.append(world.log_pair_factory.create(settings.VIRTUAL_WIDTH, y))

class HardObstacle(ObstacleStrategy):
    def generate_obstacle(self, world, dt) -> None:
        if world.generate_logs:
            world.logs_spawn_timer += dt

            if world.logs_spawn_timer >= world.time_to_spawn_logs_hard:
                world.time_to_spawn_logs_hard = random.uniform(0.8, 2.5)
                X = int(world.logs_spawn_timer * 20)
                world.logs_spawn_timer = 0.0
                y = max(-settings.LOG_HEIGHT + 10, min(world.last_log_y + random.randint(-X, X), settings.VIRTUAL_HEIGHT + 90 - settings.LOG_HEIGHT))
                world.last_log_y = y
                is_special = random.random() < 0.3
                new_log = world.log_pair_factory.create(settings.VIRTUAL_WIDTH, y, {"is_special": is_special})
                world.logs.append(new_log)
                prob_powerup = random.random() < 0.2
                if prob_powerup:
                    power_up = world.powerup_factory.create(settings.VIRTUAL_WIDTH, y,{"log_pair": new_log})
                    world.powerups.append(power_up)
