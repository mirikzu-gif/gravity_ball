"""Тесты make_preview — генератор мини-превью уровня."""
import pygame
import pytest

from src.scenes.level_preview import make_preview
from src.utils.level import LEVELS


@pytest.mark.parametrize("level_index", range(len(LEVELS)))
def test_preview_returns_surface_of_requested_size(level_index):
    surf = make_preview(LEVELS[level_index], size=(100, 70))
    assert isinstance(surf, pygame.Surface)
    assert surf.get_size() == (100, 70)


def test_preview_default_size():
    surf = make_preview(LEVELS[0])
    # дефолтный размер задан в самой функции, проверяем что Surface получилось
    assert isinstance(surf, pygame.Surface)
    assert surf.get_width() > 0
    assert surf.get_height() > 0


def test_preview_handles_level_with_no_obstacles():
    """Уровень «Старт» не имеет obstacles — превью всё равно должно отрисоваться."""
    start = LEVELS[0]
    assert len(start.obstacles) == 0
    make_preview(start)  # не должно падать


def test_preview_renders_distinct_colors_for_known_layout():
    """Превью должно содержать цвет цели — простая sanity-проверка."""
    surf = make_preview(LEVELS[1], size=(500, 350))  # достаточно большой превью
    pixels = {surf.get_at((x, y))[:3]
              for x in range(0, 500, 5)
              for y in range(0, 350, 5)}
    # ожидаем хотя бы 3 разных цвета: фон, платформа, цель
    assert len(pixels) >= 3


class _Sprites:
    def __init__(self):
        self.scaled_calls = []
        self.tiled_calls = []

    def get_scaled(self, sprite_id, size):
        self.scaled_calls.append((sprite_id, size))
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill((10, 20, 30))
        return surface

    def get_tiled(self, sprite_id, size):
        self.tiled_calls.append((sprite_id, size))
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill((40, 50, 60))
        return surface


def test_preview_uses_texture_sprites():
    sprites = _Sprites()

    make_preview(LEVELS[1], size=(500, 350), sprites=sprites)

    scaled_ids = [call[0] for call in sprites.scaled_calls]
    tiled_ids = [call[0] for call in sprites.tiled_calls]
    assert "background" in scaled_ids
    assert "goal" in scaled_ids
    assert "ball" in scaled_ids
    assert "platform" in tiled_ids
    assert "obstacle" in tiled_ids
