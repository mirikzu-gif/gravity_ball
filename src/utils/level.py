"""Описание уровней и сборка их в pymunk.Space."""
from dataclasses import dataclass
from typing import NamedTuple, Tuple

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
# Уровни
# ---------------------------------------------------------------------------


LEVELS: Tuple[LevelDef, ...] = (
    # Простой вводный уровень — мяч уже на длинной платформе, цель чуть правее.
    # Цель — быстро добраться удержанием стрелки, чтобы тестировать переход
    # между уровнями без долгого прохождения.
    LevelDef(
        name="Старт",
        ball_start=(150, 100),
        platforms=(Block(500, 620, 800, 20),),
        obstacles=(),
        goal=Block(820, 560, 40, 60),
    ),
    # «Знакомство» с настоящей геометрией — теперь финальный уровень.
    LevelDef(
        name="Знакомство",
        ball_start=(100, 100),
        platforms=(
            Block(200, 600, 300, 20),
            Block(500, 500, 200, 20),
            Block(750, 400, 250, 20),
            Block(400, 350, 150, 20),
            Block(100, 450, 180, 20),
        ),
        obstacles=(
            Block(350, 550, 40, 80),
            Block(600, 450, 60, 60),
            Block(800, 350, 50, 100),
            Block(250, 400, 40, 40),
            Block(500, 250, 80, 30),
        ),
        goal=Block(880, 350, 40, 60),
    ),
)


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
