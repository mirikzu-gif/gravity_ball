"""Генерирует дефолтные PNG-ассеты в assets/.

Запуск:
    python tools/generate_assets.py

Создаёт:
    assets/background.png — небо с градиентом, солнцем и редкими «звёздами»
    assets/ball.png — мяч-сфера с бликом
    assets/platform.png — деревянная платформа
    assets/obstacle.png — каменное препятствие

Все ассеты можно переопределить, положив свои PNG того же имени в assets/.
"""
import os
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Headless-режим для запуска без открытия окна.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from src.utils.config import HEIGHT, WIDTH  # noqa: E402


ASSETS_DIR = PROJECT_ROOT / "assets"
ASSETS_DIR.mkdir(exist_ok=True)


def _make_background() -> pygame.Surface:
    surf = pygame.Surface((WIDTH, HEIGHT))

    # Вертикальный градиент: глубокое небо вверху → светлая дымка внизу
    top = (95, 145, 210)
    bottom = (220, 230, 240)
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))

    # Солнечный диск с гало
    sun_pos = (850, 110)
    pygame.draw.circle(surf, (255, 240, 200), sun_pos, 70)
    pygame.draw.circle(surf, (255, 248, 220), sun_pos, 55)
    pygame.draw.circle(surf, (255, 255, 240), sun_pos, 35)

    # Редкие «снежинки» / звёзды для текстуры неба
    rng = random.Random(12345)
    for _ in range(30):
        x = rng.randint(0, WIDTH)
        y = rng.randint(0, HEIGHT // 3)
        radius = rng.randint(1, 2)
        c = rng.randint(220, 255)
        pygame.draw.circle(surf, (c, c, c), (x, y), radius)

    # Лёгкий горизонт-туман
    fog = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
    for y in range(80):
        a = int(60 * (1 - y / 80))
        pygame.draw.line(fog, (255, 255, 255, a), (0, y), (WIDTH, y))
    surf.blit(fog, (0, HEIGHT - 80))

    return surf


def _make_ball(radius: int = 20) -> pygame.Surface:
    diameter = radius * 2 + 2  # +2 чтобы влезла обводка
    surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    center = (diameter // 2, diameter // 2)

    # Тело (красный с лёгким градиентом)
    pygame.draw.circle(surf, (180, 30, 30), center, radius)
    pygame.draw.circle(surf, (255, 70, 70), center, radius - 2)

    # Блик (диагональ верхняя-левая)
    highlight_pos = (center[0] - radius // 3, center[1] - radius // 3)
    pygame.draw.circle(surf, (255, 200, 200), highlight_pos, radius // 3)
    pygame.draw.circle(surf, (255, 255, 255), highlight_pos, radius // 5)

    # Тонкая обводка
    pygame.draw.circle(surf, (40, 0, 0), center, radius, 2)

    return surf


def _make_platform(size=(128, 32)) -> pygame.Surface:
    surf = pygame.Surface(size, pygame.SRCALPHA)
    rect = surf.get_rect()

    # Base wood gradient.
    top = (156, 100, 52)
    bottom = (92, 58, 32)
    for y in range(rect.height):
        t = y / max(1, rect.height - 1)
        color = (
            int(top[0] + (bottom[0] - top[0]) * t),
            int(top[1] + (bottom[1] - top[1]) * t),
            int(top[2] + (bottom[2] - top[2]) * t),
        )
        pygame.draw.line(surf, color, (0, y), (rect.width, y))

    # Plank seams and light grain.
    seam = rect.width // 4
    for x in range(seam, rect.width, seam):
        pygame.draw.line(surf, (72, 42, 24), (x, 3), (x, rect.height - 4), 2)

    rng = random.Random(4242)
    for _ in range(18):
        y = rng.randint(5, rect.height - 6)
        x1 = rng.randint(0, rect.width // 2)
        x2 = min(rect.width, x1 + rng.randint(24, 70))
        color = rng.choice(((181, 124, 70), (69, 40, 22), (123, 76, 38)))
        pygame.draw.line(surf, color, (x1, y), (x2, y + rng.choice((-1, 0, 1))), 1)

    pygame.draw.rect(surf, (55, 34, 22), rect, 3)
    pygame.draw.line(surf, (210, 158, 92), (3, 3), (rect.width - 4, 3), 2)
    return surf


def _make_obstacle(size=(64, 64)) -> pygame.Surface:
    surf = pygame.Surface(size, pygame.SRCALPHA)
    rect = surf.get_rect()

    # Square stone block with shaded facets.
    top = (95, 108, 132)
    bottom = (45, 53, 75)
    for y in range(rect.height):
        t = y / max(1, rect.height - 1)
        color = (
            int(top[0] + (bottom[0] - top[0]) * t),
            int(top[1] + (bottom[1] - top[1]) * t),
            int(top[2] + (bottom[2] - top[2]) * t),
        )
        pygame.draw.line(surf, color, (0, y), (rect.width, y))

    pygame.draw.polygon(surf, (119, 132, 154), [(4, 4), (31, 4), (24, 29), (4, 36)])
    pygame.draw.polygon(surf, (68, 79, 105), [(31, 4), (60, 4), (60, 28), (24, 29)])
    pygame.draw.polygon(surf, (39, 47, 69), [(4, 36), (24, 29), (35, 60), (4, 60)])
    pygame.draw.polygon(surf, (82, 94, 119), [(24, 29), (60, 28), (60, 60), (35, 60)])

    # Cracks, chips, and hard square outline.
    pygame.draw.line(surf, (29, 35, 53), (23, 10), (29, 29), 2)
    pygame.draw.line(surf, (29, 35, 53), (29, 29), (20, 48), 2)
    pygame.draw.line(surf, (33, 40, 61), (43, 16), (50, 31), 2)
    pygame.draw.circle(surf, (35, 42, 62), (12, 14), 2)
    pygame.draw.circle(surf, (112, 126, 148), (51, 48), 2)
    pygame.draw.rect(surf, (22, 26, 40), rect, 3)

    return surf


def main() -> None:
    pygame.init()

    bg = _make_background()
    pygame.image.save(bg, str(ASSETS_DIR / "background.png"))
    print(f"saved {ASSETS_DIR / 'background.png'}")

    ball = _make_ball(radius=20)
    pygame.image.save(ball, str(ASSETS_DIR / "ball.png"))
    print(f"saved {ASSETS_DIR / 'ball.png'}")

    platform = _make_platform()
    pygame.image.save(platform, str(ASSETS_DIR / "platform.png"))
    print(f"saved {ASSETS_DIR / 'platform.png'}")

    obstacle = _make_obstacle()
    pygame.image.save(obstacle, str(ASSETS_DIR / "obstacle.png"))
    print(f"saved {ASSETS_DIR / 'obstacle.png'}")

    pygame.quit()


if __name__ == "__main__":
    main()
