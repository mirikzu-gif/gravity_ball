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
)
from ..utils.level import create_level
from ..utils.physics import is_on_ground
from .base import Scene


# JUMP_FORCE в config.py выражен как «сила за один кадр 60 fps».
# Чтобы сохранить ощущения управления, переводим её в импульс: F * FIXED_DT.
JUMP_IMPULSE = JUMP_FORCE * FIXED_DT


class GameScene(Scene):
    """Игровая сцена: физика, ввод, цель уровня."""

    def __init__(self) -> None:
        super().__init__()

        self._space = pymunk.Space()
        self._space.gravity = GRAVITY
        self._space.damping = DAMPING

        self._ball = Ball(100, 100, space=self._space)
        self._obstacles, self._platforms, self._goal = create_level(self._space)

        self._input = InputHandler()
        self._jump = JumpController(MAX_CHARGE_TIME, JUMP_IMPULSE)

        self._prev_ball_pos = self._ball.body.position
        self._step_alpha = 0.0  # доля FIXED_DT, не «съеденная» в рендере

        self._info_font = pygame.font.Font(None, 36)
        self._info_text = self._info_font.render(
            "Стрелки — движение, пробел — прыжок (зажми, чтобы зарядить)",
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
            from .win import WinScene

            self.next_scene = WinScene()

    def render(self, screen: pygame.Surface) -> None:
        # Пока сцена не делает интерполяции по accumulator (рантаймом он не передаётся),
        # рисуем по фактической позиции — рывки незаметны при FIXED_DT=1/60.
        screen.fill(WHITE)

        for platform in self._platforms:
            platform.draw(screen)
        for obstacle in self._obstacles:
            obstacle.draw(screen)
        self._goal.draw(screen)
        self._ball.draw(screen)

        if self._jump.is_charging and is_on_ground(self._ball, self._space):
            self._draw_charge_bar(screen)

        screen.blit(self._info_text, (10, 10))

    # ------------------------------------------------------------------
    # Внутреннее
    # ------------------------------------------------------------------
    def _draw_charge_bar(self, screen: pygame.Surface) -> None:
        bar_width = 60
        bar_height = 8
        bar_x = int(self._ball.body.position.x - bar_width // 2)
        bar_y = int(self._ball.body.position.y + self._ball.radius + 10)
        ratio = self._jump.charge_ratio

        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * ratio)
        color = (255, int(255 - ratio * 200), 50)
        pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(
            screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 2
        )
