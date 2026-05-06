"""Тесты MenuScene."""
import pygame

from src.scenes.menu import MenuScene
from src.scenes.play import GameScene


def _ev(type_, **attrs):
    return pygame.event.Event(type_, **attrs)


def test_enter_transitions_to_game():
    scene = MenuScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert isinstance(scene.next_scene, GameScene)


def test_space_transitions_to_game():
    scene = MenuScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_SPACE))
    assert isinstance(scene.next_scene, GameScene)


def test_escape_posts_quit():
    scene = MenuScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    posted = [e for e in pygame.event.get() if e.type == pygame.QUIT]
    assert len(posted) == 1


def test_q_posts_quit():
    scene = MenuScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_q))
    posted = [e for e in pygame.event.get() if e.type == pygame.QUIT]
    assert len(posted) == 1


def test_unrelated_key_does_nothing():
    scene = MenuScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_LEFT))
    assert scene.next_scene is None
    assert not [e for e in pygame.event.get() if e.type == pygame.QUIT]


def test_keyup_does_nothing():
    scene = MenuScene()
    scene.handle_event(_ev(pygame.KEYUP, key=pygame.K_RETURN))
    assert scene.next_scene is None


def test_render_does_not_crash():
    scene = MenuScene()
    screen = pygame.Surface((1000, 700))
    scene.render(screen)
