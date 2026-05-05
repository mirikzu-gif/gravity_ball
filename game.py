"""Основной файл игры — точка входа."""
import pygame
import pymunk
import pymunk.pygame_util

from src.entities.ball import Ball
from src.game.input_handler import InputAction, InputHandler
from src.game.jump_controller import JumpController
from src.utils.config import (
    DAMPING,
    GRAVITY,
    GRAY,
    HEIGHT,
    JUMP_FORCE,
    MAX_CHARGE_TIME,
    MOVE_FORCE,
    WHITE,
    WIDTH,
)
from src.utils.level import create_level
from src.utils.physics import is_on_ground


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
    obstacles, platforms = create_level(space)

    input_handler = InputHandler()
    jump_controller = JumpController(MAX_CHARGE_TIME, JUMP_FORCE)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        on_ground = is_on_ground(ball, space)

        for event in pygame.event.get():
            action = input_handler.process_event(event)
            if action is InputAction.QUIT:
                running = False
            elif action is InputAction.JUMP_PRESS:
                jump_controller.press(on_ground=on_ground)
            elif action is InputAction.JUMP_RELEASE:
                jump_event = jump_controller.release(on_ground=on_ground)
                if jump_event is not None:
                    ball.apply_force(jump_event.force)

        dx, dy = input_handler.get_movement()
        if dx or dy:
            ball.apply_force((dx * MOVE_FORCE, dy * MOVE_FORCE))

        jump_controller.update(dt, on_ground=on_ground)

        space.step(dt)

        screen.fill(WHITE)
        for platform in platforms:
            platform.draw(screen)
        for obstacle in obstacles:
            obstacle.draw(screen)
        ball.draw(screen)

        if jump_controller.is_charging and on_ground:
            _draw_charge_bar(screen, ball, jump_controller.charge_ratio)

        screen.blit(info_text, (10, 10))
        pygame.display.flip()

    pygame.quit()


def _draw_charge_bar(screen, ball, charge_ratio):
    bar_width = 60
    bar_height = 8
    bar_x = int(ball.body.position.x - bar_width // 2)
    bar_y = int(ball.body.position.y + ball.radius + 10)

    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
    fill_width = int(bar_width * charge_ratio)
    color = (255, int(255 - charge_ratio * 200), 50)
    pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))
    pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 2)


if __name__ == "__main__":
    main()
