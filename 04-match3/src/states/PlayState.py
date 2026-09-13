"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

from typing import Dict, Any, List, Optional, Tuple

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params["level"]
        self.board = enter_params["board"]
        self.score = enter_params["score"]

        # The tile currently being dragged, or None when nothing is held.
        self.drag_tile = None
        self.drag_start_i = -1
        self.drag_start_j = -1
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.active = True

        self.timer = settings.LEVEL_TIME

        self.goal_score = self.level * 1.25 * 1000

        # A surface that supports alpha to highlight the slot a tile is
        # being dragged out of.
        self.tile_alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        pygame.draw.rect(
            self.tile_alpha_surface,
            (255, 255, 255, 96),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )

        # A surface that supports alpha to draw behind the text.
        self.text_alpha_surface = pygame.Surface((212, 136), pygame.SRCALPHA)
        pygame.draw.rect(
            self.text_alpha_surface, (56, 56, 56, 234), pygame.Rect(0, 0, 212, 136)
        )

        def decrement_timer():
            self.timer -= 1

            # Play warning sound on timer if we get low
            if self.timer <= 5:
                settings.SOUNDS["clock"].play()

        Timer.every(1, decrement_timer)

        # Guarantee the level never starts on a dead board.
        self._ensure_valid_moves()

    def update(self, _: float) -> None:
        if self.timer <= 0:
            Timer.clear()
            settings.SOUNDS["game-over"].play()
            self.state_machine.change("game-over", score=self.score)

        if self.score >= self.goal_score:
            Timer.clear()
            settings.SOUNDS["next-level"].play()
            self.state_machine.change("begin", level=self.level + 1, score=self.score)

        if self.drag_tile is not None:
            local_x, local_y = self._to_virtual(*pygame.mouse.get_pos())
            self.drag_tile.x = local_x - self.board.x - self.drag_offset_x
            self.drag_tile.y = local_y - self.board.y - self.drag_offset_y

    def render(self, surface: pygame.Surface) -> None:
        self.board.render(surface)

        if self.drag_tile is not None:
            x = self.drag_start_j * settings.TILE_SIZE + self.board.x
            y = self.drag_start_i * settings.TILE_SIZE + self.board.y
            surface.blit(self.tile_alpha_surface, (x, y))
            # Rendered again on top so it draws over every other tile while dragged.
            self.drag_tile.render(surface, self.board.x, self.board.y)

        surface.blit(self.text_alpha_surface, (16, 16))
        render_text(
            surface,
            f"Level: {self.level}",
            settings.FONTS["medium"],
            30,
            24,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["medium"],
            30,
            52,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Goal: {self.goal_score}",
            settings.FONTS["medium"],
            30,
            80,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Timer: {self.timer}",
            settings.FONTS["medium"],
            30,
            108,
            (99, 155, 255),
            shadowed=True,
        )

    def _to_virtual(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        x = screen_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
        y = screen_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
        return x, y

    def _cell_at(self, screen_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        pos_x, pos_y = self._to_virtual(*screen_pos)
        i = (pos_y - self.board.y) // settings.TILE_SIZE
        j = (pos_x - self.board.x) // settings.TILE_SIZE

        if 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH:
            return i, j

        return None

    def _ensure_valid_moves(self) -> None:
        while not self.board.has_valid_moves():
            self.board.reshuffle()

    def _explode(self, tile) -> List:
        if tile.power_up == "bomb":
            return self.board.detonate_color(tile)
        return self.board.detonate_line(tile)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not self.active or input_id != "click":
            return

        if input_data.pressed:
            cell = self._cell_at(input_data.position)

            if cell is None:
                return

            i, j = cell
            tile = self.board.tiles[i][j]
            local_x, local_y = self._to_virtual(*input_data.position)
            self.drag_tile = tile
            self.drag_start_i = i
            self.drag_start_j = j
            self.drag_offset_x = local_x - self.board.x - tile.x
            self.drag_offset_y = local_y - self.board.y - tile.y

        elif input_data.released and self.drag_tile is not None:
            tile1 = self.drag_tile
            self.drag_tile = None

            cell = self._cell_at(input_data.position)
            # Dropped back on the same cell it was picked up from: either
            # detonate it (if it's a power-up) or it's just a no-op click.
            if cell == (self.drag_start_i, self.drag_start_j):
                if tile1.power_up is not None:
                    self._detonate(tile1)
                return

            valid_target = False
            attempted_move = False

            if cell is not None:
                i2, j2 = cell
                di = i2 - self.drag_start_i
                dj = j2 - self.drag_start_j

                if abs(di) + abs(dj) == 1:
                    attempted_move = True
                    tile2 = self.board.tiles[i2][j2]
                    valid_target = self.board.would_match(tile1, tile2)

            if valid_target:
                self.active = False
                self.board.swap_tiles(tile1, tile2)

                # tileN.i/.j were just updated by swap_tiles, so this reads
                # each tile's *new* grid slot to tween its pixel position to.
                target1 = (tile1.j * settings.TILE_SIZE, tile1.i * settings.TILE_SIZE)
                target2 = (tile2.j * settings.TILE_SIZE, tile2.i * settings.TILE_SIZE)

                def arrive():
                    # tile1 is the tile the player actually dragged (moved) to
                    # its new slot, used to place any 4-match power-up there.
                    self._calculate_matches([tile1, tile2], moved_tile=tile1)

                Timer.tween(
                    0.25,
                    [
                        (tile1, {"x": target1[0], "y": target1[1]}),
                        (tile2, {"x": target2[0], "y": target2[1]}),
                    ],
                    on_finish=arrive,
                )
            else:
                if attempted_move:
                    settings.SOUNDS["error"].play()

                target_x = self.drag_start_j * settings.TILE_SIZE
                target_y = self.drag_start_i * settings.TILE_SIZE
                Timer.tween(0.15, [(tile1, {"x": target_x, "y": target_y})])

    def _detonate(self, tile) -> None:
        self.active = False
        settings.SOUNDS["match"].stop()
        settings.SOUNDS["match"].play()

        exploded = self._explode(tile)
        self.score += len(exploded) * 50

        falling_tiles = self.board.get_falling_tiles()

        Timer.tween(
            0.25,
            falling_tiles,
            on_finish=lambda: self._calculate_matches(
                [item[0] for item in falling_tiles]
            ),
        )

    def _calculate_matches(self, tiles: List, moved_tile=None) -> None:
        matches = self.board.calculate_matches_for(tiles)

        if matches is None:
            self._ensure_valid_moves()
            self.active = True
            return

        settings.SOUNDS["match"].stop()
        settings.SOUNDS["match"].play()

        for match in matches:
            self.score += len(match) * 50

        for match in matches:
            for tile in list(match):
                if tile.power_up is not None:
                    exploded = self._explode(tile)
                    self.score += len(exploded) * 50

        # A brand-new 4-tile match spawns a line-clear power-up at the tile
        # that was actually dragged there (or the first tile of the match
        # for cascades, where nothing was "moved" by the player).
        for match in matches:
            if len(match) >= 5:
                survivor = moved_tile if moved_tile in match else match[0]
                survivor.power_up = "bomb"
                match.remove(survivor)
            elif len(match) == 4:
                survivor = moved_tile if moved_tile in match else match[0]
                survivor.power_up = "line"
                match.remove(survivor)

        self.board.remove_matches()

        falling_tiles = self.board.get_falling_tiles()

        Timer.tween(
            0.25,
            falling_tiles,
            on_finish=lambda: self._calculate_matches(
                [item[0] for item in falling_tiles]
            ),
        )