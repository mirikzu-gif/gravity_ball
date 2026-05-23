"""Тесты MenuScene."""
import json

import pygame
import pytest

from src.scenes.level_select import LevelSelectScene
from src.scenes.level_editor import LevelEditorScene
from src.scenes.menu import MenuScene
from src.scenes.skin_select import SkinSelectScene


def _ev(type_, **attrs):
    return pygame.event.Event(type_, **attrs)


@pytest.fixture(autouse=True)
def custom_editor_catalog(monkeypatch, tmp_path):
    import src.scenes.level_editor as scene_module

    levels_dir = tmp_path / "custom_levels"
    levels_dir.mkdir()
    manifest = levels_dir / "manifest.json"
    manifest.write_text(json.dumps({"levels": ["start"]}), encoding="utf-8")
    (levels_dir / "start.json").write_text(
        json.dumps(
            {
                "name": "Старт",
                "ball_start": [100, 100],
                "platforms": [[500, 620, 800, 20]],
                "obstacles": [],
                "springs": [],
                "spikes": [],
                "goal": [840, 560, 40, 60],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(scene_module, "CUSTOM_LEVELS_DIR", levels_dir)
    monkeypatch.setattr(scene_module, "CUSTOM_MANIFEST_PATH", manifest)


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


def test_up_wraps_to_editor_button():
    scene = MenuScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_UP))
    assert scene.selected == MenuScene.EDITOR_INDEX


def test_mouse_click_on_skins_button_opens_skin_select():
    scene = MenuScene()
    pos = scene._button_rect(MenuScene.SKINS_INDEX).center
    scene.handle_event(_ev(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
    assert isinstance(scene.next_scene, SkinSelectScene)


def test_editor_button_opens_in_game_editor():
    scene = MenuScene()
    scene.selected = MenuScene.EDITOR_INDEX
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert isinstance(scene.next_scene, LevelEditorScene)


def test_mouse_click_on_editor_button_opens_editor():
    scene = MenuScene()
    pos = scene._button_rect(MenuScene.EDITOR_INDEX).center
    scene.handle_event(_ev(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
    assert isinstance(scene.next_scene, LevelEditorScene)


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
