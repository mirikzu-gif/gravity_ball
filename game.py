"""Основной файл игры — точка входа.

Game-loop по схеме Glenn Fiedler "Fix Your Timestep!":
  - физика идёт фиксированным шагом FIXED_DT (60 Гц);
  - frame_dt накапливается в accumulator, выполняется N полных шагов;
  - рендер интерполирует позицию мяча между prev и curr состоянием.
"""
import pygame
import pymunk
import pymunk.pygame_util

from src.entities.ball import Ball
from src.game.input_handler import InputAction, InputHandler
from src.game.jump_controller import JumpController
from src.game.movement import apply_movement_force
from src.utils.config import (
    DAMPING,
    FIXED_DT,
    GRAVITY,
    GRAY,
    HEIGHT,
    JUMP_FORCE,
    MAX_CHARGE_TIME,
    MAX_FRAME_DT,
    MOVE_FORCE,
    WHITE,
    WIDTH,
)
from src.utils.level import create_level
from src.utils.physics import is_on_ground


# JUMP_FORCE в config.py исторически выражен как «сила за один кадр 60 fps».
# Чтобы сохранить ощущения управления, переводим её в импульс: F * FIXED_DT.
JUMP_IMPULSE = JUMP_FORCE * FIXED_DT


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Упругий мяч")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    info_text = font.render(
        "Управляй мячом стрелками! Зажми пробел для зарядки прыжка",
        True,
        (0, 0, 0),
    )

    space = pymunk.Space()
    space.gravity = GRAVITY
    space.damping = DAMPING

    ball = Ball(100, 100, space=space)
    obstacles, platforms, goal = create_level(space)

    input_handler = InputHandler()
    jump_controller = JumpController(MAX_CHARGE_TIME, JUMP_IMPULSE)

    big_font = pygame.font.Font(None, 72)
    win_text = big_font.render("Уровень пройден!", True, (0, 120, 0))
    win_hint = font.render(
        "Закрой окно или нажми Esc для выхода", True, (0, 0, 0)
    )

    accumulator = 0.0
    prev_ball_pos = ball.body.position
    level_complete = False

    running = True
    while running:
        frame_dt = clock.tick(60) / 1000.0
        accumulator += min(frame_dt, MAX_FRAME_DT)

        # --- ввод (раз за кадр, без привязки к физическому шагу) -----------
        on_ground = is_on_ground(ball, space)
        for event in pygame.event.get():
            action = input_handler.process_event(event)
            if action is InputAction.QUIT:
                running = False
            elif level_complete:
                # после прохождения — только Esc/Q или закрытие окна
                if event.type == pygame.KEYDOWN and event.key in (
                    pygame.K_ESCAPE,
                    pygame.K_q,
                ):
                    running = False
            elif action is InputAction.JUMP_PRESS:
                jump_controller.press(on_ground=on_ground)
            elif action is InputAction.JUMP_RELEASE:
                jump_event = jump_controller.release(on_ground=on_ground)
                if jump_event is not None:
                    ball.apply_impulse(jump_event.impulse)

        # --- физика и обновление: только пока уровень не пройден -----------
        if not level_complete:
            while accumulator >= FIXED_DT:
                prev_ball_pos = pymunk.Vec2d(*ball.body.position)
                on_ground_step = is_on_ground(ball, space)

                apply_movement_force(
                    ball,
                    input_handler.get_movement(),
                    on_ground_step,
                    MOVE_FORCE,
                )
                jump_controller.update(FIXED_DT, on_ground=on_ground_step)

                space.step(FIXED_DT)
                accumulator -= FIXED_DT

                if goal.is_touched_by(ball):
                    level_complete = True
                    accumulator = 0.0
                    break
        else:
            accumulator = 0.0

        # --- рендер с интерполяцией ----------------------------------------
        alpha = accumulator / FIXED_DT
        curr_pos = ball.body.position
        ball_render_pos = prev_ball_pos * (1.0 - alpha) + curr_pos * alpha

        screen.fill(WHITE)
        for platform in platforms:
            platform.draw(screen)
        for obstacle in obstacles:
            obstacle.draw(screen)
        goal.draw(screen)
        ball.draw(screen, position=ball_render_pos)

        if (
            not level_complete
            and jump_controller.is_charging
            and is_on_ground(ball, space)
        ):
            _draw_charge_bar(
                screen,
                ball_render_pos,
                ball.radius,
                jump_controller.charge_ratio,
            )

        screen.blit(info_text, (10, 10))

        if level_complete:
            text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            hint_rect = win_hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            screen.blit(win_text, text_rect)
            screen.blit(win_hint, hint_rect)

        pygame.display.flip()

    pygame.quit()


def _draw_charge_bar(screen, position, radius, charge_ratio):
    bar_width = 60
    bar_height = 8
    bar_x = int(position[0] - bar_width // 2)
    bar_y = int(position[1] + radius + 10)

    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
    fill_width = int(bar_width * charge_ratio)
    color = (255, int(255 - charge_ratio * 200), 50)
    pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))
    pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 2)


if __name__ == "__main__":
    main()
