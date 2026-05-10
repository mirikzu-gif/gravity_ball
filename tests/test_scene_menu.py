"""Тесты MenuScene."""
import pygame

from src.scenes.level_select import LevelSelectScene
from src.scenes.menu import MenuScene
from src.scenes.skin_select import SkinSelectScene


def _ev(type_, **attrs):
    return pygame.event.Event(type_, **attrs)


def test_enter_transitions_to_level_select():
    scene = MenuScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert isinstance(scene.next_scene, LevelSelectScene)


def test_space_transitions_to_level_select():
    scene = MenuScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_SPACE))
    assert isinstance(scene.next_scene, LevelSelectScene)


def test_down_then_enter_transitions_to_skin_select():
    scene = MenuScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_DOWN))
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert isinstance(scene.next_scene, SkinSelectScene)


def test_up_wraps_to_skin_select_button():
    scene = MenuScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_UP))
    assert scene.selected == MenuScene.SKINS_INDEX


def test_mouse_click_on_skins_button_opens_skin_select():
    scene = MenuScene()
    pos = scene._button_rect(MenuScene.SKINS_INDEX).center
    scene.handle_event(_ev(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
    assert isinstance(scene.next_scene, SkinSelectScene)


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
