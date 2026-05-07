"""Главный цикл приложения с фиксированным шагом физики и переключением сцен."""
import pygame

from ..utils.config import FIXED_DT, HEIGHT, MAX_FRAME_DT, WIDTH
from .base import Scene


def _set_display(fullscreen: bool = False) -> pygame.Surface:
    """Creates the display surface.

    SCALED keeps the game at the logical WIDTH x HEIGHT resolution and lets
    pygame scale it to the actual window or desktop fullscreen size. Some
    headless/test drivers do not support SCALED, so we fall back to the plain
    mode instead of crashing on F11.
    """
    use_scaled = pygame.display.get_driver() != "dummy"
    flags = pygame.SCALED if use_scaled else 0
    if fullscreen:
        flags |= pygame.FULLSCREEN
    try:
        return pygame.display.set_mode((WIDTH, HEIGHT), flags)
    except pygame.error:
        fallback_flags = pygame.FULLSCREEN if fullscreen else 0
        return pygame.display.set_mode((WIDTH, HEIGHT), fallback_flags)


def run_scenes(initial_scene: Scene, caption: str = "Упругий мяч") -> None:
    """Открывает окно и крутит сцены, начиная с `initial_scene`.

    Цикл:
      1. drain pygame events → scene.handle_event (QUIT завершает приложение);
      2. while accumulator >= FIXED_DT: scene.fixed_update(FIXED_DT);
      3. если scene.next_scene установлено — переключаемся;
      4. scene.render(screen) и pygame.display.flip().
    """
    pygame.init()
    screen = _set_display(fullscreen=False)
    pygame.display.set_caption(caption)
    clock = pygame.time.Clock()

    current = initial_scene
    accumulator = 0.0
    fullscreen = False

    running = True
    while running:
        frame_dt = clock.tick(60) / 1000.0
        accumulator += min(frame_dt, MAX_FRAME_DT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            # F11 переключает полноэкранный режим — перехватывается до сцен.
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                fullscreen = not fullscreen
                screen = _set_display(fullscreen)
                continue
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
            # Сбрасываем next_scene на новой сцене — иначе при повторном использовании
            # того же экземпляра (например, GameScene → PauseScene → та же GameScene)
            # старое значение мгновенно вернёт нас обратно.
            current.next_scene = None
            accumulator = 0.0

        current.render(screen, alpha=accumulator / FIXED_DT)
        pygame.display.flip()

    pygame.quit()
