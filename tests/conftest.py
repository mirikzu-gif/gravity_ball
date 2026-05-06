"""Общая конфигурация тестов: headless-режим pygame и фикстуры pymunk."""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pymunk
import pytest

from src.utils import best_times


@pytest.fixture(autouse=True)
def _pygame_init():
    """Поднимает pygame перед каждым тестом и чистит очередь событий после.

    Нужен потому что сцены создают pygame.font.Font в __init__, а run_scenes
    вызывает pygame.quit() в конце — без этого следующий тест видит «video
    system not initialized».
    """
    pygame.init()
    pygame.event.clear()
    yield
    try:
        pygame.event.clear()
    except pygame.error:
        # pygame.quit() мог быть вызван внутри теста (run_scenes)
        pass


@pytest.fixture(autouse=True)
def _isolated_best_times(monkeypatch, tmp_path):
    """Каждый тест получает свой best_times.json в tmp_path,
    чтобы не мусорить и не зависеть от реального файла рекордов."""
    monkeypatch.setattr(best_times, "DEFAULT_PATH", tmp_path / "best_times.json")


@pytest.fixture
def space():
    return pymunk.Space()
