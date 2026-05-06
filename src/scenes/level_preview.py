"""Генерация мини-превью уровня для меню выбора.

Чистая функция от LevelDef → pygame.Surface. Не создаёт pymunk-объекты,
просто рисует масштабированные прямоугольники по координатам блоков.
"""
from typing import Tuple

import pygame

from ..utils.config import HEIGHT, WIDTH
from ..utils.level import LevelDef


def make_preview(
    level_def: LevelDef, size: Tuple[int, int] = (220, 154)
) -> pygame.Surface:
    """Рисует упрощённое превью уровня в Surface заданного размера."""
    surf = pygame.Surface(size)
    surf.fill((215, 230, 245))

    sx = size[0] / WIDTH
    sy = size[1] / HEIGHT

    def _scaled(block):
        return pygame.Rect(
            int((block.x - block.width / 2) * sx),
            int((block.y - block.height / 2) * sy),
            max(1, int(block.width * sx)),
            max(1, int(block.height * sy)),
        )

    # Платформы (зелёные)
    for b in level_def.platforms:
        pygame.draw.rect(surf, (50, 180, 60), _scaled(b))

    # Препятствия (синие)
    for b in level_def.obstacles:
        pygame.draw.rect(surf, (50, 70, 200), _scaled(b))

    # Цель (жёлтая)
    pygame.draw.rect(surf, (240, 220, 60), _scaled(level_def.goal))
    pygame.draw.rect(surf, (40, 30, 0), _scaled(level_def.goal), 1)

    # Старт мяча (красная точка)
    bx, by = level_def.ball_start
    radius = max(2, int(6 * min(sx, sy)))
    pygame.draw.circle(surf, (220, 40, 40), (int(bx * sx), int(by * sy)), radius)

    # Рамка
    pygame.draw.rect(surf, (60, 60, 80), surf.get_rect(), 2)

    return surf
