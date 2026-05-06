"""Описание уровней и сборка их в pymunk.Space.

Уровни хранятся в levels/levels.json — массив объектов с полями
`name`, `ball_start`, `platforms`, `obstacles`, `goal`. Каждый блок
описывается четвёркой `[x, y, width, height]`.
"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple, Tuple, Union

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


def load_levels(path: Union[str, Path]) -> Tuple[LevelDef, ...]:
    """Загружает массив уровней из JSON-файла."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("корень JSON-файла уровней должен быть массивом")
    return tuple(_level_from_dict(item) for item in data)


_DEFAULT_LEVELS_PATH = (
    Path(__file__).resolve().parent.parent.parent / "levels" / "levels.json"
)

LEVELS: Tuple[LevelDef, ...] = load_levels(_DEFAULT_LEVELS_PATH)


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
