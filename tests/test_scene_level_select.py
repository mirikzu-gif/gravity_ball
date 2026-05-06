"""Тесты LevelSelectScene."""
import pygame

from src.scenes.level_select import LevelSelectScene
from src.scenes.menu import MenuScene
from src.scenes.play import GameScene
from src.utils.level import LEVELS


def _ev(type_, **attrs):
    return pygame.event.Event(type_, **attrs)


def test_initial_selection_is_zero():
    scene = LevelSelectScene()
    assert scene.selected == 0


def test_constructor_clamps_invalid_to_zero():
    scene = LevelSelectScene(selected=999)
    assert scene.selected == 0
    scene2 = LevelSelectScene(selected=-1)
    assert scene2.selected == 0


def test_can_pre_select_a_level():
    scene = LevelSelectScene(selected=1)
    assert scene.selected == 1


def test_down_advances():
    scene = LevelSelectScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_DOWN))
    assert scene.selected == 1


def test_down_wraps_to_zero():
    scene = LevelSelectScene(selected=len(LEVELS) - 1)
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_DOWN))
    assert scene.selected == 0


def test_up_wraps_to_last():
    scene = LevelSelectScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_UP))
    assert scene.selected == len(LEVELS) - 1


def test_w_and_s_also_navigate():
    scene = LevelSelectScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_s))
    assert scene.selected == 1
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_w))
    assert scene.selected == 0


def test_enter_starts_game_at_selected_level():
    scene = LevelSelectScene(selected=1)
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert isinstance(scene.next_scene, GameScene)
    assert scene.next_scene.level_index == 1


def test_space_also_starts_game():
    scene = LevelSelectScene(selected=0)
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_SPACE))
    assert isinstance(scene.next_scene, GameScene)


def test_escape_returns_to_menu():
    scene = LevelSelectScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert isinstance(scene.next_scene, MenuScene)


def test_m_returns_to_menu():
    scene = LevelSelectScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_m))
    assert isinstance(scene.next_scene, MenuScene)


def test_q_posts_quit():
    scene = LevelSelectScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_q))
    posted = [e for e in pygame.event.get() if e.type == pygame.QUIT]
    assert len(posted) == 1


def test_unrelated_key_does_nothing():
    scene = LevelSelectScene(selected=0)
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_a))
    assert scene.selected == 0
    assert scene.next_scene is None


def test_keyup_does_nothing():
    scene = LevelSelectScene()
    scene.handle_event(_ev(pygame.KEYUP, key=pygame.K_RETURN))
    assert scene.next_scene is None


def test_render_does_not_crash():
    scene = LevelSelectScene()
    screen = pygame.Surface((1000, 700))
    scene.render(screen)


def test_render_each_selection_does_not_crash():
    for i in range(len(LEVELS)):
        scene = LevelSelectScene(selected=i)
        screen = pygame.Surface((1000, 700))
        scene.render(screen)


# ---------------------------------------------------------------------------
# Интеграция с MenuScene
# ---------------------------------------------------------------------------


def test_menu_enter_now_goes_to_level_select():
    menu = MenuScene()
    menu.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert isinstance(menu.next_scene, LevelSelectScene)
