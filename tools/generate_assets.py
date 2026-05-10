"""Генерирует дефолтные PNG-ассеты в assets/.

Запуск:
    python tools/generate_assets.py
    python tools/generate_assets.py --only goal spring spike

Создаёт:
    assets/background.png — небо с градиентом, солнцем и редкими «звёздами»
    assets/ball.png — мяч-сфера с бликом
    assets/skins/*.png — PNG-скины мяча
    assets/platform.png — деревянная платформа
    assets/obstacle.png — каменное препятствие
    assets/goal.png — сияющий портал-цель
    assets/spring.png — металлическая пружина
    assets/spike.png — тайловая ячейка острого шипа

Все ассеты можно переопределить, положив свои PNG того же имени в assets/.
"""
import argparse
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
from tools.generate_skin_assets import FILENAMES, SKINS_DIR, make_skin_surface  # noqa: E402
from src.utils import skins  # noqa: E402


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


def _make_goal(size=(64, 96)) -> pygame.Surface:
    surf = pygame.Surface(size, pygame.SRCALPHA)
    rect = surf.get_rect()

    # Warm metal frame with a bright portal center.
    inner = rect.inflate(-14, -14)
    for y in range(rect.height):
        t = y / max(1, rect.height - 1)
        color = (
            int(255 + (194 - 255) * t),
            int(235 + (130 - 235) * t),
            int(82 + (24 - 82) * t),
            255,
        )
        pygame.draw.line(surf, color, (0, y), (rect.width, y))

    pygame.draw.rect(surf, (82, 55, 28), rect, 3, border_radius=10)
    pygame.draw.rect(surf, (255, 250, 176), rect.inflate(-8, -8), 2, border_radius=8)

    glow = pygame.Surface(inner.size, pygame.SRCALPHA)
    glow_rect = glow.get_rect()
    for y in range(glow_rect.height):
        t = y / max(1, glow_rect.height - 1)
        color = (
            int(72 + 35 * t),
            int(210 + 22 * t),
            int(255 - 35 * t),
            210,
        )
        pygame.draw.line(glow, color, (0, y), (glow_rect.width, y))
    pygame.draw.ellipse(glow, (235, 255, 255, 135), glow_rect.inflate(-8, -18))
    pygame.draw.ellipse(glow, (255, 255, 255, 70), glow_rect.inflate(-22, -42))
    surf.blit(glow, inner)

    # Checkpoint sparkle and a small central dot keep the target readable.
    cx, cy = rect.center
    pygame.draw.circle(surf, (255, 255, 255, 230), (cx, cy), 5)
    for dx, dy in ((0, -34), (18, -18), (-18, 20), (14, 32)):
        pygame.draw.line(surf, (255, 255, 220, 210), (cx + dx - 4, cy + dy), (cx + dx + 4, cy + dy), 2)
        pygame.draw.line(surf, (255, 255, 220, 210), (cx + dx, cy + dy - 4), (cx + dx, cy + dy + 4), 2)

    return surf


def _make_spring(size=(96, 32)) -> pygame.Surface:
    surf = pygame.Surface(size, pygame.SRCALPHA)
    rect = surf.get_rect()

    # Rubber/steel pads.
    pygame.draw.rect(surf, (31, 43, 52), rect, border_radius=6)
    pygame.draw.rect(surf, (94, 118, 130), rect.inflate(-4, -4), border_radius=5)
    pygame.draw.line(surf, (186, 220, 226), (8, 5), (rect.width - 9, 5), 2)
    pygame.draw.line(surf, (22, 30, 38), (8, rect.height - 6), (rect.width - 9, rect.height - 6), 3)

    # Cyan energy under the coil.
    glow = pygame.Surface((rect.width - 12, rect.height - 10), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (75, 230, 255, 95), glow.get_rect())
    surf.blit(glow, (6, 5))

    left = 10
    right = rect.width - 10
    mid_y = rect.centery
    amp = max(5, rect.height // 3)
    points = []
    for i in range(9):
        x = left + int((right - left) * i / 8)
        y = mid_y + (amp if i % 2 else -amp)
        points.append((x, y))
    pygame.draw.lines(surf, (17, 50, 62), False, points, 6)
    pygame.draw.lines(surf, (87, 239, 255), False, points, 3)

    pygame.draw.rect(surf, (19, 24, 30), rect, 3, border_radius=6)
    return surf


def _make_spike(size=(24, 40)) -> pygame.Surface:
    surf = pygame.Surface(size, pygame.SRCALPHA)
    rect = surf.get_rect()

    base_h = max(7, rect.height // 3)
    base = pygame.Rect(0, rect.height - base_h, rect.width, base_h)
    pygame.draw.rect(surf, (82, 25, 31), base)
    pygame.draw.line(surf, (186, 44, 53), base.topleft, base.topright, 2)
    pygame.draw.line(surf, (45, 13, 18), base.bottomleft, base.bottomright, 3)

    peak = (rect.centerx, 3)
    points = [(1, base.top + 1), peak, (rect.right - 1, base.top + 1)]
    pygame.draw.polygon(surf, (218, 231, 236), points)
    pygame.draw.polygon(
        surf,
        (132, 146, 158),
        [peak, (rect.right - 1, base.top + 1), (rect.centerx, base.top + 1)],
    )
    pygame.draw.polygon(surf, (35, 38, 45), points, 2)
    pygame.draw.line(
        surf,
        (255, 255, 255),
        (peak[0] - 2, peak[1] + 5),
        (5, base.top - 1),
        1,
    )

    pygame.draw.line(surf, (35, 18, 24), base.topleft, base.topright, 2)
    return surf


def _parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--only",
        nargs="+",
        choices=(
            "background",
            "ball",
            "skins",
            "platform",
            "obstacle",
            "goal",
            "spring",
            "spike",
        ),
        help="Сгенерировать только перечисленные ассеты.",
    )
    return parser.parse_args(argv)


def main(argv=None) -> None:
    args = _parse_args(argv)

    def wants(name: str) -> bool:
        return args.only is None or name in args.only

    pygame.init()

    if wants("background"):
        bg = _make_background()
        pygame.image.save(bg, str(ASSETS_DIR / "background.png"))
        print(f"saved {ASSETS_DIR / 'background.png'}")

    if wants("ball"):
        ball = _make_ball(radius=20)
        pygame.image.save(ball, str(ASSETS_DIR / "ball.png"))
        print(f"saved {ASSETS_DIR / 'ball.png'}")

    if wants("skins"):
        SKINS_DIR.mkdir(parents=True, exist_ok=True)
        for skin in skins.SKINS:
            path = SKINS_DIR / FILENAMES[skin.sprite_id]
            pygame.image.save(make_skin_surface(skin), str(path))
            print(f"saved {path}")

    if wants("platform"):
        platform = _make_platform()
        pygame.image.save(platform, str(ASSETS_DIR / "platform.png"))
        print(f"saved {ASSETS_DIR / 'platform.png'}")

    if wants("obstacle"):
        obstacle = _make_obstacle()
        pygame.image.save(obstacle, str(ASSETS_DIR / "obstacle.png"))
        print(f"saved {ASSETS_DIR / 'obstacle.png'}")

    if wants("goal"):
        goal = _make_goal()
        pygame.image.save(goal, str(ASSETS_DIR / "goal.png"))
        print(f"saved {ASSETS_DIR / 'goal.png'}")

    if wants("spring"):
        spring = _make_spring()
        pygame.image.save(spring, str(ASSETS_DIR / "spring.png"))
        print(f"saved {ASSETS_DIR / 'spring.png'}")

    if wants("spike"):
        spike = _make_spike()
        pygame.image.save(spike, str(ASSETS_DIR / "spike.png"))
        print(f"saved {ASSETS_DIR / 'spike.png'}")

    pygame.quit()


if __name__ == "__main__":
    main()
