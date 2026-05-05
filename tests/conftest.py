"""Общая конфигурация тестов: headless-режим pygame и фикстуры pymunk."""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pymunk
import pytest


@pytest.fixture
def space():
    return pymunk.Space()
