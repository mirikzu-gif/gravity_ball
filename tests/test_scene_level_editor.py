"""Тесты встроенного игрового редактора уровней."""
import json

import pygame
import pytest

from src.scenes.level_editor import CANVAS_RECT, LevelEditorScene
from src.scenes.menu import MenuScene
from src.scenes.play import GameScene


def _ev(type_, **attrs):
    return pygame.event.Event(type_, **attrs)


def _write_level(path, name="Старт"):
    path.write_text(
        json.dumps(
            {
                "name": name,
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


def _mods(value):
    pygame.key.set_mods(value)


@pytest.fixture(autouse=True)
def custom_catalog(monkeypatch, tmp_path):
    import src.scenes.level_editor as scene_module

    levels_dir = tmp_path / "custom_levels"
    levels_dir.mkdir()
    manifest = levels_dir / "manifest.json"
    manifest.write_text(json.dumps({"levels": ["start"]}), encoding="utf-8")
    _write_level(levels_dir / "start.json")

    monkeypatch.setattr(scene_module, "CUSTOM_LEVELS_DIR", levels_dir)
    monkeypatch.setattr(scene_module, "CUSTOM_MANIFEST_PATH", manifest)
    return levels_dir, manifest


def test_editor_scene_loads_first_level():
    scene = LevelEditorScene()
    assert scene.index == 0
    assert scene.draft.name
    assert scene.path.parent.name == "custom_levels"


def test_editor_scene_render_does_not_crash():
    scene = LevelEditorScene()
    screen = pygame.Surface((1000, 700))
    scene.render(screen)


def test_escape_returns_to_menu_when_clean():
    scene = LevelEditorScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert isinstance(scene.next_scene, MenuScene)


def test_escape_keeps_dirty_editor_open():
    scene = LevelEditorScene()
    scene.dirty = True
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert scene.next_scene is None
    assert "несохраненные" in scene.message


def test_mouse_adds_platform_on_scaled_canvas():
    scene = LevelEditorScene()
    scene._set_mode("platform")
    pos = scene._screen_from_world(123, 111)

    scene.handle_event(_ev(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))

    assert scene.draft.platforms[-1] == [120, 110, 180, 20]
    assert scene.selection == ("platform", len(scene.draft.platforms) - 1)
    assert scene.dirty is True


def test_click_outside_canvas_does_not_edit():
    scene = LevelEditorScene()
    scene._set_mode("platform")
    count = len(scene.draft.platforms)

    scene.handle_event(
        _ev(pygame.MOUSEBUTTONDOWN, button=1, pos=(CANVAS_RECT.right + 5, CANVAS_RECT.y))
    )

    assert len(scene.draft.platforms) == count
    assert scene.dirty is False


def test_enter_starts_custom_level_test():
    scene = LevelEditorScene()

    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_RETURN))

    assert isinstance(scene.next_scene, GameScene)
    assert scene.next_scene.level_def.name == scene.draft.name
    assert scene.next_scene._record_progress is False
    assert scene.next_scene._return_scene is scene


def test_save_current_writes_custom_json_without_campaign_reload(
    monkeypatch,
    custom_catalog,
):
    import src.scenes.level_editor as scene_module

    monkeypatch.setattr(
        scene_module.level_utils,
        "reload_levels",
        lambda: pytest.fail("campaign catalog must not reload for custom save"),
    )

    scene = LevelEditorScene()
    scene.draft.name = "Из игры"
    scene.dirty = True
    scene._save_current()

    levels_dir, _ = custom_catalog
    raw = json.loads((levels_dir / "start.json").read_text(encoding="utf-8"))
    assert raw["name"] == "Из игры"
    assert scene.dirty is False


def test_ctrl_n_creates_custom_level_in_game_editor(custom_catalog):
    levels_dir, manifest = custom_catalog
    scene = LevelEditorScene()
    try:
        _mods(pygame.KMOD_CTRL)
        scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_n))
    finally:
        _mods(0)

    assert scene.index == 1
    assert (levels_dir / "level_002.json").exists()
    assert json.loads(manifest.read_text(encoding="utf-8")) == {
        "levels": ["start", "level_002"]
    }
