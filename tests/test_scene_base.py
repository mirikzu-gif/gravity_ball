"""Тесты Scene API."""
import pygame

from src.scenes.base import Scene


def test_scene_default_next_scene_is_none():
    scene = Scene()
    assert scene.next_scene is None


def test_scene_default_handle_event_is_noop():
    scene = Scene()
    scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a))
    assert scene.next_scene is None


def test_scene_default_fixed_update_is_noop():
    scene = Scene()
    scene.fixed_update(1 / 60.0)


def test_scene_default_render_is_noop():
    scene = Scene()
    surface = pygame.Surface((10, 10))
    scene.render(surface)


def test_scene_default_render_accepts_alpha():
    scene = Scene()
    surface = pygame.Surface((10, 10))
    scene.render(surface, alpha=0.0)
    scene.render(surface, alpha=0.5)
    scene.render(surface, alpha=0.99)


def test_scene_can_set_next_scene():
    scene = Scene()
    other = Scene()
    scene.next_scene = other
    assert scene.next_scene is other
