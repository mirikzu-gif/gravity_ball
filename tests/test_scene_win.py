"""Тесты WinScene."""
import pygame

from src.scenes.play import GameScene
from src.scenes.win import WinScene
from src.utils import best_times


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


def test_default_total_time_is_zero():
    scene = WinScene()
    assert scene.total_time == 0.0


def test_total_time_stored_and_rendered():
    scene = WinScene(total_time=125.5)
    assert scene.total_time == 125.5
    # render не должен падать
    screen = pygame.Surface((1000, 700))
    scene.render(screen)


def test_first_run_records_new_record():
    scene = WinScene(total_time=42.0)
    assert scene.is_new_record is True
    assert best_times.best_total() == 42.0


def test_better_time_records_new_record():
    best_times.record_total(50.0)
    scene = WinScene(total_time=42.0)
    assert scene.is_new_record is True
    assert best_times.best_total() == 42.0


def test_worse_time_does_not_record():
    best_times.record_total(20.0)
    scene = WinScene(total_time=42.0)
    assert scene.is_new_record is False
    assert scene.best_total == 20.0
    assert best_times.best_total() == 20.0
