"""Генерация мини-превью уровня для меню выбора.

Чистая функция от LevelDef → pygame.Surface. Не создаёт pymunk-объекты,
просто рисует масштабированные прямоугольники по координатам блоков.
"""
from typing import Tuple

import pygame

from ..utils import assets
from ..utils.config import HEIGHT, WIDTH
from ..utils.level import LevelDef


def make_preview(
    level_def: LevelDef, size: Tuple[int, int] = (220, 154), sprites=None
) -> pygame.Surface:
    """Рисует упрощённое превью уровня в Surface заданного размера."""
    surf = pygame.Surface(size, pygame.SRCALPHA)
    if sprites is None:
        sprites = assets.get_sprite_manager()

    background = sprites.get_scaled("background", size)
    if background is not None:
        surf.blit(background, (0, 0))
    else:
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

    def _draw_tiled(sprite_id, rect, fallback_color, border_color):
        if rect.width <= 0 or rect.height <= 0:
            return
        sprite = sprites.get_tiled(sprite_id, rect.size)
        if sprite is not None:
            surf.blit(sprite, rect)
        else:
            pygame.draw.rect(surf, fallback_color, rect)
        pygame.draw.rect(surf, border_color, rect, 1)

    def _draw_scaled(sprite_id, rect, fallback_color, border_color):
        if rect.width <= 0 or rect.height <= 0:
            return
        sprite = sprites.get_scaled(sprite_id, rect.size)
        if sprite is not None:
            surf.blit(sprite, rect)
        else:
            pygame.draw.rect(surf, fallback_color, rect)
        pygame.draw.rect(surf, border_color, rect, 1)

    for b in level_def.platforms:
        _draw_tiled("platform", _scaled(b), (50, 180, 60), (40, 30, 20))

    for b in level_def.obstacles:
        _draw_tiled("obstacle", _scaled(b), (50, 70, 200), (30, 30, 40))

    _draw_scaled("goal", _scaled(level_def.goal), (240, 220, 60), (40, 30, 0))

    bx, by = level_def.ball_start
    radius = max(2, int(6 * min(sx, sy)))
    ball_sprite = sprites.get_scaled("ball", (radius * 2, radius * 2))
    if ball_sprite is not None:
        rect = ball_sprite.get_rect(center=(int(bx * sx), int(by * sy)))
        surf.blit(ball_sprite, rect)
    else:
        pygame.draw.circle(surf, (220, 40, 40), (int(bx * sx), int(by * sy)), radius)

    pygame.draw.rect(surf, (60, 60, 80), surf.get_rect(), 2)

    return surf
