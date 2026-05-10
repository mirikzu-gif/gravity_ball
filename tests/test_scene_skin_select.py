"""Тесты SkinSelectScene."""
import pygame

from src.scenes.menu import MenuScene
from src.scenes.skin_select import SkinSelectScene
from src.utils import skins


def _ev(type_, **attrs):
    return pygame.event.Event(type_, **attrs)


def test_initial_selection_matches_current_skin():
    skins.select_skin(2)
    scene = SkinSelectScene()
    assert scene.selected == 2


def test_constructor_clamps_invalid_to_current_skin():
    skins.select_skin(1)
    scene = SkinSelectScene(selected=999)
    assert scene.selected == 1


def test_right_advances():
    scene = SkinSelectScene(selected=0)
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_RIGHT))
    assert scene.selected == 1


def test_left_wraps_to_last():
    scene = SkinSelectScene(selected=0)
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_LEFT))
    assert scene.selected == skins.skin_count() - 1


def test_wasd_also_navigate():
    scene = SkinSelectScene(selected=0)
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_d))
    assert scene.selected == 1
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_a))
    assert scene.selected == 0


def test_enter_selects_skin_and_returns_to_menu():
    scene = SkinSelectScene(selected=1)
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert skins.get_selected_index() == 1
    assert isinstance(scene.next_scene, MenuScene)


def test_space_also_selects_skin():
    scene = SkinSelectScene(selected=2)
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_SPACE))
    assert skins.get_selected_index() == 2
    assert isinstance(scene.next_scene, MenuScene)


def test_escape_returns_without_changing_skin():
    scene = SkinSelectScene(selected=2)
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert skins.get_selected_index() == skins.DEFAULT_SKIN_INDEX
    assert isinstance(scene.next_scene, MenuScene)


def test_m_returns_to_menu():
    scene = SkinSelectScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_m))
    assert isinstance(scene.next_scene, MenuScene)


def test_q_posts_quit():
    scene = SkinSelectScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_q))
    posted = [e for e in pygame.event.get() if e.type == pygame.QUIT]
    assert len(posted) == 1


def test_unrelated_key_does_nothing():
    scene = SkinSelectScene(selected=0)
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_TAB))
    assert scene.selected == 0
    assert scene.next_scene is None


def test_keyup_does_nothing():
    scene = SkinSelectScene()
    scene.handle_event(_ev(pygame.KEYUP, key=pygame.K_RETURN))
    assert scene.next_scene is None


def test_mouse_hover_updates_selection():
    scene = SkinSelectScene(selected=0)
    pos = scene._card_rect(2).center
    scene.handle_event(_ev(pygame.MOUSEMOTION, pos=pos))
    assert scene.selected == 2


def test_mouse_click_selects_skin_and_returns_to_menu():
    scene = SkinSelectScene(selected=0)
    pos = scene._card_rect(3).center
    scene.handle_event(_ev(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
    assert skins.get_selected_index() == 3
    assert isinstance(scene.next_scene, MenuScene)


def test_render_does_not_crash():
    scene = SkinSelectScene()
    screen = pygame.Surface((1000, 700))
    scene.render(screen)


def test_render_each_selection_does_not_crash():
    for i in range(skins.skin_count()):
        scene = SkinSelectScene(selected=i)
        screen = pygame.Surface((1000, 700))
        scene.render(screen)
