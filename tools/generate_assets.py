"""Генерирует дефолтные PNG-ассеты в assets/.

Запуск:
    python tools/generate_assets.py

Создаёт:
    assets/background.png — небо с градиентом, солнцем и редкими «звёздами»
    assets/ball.png — мяч-сфера с бликом

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


def main() -> None:
    pygame.init()

    bg = _make_background()
    pygame.image.save(bg, str(ASSETS_DIR / "background.png"))
    print(f"saved {ASSETS_DIR / 'background.png'}")

    ball = _make_ball(radius=20)
    pygame.image.save(ball, str(ASSETS_DIR / "ball.png"))
    print(f"saved {ASSETS_DIR / 'ball.png'}")

    pygame.quit()


if __name__ == "__main__":
    main()
