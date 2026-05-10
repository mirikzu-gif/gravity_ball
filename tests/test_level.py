"""Тесты уровней: данные, builder, обратная совместимость create_level."""
import pymunk
import pytest

from src.entities.goal import Goal
from src.entities.obstacle import Obstacle
from src.entities.platform import Platform
from src.entities.spike import Spike
from src.entities.spring import Spring
from src.utils.config import HEIGHT, WIDTH
from src.utils.level import LEVELS, Block, LevelDef, build_level, create_level


# ---------------------------------------------------------------------------
# LEVELS — структура данных
# ---------------------------------------------------------------------------


def test_levels_is_non_empty():
    assert len(LEVELS) >= 1


@pytest.mark.parametrize("level", LEVELS, ids=[lvl.name for lvl in LEVELS])
def test_level_has_required_fields(level):
    assert isinstance(level, LevelDef)
    assert isinstance(level.name, str) and level.name
    assert len(level.ball_start) == 2
    assert all(isinstance(p, Block) for p in level.platforms)
    assert all(isinstance(o, Block) for o in level.obstacles)
    assert all(isinstance(s, Block) for s in level.springs)
    assert all(isinstance(s, Block) for s in level.spikes)
    assert isinstance(level.goal, Block)


@pytest.mark.parametrize("level", LEVELS, ids=[lvl.name for lvl in LEVELS])
def test_level_geometry_inside_world(level):
    """Старт мяча и цель внутри игрового поля."""
    bx, by = level.ball_start
    assert 0 < bx < WIDTH
    assert 0 < by < HEIGHT
    assert 0 < level.goal.x < WIDTH
    assert 0 < level.goal.y < HEIGHT


@pytest.mark.parametrize("level", LEVELS, ids=[lvl.name for lvl in LEVELS])
def test_ball_does_not_start_inside_goal(level):
    """Стартовая позиция мяча не должна сразу пересекать цель уровня."""
    ball_radius = 20
    bx, by = level.ball_start
    goal_left = level.goal.x - level.goal.width / 2 - ball_radius
    goal_right = level.goal.x + level.goal.width / 2 + ball_radius
    goal_top = level.goal.y - level.goal.height / 2 - ball_radius
    goal_bottom = level.goal.y + level.goal.height / 2 + ball_radius

    assert not (goal_left <= bx <= goal_right and goal_top <= by <= goal_bottom)


@pytest.mark.parametrize("level", LEVELS, ids=[lvl.name for lvl in LEVELS])
def test_level_block_dimensions_positive(level):
    for block in (
        *level.platforms,
        *level.obstacles,
        *level.springs,
        *level.spikes,
        level.goal,
    ):
        assert block.width > 0
        assert block.height > 0


def test_level_names_are_unique():
    names = [lvl.name for lvl in LEVELS]
    assert len(names) == len(set(names))


# ---------------------------------------------------------------------------
# build_level
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("level_index", range(len(LEVELS)))
def test_build_level_returns_correct_types(level_index, space):
    obstacles, platforms, springs, spikes, goal = build_level(space, LEVELS[level_index])
    assert all(isinstance(p, Platform) for p in platforms)
    assert all(isinstance(o, Obstacle) for o in obstacles)
    assert all(isinstance(s, Spring) for s in springs)
    assert all(isinstance(s, Spike) for s in spikes)
    assert isinstance(goal, Goal)


@pytest.mark.parametrize("level_index", range(len(LEVELS)))
def test_build_level_counts(level_index, space):
    """Количество объектов = описанию + 3 стандартные стены."""
    level = LEVELS[level_index]
    obstacles, platforms, springs, spikes, goal = build_level(space, level)

    assert len(platforms) == len(level.platforms)
    assert len(obstacles) == len(level.obstacles) + 3  # +3 стены
    assert len(springs) == len(level.springs)
    assert len(spikes) == len(level.spikes)


@pytest.mark.parametrize("level_index", range(len(LEVELS)))
def test_build_level_registers_all_shapes(level_index, space):
    obstacles, platforms, springs, spikes, goal = build_level(space, LEVELS[level_index])
    shapes = set(space.shapes)
    for p in platforms:
        assert p.shape in shapes
    for o in obstacles:
        assert o.shape in shapes
    for s in springs:
        assert s.shape in shapes
    for s in spikes:
        assert s.shape in shapes
    assert goal.shape in shapes


@pytest.mark.parametrize("level_index", range(len(LEVELS)))
def test_build_level_walls_present(level_index, space):
    obstacles, _, _, _, _ = build_level(space, LEVELS[level_index])
    walls = obstacles[-3:]
    positions = {(int(o.body.position.x), int(o.body.position.y)) for o in walls}
    assert (0, HEIGHT // 2) in positions
    assert (WIDTH, HEIGHT // 2) in positions
    assert (WIDTH // 2, HEIGHT) in positions


def test_build_level_goal_is_sensor(space):
    _, _, _, _, goal = build_level(space, LEVELS[0])
    assert goal.shape.sensor is True


# ---------------------------------------------------------------------------
# create_level — обратная совместимость
# ---------------------------------------------------------------------------


def test_create_level_returns_first_level(space):
    obstacles_a, platforms_a, springs_a, spikes_a, goal_a = create_level(space)
    space_b = pymunk.Space()
    obstacles_b, platforms_b, springs_b, spikes_b, goal_b = build_level(space_b, LEVELS[0])

    assert len(obstacles_a) == len(obstacles_b)
    assert len(platforms_a) == len(platforms_b)
    assert len(springs_a) == len(springs_b)
    assert len(spikes_a) == len(spikes_b)
    assert goal_a.body.position == goal_b.body.position
