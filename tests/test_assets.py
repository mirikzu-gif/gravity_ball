"""Тесты AssetManager (src.utils.assets)."""
from pathlib import Path

import pygame
import pytest

from src.utils import assets


@pytest.fixture(autouse=True)
def _reset_cache_before():
    assets.reset_cache()
    yield
    assets.reset_cache()


@pytest.fixture
def tmp_assets_dir(monkeypatch, tmp_path):
    """Подменяет ASSETS_DIR на tmp_path для изоляции тестов."""
    monkeypatch.setattr(assets, "ASSETS_DIR", tmp_path)
    return tmp_path


def _save_test_image(path: Path, color=(0, 200, 0), size=(8, 8)):
    surf = pygame.Surface(size)
    surf.fill(color)
    pygame.image.save(surf, str(path))


def test_returns_none_when_file_missing(tmp_assets_dir):
    assert assets.get_image("missing.png") is None


def test_loads_existing_image(tmp_assets_dir):
    _save_test_image(tmp_assets_dir / "tile.png")
    surf = assets.get_image("tile.png")
    assert isinstance(surf, pygame.Surface)


def test_returns_same_surface_on_second_call(tmp_assets_dir):
    _save_test_image(tmp_assets_dir / "tile.png")
    a = assets.get_image("tile.png")
    b = assets.get_image("tile.png")
    assert a is b


def test_caches_misses_too(tmp_assets_dir):
    """Первый вызов вернул None, файл потом появился — но из кэша всё ещё None."""
    assert assets.get_image("late.png") is None
    _save_test_image(tmp_assets_dir / "late.png")
    assert assets.get_image("late.png") is None  # кэш не перезагружается
    assets.reset_cache()
    assert assets.get_image("late.png") is not None


def test_corrupt_file_returns_none(tmp_assets_dir):
    (tmp_assets_dir / "broken.png").write_text("not an image", encoding="utf-8")
    assert assets.get_image("broken.png") is None


def test_default_assets_dir_resolves_to_project_root():
    expected = Path(__file__).resolve().parent.parent / "assets"
    assert assets.ASSETS_DIR == expected


# ---------------------------------------------------------------------------
# Sanity-check сгенерированных дефолтных PNG
# ---------------------------------------------------------------------------


def test_default_background_loads():
    """Если кто-то запустил tools/generate_assets.py — background должен парситься."""
    project_assets = Path(__file__).resolve().parent.parent / "assets"
    if not (project_assets / "background.png").exists():
        pytest.skip("assets/background.png отсутствует — запусти tools/generate_assets.py")
    assets.reset_cache()
    surf = assets.get_image("background.png")
    assert surf is not None


def test_default_ball_loads():
    project_assets = Path(__file__).resolve().parent.parent / "assets"
    if not (project_assets / "ball.png").exists():
        pytest.skip("assets/ball.png отсутствует — запусти tools/generate_assets.py")
    assets.reset_cache()
    surf = assets.get_image("ball.png")
    assert surf is not None
