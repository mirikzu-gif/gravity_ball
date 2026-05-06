"""Тесты WinScene."""
import pygame

from src.scenes.play import GameScene
from src.scenes.win import WinScene


def _ev(type_, **attrs):
    return pygame.event.Event(type_, **attrs)


def test_enter_starts_new_game():
    scene = WinScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert isinstance(scene.next_scene, GameScene)


def test_space_starts_new_game():
    scene = WinScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_SPACE))
    assert isinstance(scene.next_scene, GameScene)


def test_escape_posts_quit():
    scene = WinScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    posted = [e for e in pygame.event.get() if e.type == pygame.QUIT]
    assert len(posted) == 1


def test_render_does_not_crash():
    scene = WinScene()
    screen = pygame.Surface((1000, 700))
    scene.render(screen)
