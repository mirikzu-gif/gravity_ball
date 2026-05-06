"""Тесты JSON-загрузчиков уровней и LevelCatalog."""
import json
from pathlib import Path

import pytest

from src.utils.level import (
    Block,
    LevelCatalog,
    LevelDef,
    load_level_file,
    load_levels,
    load_manifest,
)


@pytest.fixture
def tmp_levels_file(tmp_path: Path):
    """Возвращает функцию write(data) → Path для временного файла-массива."""
    file_path = tmp_path / "levels.json"

    def write(data):
        file_path.write_text(json.dumps(data), encoding="utf-8")
        return file_path

    return write


@pytest.fixture
def tmp_level_dir(tmp_path: Path):
    """Создаёт временную директорию с manifest и двумя уровнями.

    Возвращает Path до manifest.json — пригоден к LevelCatalog.
    """
    (tmp_path / "a.json").write_text(
        json.dumps({
            "name": "A",
            "ball_start": [10, 20],
            "platforms": [[100, 100, 50, 10]],
            "obstacles": [],
            "goal": [200, 200, 40, 60],
        }),
        encoding="utf-8",
    )
    (tmp_path / "b.json").write_text(
        json.dumps({
            "name": "B",
            "ball_start": [30, 40],
            "platforms": [],
            "obstacles": [[300, 300, 30, 30]],
            "goal": [400, 400, 40, 60],
        }),
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"levels": ["a", "b"]}), encoding="utf-8")
    return manifest


# ---------------------------------------------------------------------------
# load_levels (legacy: одиночный файл-массив)
# ---------------------------------------------------------------------------


def test_load_levels_loads_single_level(tmp_levels_file):
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


def test_load_levels_root_must_be_list(tmp_path):
    file_path = tmp_path / "bad.json"
    file_path.write_text('{"name": "wrong"}', encoding="utf-8")
    with pytest.raises(ValueError, match="массивом"):
        load_levels(file_path)


@pytest.mark.parametrize(
    "missing_field",
    ["name", "ball_start", "platforms", "obstacles", "goal"],
)
def test_load_levels_missing_field_raises(tmp_levels_file, missing_field):
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


def test_load_levels_block_with_wrong_arity_raises(tmp_levels_file):
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


# ---------------------------------------------------------------------------
# load_level_file (новый формат — отдельный файл на уровень)
# ---------------------------------------------------------------------------


def test_load_level_file(tmp_path):
    path = tmp_path / "lvl.json"
    path.write_text(
        json.dumps({
            "name": "Уровень",
            "ball_start": [50, 60],
            "platforms": [[1, 2, 3, 4]],
            "obstacles": [],
            "goal": [10, 20, 30, 40],
        }),
        encoding="utf-8",
    )
    lvl = load_level_file(path)
    assert isinstance(lvl, LevelDef)
    assert lvl.name == "Уровень"
    assert lvl.ball_start == (50, 60)


def test_load_level_file_root_must_be_object(tmp_path):
    path = tmp_path / "lvl.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="объектом"):
        load_level_file(path)


def test_load_level_file_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_level_file(tmp_path / "missing.json")


# ---------------------------------------------------------------------------
# load_manifest
# ---------------------------------------------------------------------------


def test_load_manifest(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"levels": ["a", "b", "c"]}), encoding="utf-8")
    assert load_manifest(manifest) == ("a", "b", "c")


def test_load_manifest_root_must_be_object(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="полем 'levels'"):
        load_manifest(manifest)


def test_load_manifest_levels_must_be_list(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"levels": "wrong"}), encoding="utf-8")
    with pytest.raises(ValueError, match="массивом"):
        load_manifest(manifest)


# ---------------------------------------------------------------------------
# LevelCatalog
# ---------------------------------------------------------------------------


def test_catalog_length(tmp_level_dir):
    cat = LevelCatalog(tmp_level_dir)
    assert len(cat) == 2


def test_catalog_names(tmp_level_dir):
    cat = LevelCatalog(tmp_level_dir)
    assert cat.names == ("a", "b")


def test_catalog_lazy_loading(tmp_level_dir):
    """Создание каталога не должно читать файлы уровней."""
    cat = LevelCatalog(tmp_level_dir)
    assert not cat.is_loaded(0)
    assert not cat.is_loaded(1)


def test_catalog_loads_on_index(tmp_level_dir):
    cat = LevelCatalog(tmp_level_dir)
    lvl_a = cat[0]
    assert isinstance(lvl_a, LevelDef)
    assert lvl_a.name == "A"
    assert cat.is_loaded(0)
    assert not cat.is_loaded(1)


def test_catalog_caches(tmp_level_dir):
    cat = LevelCatalog(tmp_level_dir)
    first = cat[0]
    second = cat[0]
    assert first is second


def test_catalog_iter_loads_all(tmp_level_dir):
    cat = LevelCatalog(tmp_level_dir)
    levels = list(cat)
    assert len(levels) == 2
    assert [lvl.name for lvl in levels] == ["A", "B"]
    assert cat.is_loaded(0)
    assert cat.is_loaded(1)


def test_catalog_index_out_of_range(tmp_level_dir):
    cat = LevelCatalog(tmp_level_dir)
    with pytest.raises(IndexError):
        cat[5]
    with pytest.raises(IndexError):
        cat[-1]  # отрицательные не поддерживаются (явная семантика)


# ---------------------------------------------------------------------------
# Default manifest существует и парсится
# ---------------------------------------------------------------------------


def test_default_manifest_exists():
    project_root = Path(__file__).resolve().parent.parent
    manifest = project_root / "levels" / "manifest.json"
    assert manifest.exists()
    cat = LevelCatalog(manifest)
    assert len(cat) >= 1
    # каждый уровень в манифесте должен парситься
    for lvl in cat:
        assert isinstance(lvl, LevelDef)
