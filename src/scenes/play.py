"""GameScene — основной геймплей."""
import pygame
import pymunk

from ..entities.ball import Ball
from ..game.input_handler import InputAction, InputHandler
from ..game.jump_controller import JumpController
from ..game.movement import apply_movement_force
from ..utils import assets, audio, best_times, fonts
from .clouds import generate_clouds
from ..utils.config import (
    DAMPING,
    FIXED_DT,
    GRAVITY,
    GRAY,
    HEIGHT,
    JUMP_FORCE,
    MAX_CHARGE_TIME,
    MOVE_FORCE,
    WIDTH,
)
from ..utils.level import LEVELS, build_level
from ..utils.physics import is_on_ground
from ..rendering.world_renderer import WorldRenderer
from .base import Scene


# JUMP_FORCE в config.py выражен как «сила за один кадр 60 fps».
# Чтобы сохранить ощущения управления, переводим её в импульс: F * FIXED_DT.
JUMP_IMPULSE = JUMP_FORCE * FIXED_DT


def _format_time(secs: float) -> str:
    minutes, seconds = divmod(secs, 60)
    return f"{int(minutes):02d}:{seconds:05.2f}"


_BOUNCE_IMPULSE_THRESHOLD = 250.0


def _on_collision_post_solve(arbiter, space, data):
    """Pymunk-callback: проигрывает звук при сильном ударе.

    arbiter.total_impulse — суммарный импульс контакта за этот шаг.
    Лежание мяча на платформе тоже даёт импульс (из-за гравитации), но
    значительно ниже; порог отсекает такие фоновые контакты.
    """
    if arbiter.total_impulse.length > _BOUNCE_IMPULSE_THRESHOLD:
        audio.play_bounce()


def _build_background(sprites=None):
    """Возвращает Surface для фона.

    Если есть assets/background.png — масштабируется к размеру окна и используется;
    иначе fallback на простой вертикальный градиент.
    """
    if sprites is None:
        sprites = assets.get_sprite_manager()

    sprite = sprites.get_scaled("background", (WIDTH, HEIGHT))
    if sprite is not None:
        return sprite

    surface = pygame.Surface((WIDTH, HEIGHT))
    top = (200, 222, 245)
    bottom = (245, 245, 250)
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
    return surface


class GameScene(Scene):
    """Игровая сцена: физика, ввод, цель уровня."""

    def __init__(
        self, level_index: int = 0, total_elapsed: float = 0.0
    ) -> None:
        super().__init__()
        if not 0 <= level_index < len(LEVELS):
            raise ValueError(
                f"level_index {level_index} вне диапазона [0, {len(LEVELS)})"
            )
        self.level_index = level_index
        self.level_def = LEVELS[level_index]
        audio.play_background()
        # Время с прошлых уровней + текущее на этом уровне.
        self._total_elapsed_before = total_elapsed
        self._elapsed = 0.0

        self._space = pymunk.Space()
        self._space.gravity = GRAVITY
        self._space.damping = DAMPING
        # Звук отскока: pymunk вызовет post_solve с суммарным импульсом контакта,
        # порог отсекает «лежание» мяча на полу и слабые касания.
        self._space.on_collision(post_solve=_on_collision_post_solve)

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

        self._sprites = assets.get_sprite_manager()
        self._world_renderer = WorldRenderer(self._sprites)
        self._background = _build_background(self._sprites)
        self._clouds = generate_clouds()
        self._info_font = fonts.hud(18)
        self._info_text = self._info_font.render(
            "Стрелки/пробел — играть    R — рестарт    P — пауза",
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
        # Пауза перехватывается до InputHandler, чтобы P/Esc не уходили в JumpController.
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_p,
            pygame.K_ESCAPE,
        ):
            from .pause import PauseScene

            self.next_scene = PauseScene(self)
            return

        # R — рестарт текущего уровня. Время прошлых уровней сохраняется,
        # таймер текущего уровня обнуляется.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.next_scene = GameScene(
                self.level_index, total_elapsed=self._total_elapsed_before
            )
            return

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
                audio.play_jump()

    def fixed_update(self, dt: float) -> None:
        # фиксируем позицию ДО шага — для интерполяции в render
        self._prev_ball_pos = pymunk.Vec2d(*self._ball.body.position)
        self._elapsed += dt

        for cloud in self._clouds:
            cloud.update(dt)

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

        screen.blit(self._background, (0, 0))

        # Облака рисуются между фоном и игровым миром.
        for cloud in self._clouds:
            cloud.draw(screen, (255, 255, 255))

        self._world_renderer.draw(
            screen,
            self._platforms,
            self._obstacles,
            self._goal,
            self._ball,
            ball_render_pos,
        )

        if self._jump.is_charging and is_on_ground(self._ball, self._space):
            self._draw_charge_bar(screen, ball_render_pos)

        screen.blit(self._info_text, (10, 10))
        rect = self._level_label.get_rect(topright=(WIDTH - 10, 10))
        screen.blit(self._level_label, rect)

        timer_surf = self._info_font.render(
            _format_time(self._total_elapsed_before + self._elapsed),
            True,
            (0, 0, 0),
        )
        timer_rect = timer_surf.get_rect(topright=(WIDTH - 10, 50))
        screen.blit(timer_surf, timer_rect)

    # ------------------------------------------------------------------
    # Внутреннее
    # ------------------------------------------------------------------
    def _on_goal_reached(self) -> None:
        audio.play_goal()
        best_times.record_level(self.level_def.name, self._elapsed)
        total = self._total_elapsed_before + self._elapsed
        next_index = self.level_index + 1
        if next_index >= len(LEVELS):
            from .win import WinScene

            self.next_scene = WinScene(total_time=total)
        else:
            self.next_scene = GameScene(next_index, total_elapsed=total)

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
