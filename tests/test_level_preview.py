"""Тесты make_preview — генератор мини-превью уровня."""
import pygame
import pytest

from src.scenes.level_preview import make_preview
from src.utils.level import LEVELS, Block, LevelDef


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
    """Превью должно отрисовываться для уровня без obstacles."""
    level = LevelDef(
        name="Без препятствий",
        ball_start=(120, 100),
        platforms=(Block(500, 620, 800, 20),),
        obstacles=(),
        goal=Block(820, 560, 40, 60),
    )

    make_preview(level)  # не должно падать


def test_preview_handles_springs_and_spikes():
    level = LevelDef(
        name="Блоки",
        ball_start=(120, 100),
        platforms=(Block(500, 620, 800, 20),),
        obstacles=(),
        goal=Block(820, 560, 40, 60),
        springs=(Block(300, 500, 90, 24),),
        spikes=(Block(520, 590, 90, 34),),
    )

    make_preview(level)


def test_preview_uses_spring_and_spike_sprites():
    sprites = _Sprites()
    level = LevelDef(
        name="Блоки",
        ball_start=(120, 100),
        platforms=(),
        obstacles=(),
        goal=Block(820, 560, 40, 60),
        springs=(Block(300, 500, 90, 24),),
        spikes=(Block(520, 590, 90, 34),),
    )

    make_preview(level, size=(500, 350), sprites=sprites)

    scaled_ids = [call[0] for call in sprites.scaled_calls]
    assert "spring" in scaled_ids
    assert "spike" in scaled_ids


def test_preview_tiles_spike_sprite_without_width_stretching():
    sprites = _Sprites()
    level = LevelDef(
        name="Блоки",
        ball_start=(120, 100),
        platforms=(),
        obstacles=(),
        goal=Block(820, 560, 40, 60),
        spikes=(Block(500, 560, 240, 40),),
    )

    make_preview(level, size=(1000, 700), sprites=sprites)

    spike_sizes = [
        size for sprite_id, size in sprites.scaled_calls if sprite_id == "spike"
    ]
    assert (24, 40) in spike_sizes
    assert (240, 40) not in spike_sizes


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
