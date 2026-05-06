"""Тесты JSON-загрузчика уровней."""
import json
from pathlib import Path

import pytest

from src.utils.level import Block, LevelDef, load_levels


@pytest.fixture
def tmp_levels_file(tmp_path: Path):
    """Возвращает функцию write(data) → Path для временного файла."""
    file_path = tmp_path / "levels.json"

    def write(data):
        file_path.write_text(json.dumps(data), encoding="utf-8")
        return file_path

    return write


# ---------------------------------------------------------------------------
# Базовая загрузка
# ---------------------------------------------------------------------------


def test_loads_single_level(tmp_levels_file):
    path = tmp_levels_file([
        {
            "name": "Тест",
            "ball_start": [10, 20],
            "platforms": [[100, 200, 50, 10]],
            "obstacles": [[300, 400, 30, 30]],
            "goal": [500, 600, 40, 60],
        }
    ])

    levels = load_levels(path)

    assert len(levels) == 1
    lvl = levels[0]
    assert isinstance(lvl, LevelDef)
    assert lvl.name == "Тест"
    assert lvl.ball_start == (10, 20)
    assert lvl.platforms == (Block(100, 200, 50, 10),)
    assert lvl.obstacles == (Block(300, 400, 30, 30),)
    assert lvl.goal == Block(500, 600, 40, 60)


def test_loads_multiple_levels(tmp_levels_file):
    path = tmp_levels_file([
        {
            "name": "А",
            "ball_start": [0, 0],
            "platforms": [],
            "obstacles": [],
            "goal": [10, 10, 5, 5],
        },
        {
            "name": "Б",
            "ball_start": [1, 1],
            "platforms": [],
            "obstacles": [],
            "goal": [20, 20, 5, 5],
        },
    ])

    levels = load_levels(path)
    assert tuple(lvl.name for lvl in levels) == ("А", "Б")


def test_returns_tuple(tmp_levels_file):
    path = tmp_levels_file([
        {
            "name": "x",
            "ball_start": [0, 0],
            "platforms": [],
            "obstacles": [],
            "goal": [1, 1, 1, 1],
        }
    ])
    assert isinstance(load_levels(path), tuple)


# ---------------------------------------------------------------------------
# Ошибки формата
# ---------------------------------------------------------------------------


def test_root_must_be_list(tmp_path):
    file_path = tmp_path / "bad.json"
    file_path.write_text('{"name": "wrong"}', encoding="utf-8")
    with pytest.raises(ValueError, match="массивом"):
        load_levels(file_path)


@pytest.mark.parametrize(
    "missing_field",
    ["name", "ball_start", "platforms", "obstacles", "goal"],
)
def test_missing_field_raises(tmp_levels_file, missing_field):
    item = {
        "name": "x",
        "ball_start": [0, 0],
        "platforms": [],
        "obstacles": [],
        "goal": [1, 1, 1, 1],
    }
    item.pop(missing_field)
    path = tmp_levels_file([item])
    with pytest.raises(ValueError, match="отсутств"):
        load_levels(path)


def test_block_with_wrong_arity_raises(tmp_levels_file):
    path = tmp_levels_file([
        {
            "name": "x",
            "ball_start": [0, 0],
            "platforms": [[1, 2, 3]],  # 3 значения, а нужно 4
            "obstacles": [],
            "goal": [1, 1, 1, 1],
        }
    ])
    with pytest.raises(ValueError, match="4 значения"):
        load_levels(path)


def test_ball_start_with_wrong_arity_raises(tmp_levels_file):
    path = tmp_levels_file([
        {
            "name": "x",
            "ball_start": [0, 0, 0],
            "platforms": [],
            "obstacles": [],
            "goal": [1, 1, 1, 1],
        }
    ])
    with pytest.raises(ValueError, match="ball_start"):
        load_levels(path)


def test_invalid_json_raises(tmp_path):
    file_path = tmp_path / "bad.json"
    file_path.write_text("not json at all", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_levels(file_path)


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_levels(tmp_path / "missing.json")


# ---------------------------------------------------------------------------
# Default levels.json существует и парсится
# ---------------------------------------------------------------------------


def test_default_levels_file_exists():
    """Файл levels/levels.json в репозитории должен парситься без ошибок."""
    project_root = Path(__file__).resolve().parent.parent
    default = project_root / "levels" / "levels.json"
    assert default.exists()
    levels = load_levels(default)
    assert len(levels) >= 1
