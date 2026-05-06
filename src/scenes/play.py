"""GameScene — основной геймплей."""
import pygame
import pymunk

from ..entities.ball import Ball
from ..game.input_handler import InputAction, InputHandler
from ..game.jump_controller import JumpController
from ..game.movement import apply_movement_force
from ..utils.config import (
    DAMPING,
    FIXED_DT,
    GRAVITY,
    GRAY,
    JUMP_FORCE,
    MAX_CHARGE_TIME,
    MOVE_FORCE,
    WHITE,
    WIDTH,
)
from ..utils.level import LEVELS, build_level
from ..utils.physics import is_on_ground
from .base import Scene


# JUMP_FORCE в config.py выражен как «сила за один кадр 60 fps».
# Чтобы сохранить ощущения управления, переводим её в импульс: F * FIXED_DT.
JUMP_IMPULSE = JUMP_FORCE * FIXED_DT


class GameScene(Scene):
    """Игровая сцена: физика, ввод, цель уровня."""

    def __init__(self, level_index: int = 0) -> None:
        super().__init__()
        if not 0 <= level_index < len(LEVELS):
            raise ValueError(
                f"level_index {level_index} вне диапазона [0, {len(LEVELS)})"
            )
        self.level_index = level_index
        self.level_def = LEVELS[level_index]

        self._space = pymunk.Space()
        self._space.gravity = GRAVITY
        self._space.damping = DAMPING

        self._ball = Ball(
            self.level_def.ball_start[0],
            self.level_def.ball_start[1],
            space=self._space,
        )
        self._obstacles, self._platforms, self._goal = build_level(
            self._space, self.level_def
        )

        self._input = InputHandler()
        self._jump = JumpController(MAX_CHARGE_TIME, JUMP_IMPULSE)

        # Для интерполяции рендера: позиция в начале последнего физ. шага.
        self._prev_ball_pos = pymunk.Vec2d(*self._ball.body.position)

        self._info_font = pygame.font.Font(None, 36)
        self._info_text = self._info_font.render(
            "Стрелки — движение, пробел — прыжок (зажми, чтобы зарядить)",
            True,
            (0, 0, 0),
        )
        self._level_label = self._info_font.render(
            f"Уровень {level_index + 1}/{len(LEVELS)} — {self.level_def.name}",
            True,
            (0, 0, 0),
        )

    # ------------------------------------------------------------------
    # Scene API
    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        on_ground = is_on_ground(self._ball, self._space)
        action = self._input.process_event(event)
        if action is InputAction.QUIT:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif action is InputAction.JUMP_PRESS:
            self._jump.press(on_ground=on_ground)
        elif action is InputAction.JUMP_RELEASE:
            jump_event = self._jump.release(on_ground=on_ground)
            if jump_event is not None:
                self._ball.apply_impulse(jump_event.impulse)

    def fixed_update(self, dt: float) -> None:
        # фиксируем позицию ДО шага — для интерполяции в render
        self._prev_ball_pos = pymunk.Vec2d(*self._ball.body.position)

        on_ground = is_on_ground(self._ball, self._space)

        apply_movement_force(
            self._ball,
            self._input.get_movement(),
            on_ground,
            MOVE_FORCE,
        )
        self._jump.update(dt, on_ground=on_ground)

        self._space.step(dt)

        if self._goal.is_touched_by(self._ball):
            self._on_goal_reached()

    def render(self, screen: pygame.Surface, alpha: float = 1.0) -> None:
        # Интерполяция позиции мяча между последним и текущим физическим шагом.
        curr_pos = self._ball.body.position
        ball_render_pos = (
            self._prev_ball_pos * (1.0 - alpha) + curr_pos * alpha
        )

        screen.fill(WHITE)

        for platform in self._platforms:
            platform.draw(screen)
        for obstacle in self._obstacles:
            obstacle.draw(screen)
        self._goal.draw(screen)
        self._ball.draw(screen, position=ball_render_pos)

        if self._jump.is_charging and is_on_ground(self._ball, self._space):
            self._draw_charge_bar(screen, ball_render_pos)

        screen.blit(self._info_text, (10, 10))
        rect = self._level_label.get_rect(topright=(WIDTH - 10, 10))
        screen.blit(self._level_label, rect)

    # ------------------------------------------------------------------
    # Внутреннее
    # ------------------------------------------------------------------
    def _on_goal_reached(self) -> None:
        next_index = self.level_index + 1
        if next_index >= len(LEVELS):
            from .win import WinScene

            self.next_scene = WinScene()
        else:
            self.next_scene = GameScene(next_index)

    def _draw_charge_bar(self, screen: pygame.Surface, position) -> None:
        bar_width = 60
        bar_height = 8
        bar_x = int(position[0] - bar_width // 2)
        bar_y = int(position[1] + self._ball.radius + 10)
        ratio = self._jump.charge_ratio

        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * ratio)
        color = (255, int(255 - ratio * 200), 50)
        pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(
            screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 2
        )
