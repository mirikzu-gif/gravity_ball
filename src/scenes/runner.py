"""Главный цикл приложения с фиксированным шагом физики и переключением сцен."""
import pygame

from ..utils.config import FIXED_DT, HEIGHT, MAX_FRAME_DT, WIDTH
from .base import Scene


def run_scenes(initial_scene: Scene, caption: str = "Упругий мяч") -> None:
    """Открывает окно и крутит сцены, начиная с `initial_scene`.

    Цикл:
      1. drain pygame events → scene.handle_event (QUIT завершает приложение);
      2. while accumulator >= FIXED_DT: scene.fixed_update(FIXED_DT);
      3. если scene.next_scene установлено — переключаемся;
      4. scene.render(screen) и pygame.display.flip().
    """
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(caption)
    clock = pygame.time.Clock()

    current = initial_scene
    accumulator = 0.0

    running = True
    while running:
        frame_dt = clock.tick(60) / 1000.0
        accumulator += min(frame_dt, MAX_FRAME_DT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            current.handle_event(event)
            if current.next_scene is not None:
                break

        if not running:
            break

        if current.next_scene is None:
            while accumulator >= FIXED_DT:
                current.fixed_update(FIXED_DT)
                accumulator -= FIXED_DT
                if current.next_scene is not None:
                    break

        if current.next_scene is not None:
            current = current.next_scene
            accumulator = 0.0

        current.render(screen)
        pygame.display.flip()

    pygame.quit()
