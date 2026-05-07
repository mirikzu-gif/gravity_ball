"""Tests for SpriteManager."""
from pathlib import Path

import pygame

from src.rendering.sprites import SpriteManager, SpriteSpec


def _save_test_image(path: Path, color=(20, 120, 220), size=(8, 8)):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(color)
    pygame.image.save(surface, str(path))


def test_loads_registered_sprite(tmp_path):
    _save_test_image(tmp_path / "ball.png")
    sprites = SpriteManager(tmp_path, {"ball": SpriteSpec("ball.png")})

    surface = sprites.get("ball")

    assert isinstance(surface, pygame.Surface)


def test_loads_direct_filename_for_compatibility(tmp_path):
    _save_test_image(tmp_path / "tile.png")
    sprites = SpriteManager(tmp_path)

    surface = sprites.get("tile.png")

    assert isinstance(surface, pygame.Surface)


def test_returns_same_surface_on_second_get(tmp_path):
    _save_test_image(tmp_path / "tile.png")
    sprites = SpriteManager(tmp_path)

    first = sprites.get("tile.png")
    second = sprites.get("tile.png")

    assert first is second


def test_caches_missing_sprite(tmp_path):
    sprites = SpriteManager(tmp_path)

    assert sprites.get("late.png") is None
    _save_test_image(tmp_path / "late.png")
    assert sprites.get("late.png") is None

    sprites.reset()
    assert sprites.get("late.png") is not None


def test_corrupt_sprite_returns_none(tmp_path):
    (tmp_path / "broken.png").write_text("not an image", encoding="utf-8")
    sprites = SpriteManager(tmp_path)

    assert sprites.get("broken.png") is None


def test_get_scaled_caches_scaled_variant(tmp_path):
    _save_test_image(tmp_path / "tile.png", size=(8, 8))
    sprites = SpriteManager(tmp_path)

    first = sprites.get_scaled("tile.png", (16, 12))
    second = sprites.get_scaled("tile.png", (16, 12))

    assert first is second
    assert first.get_size() == (16, 12)


def test_get_scaled_caches_missing_variant(tmp_path):
    sprites = SpriteManager(tmp_path)

    assert sprites.get_scaled("missing.png", (16, 12)) is None
    _save_test_image(tmp_path / "missing.png")
    assert sprites.get_scaled("missing.png", (16, 12)) is None


def test_preload_populates_cache(tmp_path):
    _save_test_image(tmp_path / "ball.png")
    sprites = SpriteManager(tmp_path, {"ball": SpriteSpec("ball.png")})

    sprites.preload(["ball"])
    first = sprites.get("ball")
    second = sprites.get("ball")

    assert first is second


def test_get_tiled_repeats_source_without_scaling(tmp_path):
    surface = pygame.Surface((4, 4), pygame.SRCALPHA)
    surface.fill((10, 20, 30))
    surface.set_at((0, 0), (200, 10, 10))
    pygame.image.save(surface, str(tmp_path / "tile.png"))
    sprites = SpriteManager(tmp_path)

    tiled = sprites.get_tiled("tile.png", (9, 7))

    assert tiled.get_size() == (9, 7)
    assert tiled.get_at((0, 0))[:3] == (200, 10, 10)
    assert tiled.get_at((4, 0))[:3] == (200, 10, 10)
    assert tiled.get_at((8, 4))[:3] == (200, 10, 10)


def test_get_tiled_caches_variant(tmp_path):
    _save_test_image(tmp_path / "tile.png", size=(4, 4))
    sprites = SpriteManager(tmp_path)

    first = sprites.get_tiled("tile.png", (12, 8))
    second = sprites.get_tiled("tile.png", (12, 8))

    assert first is second


def test_get_tiled_caches_missing_variant(tmp_path):
    sprites = SpriteManager(tmp_path)

    assert sprites.get_tiled("missing.png", (12, 8)) is None
    _save_test_image(tmp_path / "missing.png")
    assert sprites.get_tiled("missing.png", (12, 8)) is None
