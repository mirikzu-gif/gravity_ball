"""Описание уровней и сборка их в pymunk.Space.

Каждый уровень живёт в собственном JSON-файле в `levels/`. Файл
`levels/manifest.json` определяет порядок: ["start", "znakomstvo"]
→ загружаются `levels/start.json`, `levels/znakomstvo.json`.

Загрузка ленивая: `LevelCatalog` читает файл уровня только при первом
обращении (`LEVELS[i]`), чтобы не парсить все уровни на старте.
"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, NamedTuple, Tuple, Union

from ..entities.goal import Goal
from ..entities.obstacle import Obstacle
from ..entities.platform import Platform
from .config import HEIGHT, WIDTH


class Block(NamedTuple):
    """Прямоугольный блок: центр (x, y) и размеры."""
    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True)
class LevelDef:
    """Описание одного уровня. Стены добавляются автоматически builder'ом."""
    name: str
    ball_start: Tuple[float, float]
    platforms: Tuple[Block, ...]
    obstacles: Tuple[Block, ...]
    goal: Block


# ---------------------------------------------------------------------------
# JSON-загрузка
# ---------------------------------------------------------------------------


_REQUIRED_FIELDS = ("name", "ball_start", "platforms", "obstacles", "goal")


def _block_from_list(seq) -> Block:
    if len(seq) != 4:
        raise ValueError(f"блок должен иметь 4 значения [x, y, w, h], получено {seq!r}")
    return Block(*seq)


def _level_from_dict(item: dict) -> LevelDef:
    missing = [f for f in _REQUIRED_FIELDS if f not in item]
    if missing:
        raise ValueError(f"в уровне отсутствуют поля: {missing}")
    if len(item["ball_start"]) != 2:
        raise ValueError("ball_start должен быть [x, y]")
    return LevelDef(
        name=item["name"],
        ball_start=tuple(item["ball_start"]),
        platforms=tuple(_block_from_list(p) for p in item["platforms"]),
        obstacles=tuple(_block_from_list(o) for o in item["obstacles"]),
        goal=_block_from_list(item["goal"]),
    )


def load_level_file(path: Union[str, Path]) -> LevelDef:
    """Загружает один уровень из файла {name, ball_start, platforms, obstacles, goal}."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"корень файла уровня должен быть объектом, получено {type(data).__name__}")
    return _level_from_dict(data)


def load_manifest(path: Union[str, Path]) -> Tuple[str, ...]:
    """Загружает manifest.json — упорядоченный список имён уровней."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "levels" not in data:
        raise ValueError("manifest должен быть объектом с полем 'levels'")
    levels = data["levels"]
    if not isinstance(levels, list):
        raise ValueError("manifest['levels'] должен быть массивом")
    return tuple(levels)


def load_levels(path: Union[str, Path]) -> Tuple[LevelDef, ...]:
    """Загружает массив уровней из одного JSON-файла (legacy формат).

    Совместимость с прежним форматом, где все уровни лежали в одном файле-массиве.
    Сейчас не используется в продакшене — рантайм работает через LevelCatalog.
    """
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("корень JSON-файла уровней должен быть массивом")
    return tuple(_level_from_dict(item) for item in data)


class LevelCatalog:
    """Ленивая коллекция уровней.

    Парсит manifest сразу (нужно знать длину/имена), а конкретный LevelDef
    читает с диска при первом __getitem__ и кэширует.
    """

    def __init__(self, manifest_path: Union[str, Path]) -> None:
        manifest_path = Path(manifest_path)
        self._dir = manifest_path.parent
        self._names: Tuple[str, ...] = load_manifest(manifest_path)
        self._cache: Dict[int, LevelDef] = {}

    def __len__(self) -> int:
        return len(self._names)

    def __getitem__(self, index: int) -> LevelDef:
        if not 0 <= index < len(self._names):
            raise IndexError(index)
        if index not in self._cache:
            path = self._dir / f"{self._names[index]}.json"
            self._cache[index] = load_level_file(path)
        return self._cache[index]

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    @property
    def names(self) -> Tuple[str, ...]:
        return self._names

    def is_loaded(self, index: int) -> bool:
        return index in self._cache


_DEFAULT_MANIFEST_PATH = (
    Path(__file__).resolve().parent.parent.parent / "levels" / "manifest.json"
)

LEVELS: LevelCatalog = LevelCatalog(_DEFAULT_MANIFEST_PATH)


# ---------------------------------------------------------------------------
# Сборка
# ---------------------------------------------------------------------------


def _add_walls(space):
    """Стандартные стены: левая, правая, нижняя — одинаковы для всех уровней."""
    return [
        Obstacle(0, HEIGHT // 2, 10, HEIGHT, True, space),
        Obstacle(WIDTH, HEIGHT // 2, 10, HEIGHT, True, space),
        Obstacle(WIDTH // 2, HEIGHT, WIDTH, 10, True, space),
    ]


def build_level(space, level_def: LevelDef):
    """Создаёт объекты уровня в `space`. Возвращает (obstacles, platforms, goal).

    К списку obstacles добавляются стандартные стены (левая, правая, нижняя).
    """
    platforms = [
        Platform(b.x, b.y, b.width, b.height, space) for b in level_def.platforms
    ]
    obstacles = [
        Obstacle(b.x, b.y, b.width, b.height, True, space)
        for b in level_def.obstacles
    ]
    obstacles.extend(_add_walls(space))
    goal = Goal(
        level_def.goal.x,
        level_def.goal.y,
        width=level_def.goal.width,
        height=level_def.goal.height,
        space=space,
    )
    return obstacles, platforms, goal


def create_level(space):
    """Совместимость со старым API: собирает первый уровень."""
    return build_level(space, LEVELS[0])
