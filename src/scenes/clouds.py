"""Декоративные облака с эффектом параллакса.

Несколько облаков плывут справа налево с разными скоростями: меньшие
(«дальние») движутся медленнее, большие — быстрее, что создаёт ощущение
глубины. Облака детерминированы (фиксированный random.Random) — каждый
запуск выглядит одинаково, но разнообразно по компоновке.
"""
import random
from typing import List

import pygame

from ..utils.config import WIDTH


class Cloud:
    """Одно облачко — три перекрывающихся эллипса для «пушистости»."""

    def __init__(self, x: float, y: float, scale: float, speed: float) -> None:
        self.x = x
        self.y = y
        self.scale = scale
        self.speed = speed  # px/sec, отрицательное — влево

    def update(self, dt: float) -> None:
        self.x += self.speed * dt
        # утащили за левый край? Возрождаемся справа.
        right_edge = self.x + 80 * self.scale
        if right_edge < 0:
            self.x = WIDTH + 60 * self.scale

    def draw(self, screen: pygame.Surface, color) -> None:
        s = self.scale
        x, y = int(self.x), int(self.y)
        # 3 эллипса разного размера и оффсета — пушистее, чем один
        pygame.draw.ellipse(screen, color, (x - int(60 * s), y - int(15 * s), int(120 * s), int(35 * s)))
        pygame.draw.ellipse(screen, color, (x - int(30 * s), y - int(30 * s), int(80 * s), int(50 * s)))
        pygame.draw.ellipse(screen, color, (x + int(10 * s), y - int(20 * s), int(70 * s), int(40 * s)))


def generate_clouds(count: int = 6, seed: int = 42) -> List[Cloud]:
    """Создаёт детерминированный набор облаков с параллакс-скоростями."""
    rng = random.Random(seed)
    clouds: List[Cloud] = []
    for _ in range(count):
        x = rng.uniform(0, WIDTH)
        y = rng.uniform(40, 200)
        scale = rng.uniform(0.4, 1.0)
        # дальние (scale маленький) ползут медленнее → параллакс
        base_speed = rng.uniform(-25, -10)
        clouds.append(Cloud(x, y, scale, base_speed * scale))
    return clouds
