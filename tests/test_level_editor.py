"""Tests for the standalone level editor helpers."""
import json

import pygame

from tools.level_editor import (
    LevelEditor,
    LevelDraft,
    block_rect,
    clamp_block,
    clamp_point,
    create_default_draft,
    hit_test,
    load_level_draft,
    next_level_id,
    save_level_draft,
    save_manifest,
    snap,
)


def test_snap_rounds_to_grid():
    assert snap(14, 10) == 10
    assert snap(16, 10) == 20


def test_block_rect_uses_center_coordinates():
    rect = block_rect([100, 200, 50, 20])
    assert rect == pygame.Rect(75, 190, 50, 20)


def test_clamp_point_keeps_ball_inside_world():
    point = [-100, 9999]
    clamp_point(point)
    assert point == [20, 680]


def test_clamp_block_keeps_block_inside_world_and_positive():
    block = [-100, 9999, -1, 0]
    clamp_block(block)
    assert block[2] == 10
    assert block[3] == 10
    assert block[0] == 5
    assert block[1] == 695


def test_hit_test_prefers_ball_then_hazards_then_obstacle_then_goal_then_platform():
    draft = LevelDraft(
        name="Test",
        ball_start=[100, 100],
        platforms=[[430, 300, 120, 20]],
        obstacles=[[400, 300, 60, 60]],
        goal=[500, 500, 40, 60],
        springs=[[260, 300, 70, 24]],
        spikes=[[180, 300, 70, 34]],
    )

    assert hit_test(draft, (100, 100)) == ("ball", -1)
    assert hit_test(draft, (180, 300)) == ("spike", 0)
    assert hit_test(draft, (260, 300)) == ("spring", 0)
    assert hit_test(draft, (400, 300)) == ("obstacle", 0)
    assert hit_test(draft, (500, 500)) == ("goal", -1)
    assert hit_test(draft, (460, 300)) == ("platform", 0)
    assert hit_test(draft, (10, 10)) is None


def test_load_and_save_level_draft(tmp_path):
    path = tmp_path / "level.json"
    path.write_text(
        json.dumps(
            {
                "name": "Редактор",
                "ball_start": [10.2, 20.7],
                "platforms": [[100, 200, 50, 20]],
                "obstacles": [[300, 400, 30, 40]],
                "springs": [[350, 420, 90, 24]],
                "spikes": [[420, 470, 80, 30]],
                "goal": [500, 600, 40, 60],
            }
        ),
        encoding="utf-8",
    )

    draft = load_level_draft(path)
    assert draft.name == "Редактор"
    assert draft.ball_start == [10, 21]
    assert draft.springs == [[350, 420, 90, 24]]
    assert draft.spikes == [[420, 470, 80, 30]]

    draft.platforms.append([700, 650, 90, 20])
    draft.springs.append([220, 330, 80, 20])
    save_level_draft(path, draft)

    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["platforms"][-1] == [700, 650, 90, 20]
    assert raw["springs"][-1] == [220, 330, 80, 20]


def test_save_manifest_writes_level_order(tmp_path):
    manifest = tmp_path / "manifest.json"

    save_manifest(["a", "b"], manifest)

    assert json.loads(manifest.read_text(encoding="utf-8")) == {"levels": ["a", "b"]}


def test_next_level_id_skips_existing_files(tmp_path):
    (tmp_path / "level_003.json").write_text("{}", encoding="utf-8")

    assert next_level_id(["level_001", "level_002"], tmp_path) == "level_004"


def test_create_default_draft_has_playable_shape():
    draft = create_default_draft(13)

    assert draft.name == "Новый уровень 13"
    assert draft.ball_start == [120, 100]
    assert draft.platforms
    assert draft.springs == []
    assert draft.spikes == []
    assert draft.goal == [840, 560, 40, 60]


def test_editor_create_level_updates_manifest_and_switches(monkeypatch, tmp_path):
    import tools.level_editor as level_editor

    levels_dir = tmp_path / "levels"
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
                "goal": [840, 560, 40, 60],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(level_editor, "LEVELS_DIR", levels_dir)
    monkeypatch.setattr(level_editor, "MANIFEST_PATH", manifest)

    editor = LevelEditor()
    editor.create_level()

    assert editor.index == 1
    assert editor.path == levels_dir / "level_002.json"
    assert editor.draft.name == "Новый уровень 2"
    assert (levels_dir / "level_002.json").exists()
    assert json.loads(manifest.read_text(encoding="utf-8")) == {
        "levels": ["start", "level_002"]
    }


def test_editor_create_level_refuses_dirty_changes(monkeypatch, tmp_path):
    import tools.level_editor as level_editor

    levels_dir = tmp_path / "levels"
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
                "goal": [840, 560, 40, 60],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(level_editor, "LEVELS_DIR", levels_dir)
    monkeypatch.setattr(level_editor, "MANIFEST_PATH", manifest)

    editor = LevelEditor()
    editor.dirty = True
    editor.create_level()

    assert editor.index == 0
    assert not (levels_dir / "level_002.json").exists()
