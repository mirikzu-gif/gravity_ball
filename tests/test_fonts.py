"""Tests for project font helpers."""
import pygame

from src.utils import fonts


def test_font_files_exist():
    assert fonts.TITLE_FONT_PATH.exists()
    assert fonts.UI_FONT_PATH.exists()


def test_title_font_renders_text():
    font = fonts.title(24)
    surface = font.render("Gravity Ball", True, (0, 0, 0))
    assert isinstance(surface, pygame.Surface)
    assert surface.get_width() > 0


def test_ui_font_renders_cyrillic_text():
    font = fonts.ui(18)
    surface = font.render("Выбери уровень", True, (0, 0, 0))
    assert isinstance(surface, pygame.Surface)
    assert surface.get_width() > 0


def test_title_font_has_cyrillic_metrics():
    metrics = fonts.title(24).metrics("Пауза")
    assert all(metric is not None for metric in metrics)


def test_fonts_are_cached():
    assert fonts.title(24) is fonts.title(24)
    assert fonts.ui(18) is fonts.ui(18)


def test_reset_cache_clears_cached_fonts():
    first = fonts.title(24)
    fonts.reset_cache()
    second = fonts.title(24)
    assert second is not first
