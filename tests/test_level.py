"""Юнит-тесты создания уровня."""
from src.entities.obstacle import Obstacle
from src.entities.platform import Platform
from src.utils.level import create_level


EXPECTED_PLATFORMS = 5
# 5 препятствий + 3 стены (левая, правая, нижняя)
EXPECTED_OBSTACLES = 8


def test_create_level_returns_two_lists(space):
    obstacles, platforms = create_level(space)
    assert isinstance(obstacles, list)
    assert isinstance(platforms, list)


def test_create_level_platform_count(space):
    obstacles, platforms = create_level(space)
    assert len(platforms) == EXPECTED_PLATFORMS


def test_create_level_obstacle_count(space):
    obstacles, platforms = create_level(space)
    assert len(obstacles) == EXPECTED_OBSTACLES


def test_create_level_returns_correct_types(space):
    obstacles, platforms = create_level(space)
    assert all(isinstance(p, Platform) for p in platforms)
    assert all(isinstance(o, Obstacle) for o in obstacles)


def test_create_level_registers_all_shapes_in_space(space):
    obstacles, platforms = create_level(space)
    space_shapes = set(space.shapes)
    for p in platforms:
        assert p.shape in space_shapes
    for o in obstacles:
        assert o.shape in space_shapes


def test_create_level_total_shapes(space):
    obstacles, platforms = create_level(space)
    assert len(space.shapes) == EXPECTED_PLATFORMS + EXPECTED_OBSTACLES


def test_create_level_all_obstacles_static(space):
    import pymunk

    obstacles, _ = create_level(space)
    for o in obstacles:
        assert o.body.body_type == pymunk.Body.STATIC


def test_create_level_walls_present(space):
    """Последние 3 obstacle — это стены: левая (x=0), правая (x=WIDTH), нижняя (y=HEIGHT)."""
    from src.utils.config import WIDTH, HEIGHT

    obstacles, _ = create_level(space)
    walls = obstacles[-3:]
    positions = {(int(o.body.position.x), int(o.body.position.y)) for o in walls}
    assert (0, HEIGHT // 2) in positions
    assert (WIDTH, HEIGHT // 2) in positions
    assert (WIDTH // 2, HEIGHT) in positions


def test_create_level_idempotent_for_fresh_space(space):
    """Повторный вызов с новым space даёт ту же геометрию."""
    import pymunk

    obstacles_a, platforms_a = create_level(space)

    space_b = pymunk.Space()
    obstacles_b, platforms_b = create_level(space_b)

    assert len(obstacles_a) == len(obstacles_b)
    assert len(platforms_a) == len(platforms_b)
    for a, b in zip(platforms_a, platforms_b):
        assert a.body.position == b.body.position
        assert a.width == b.width
        assert a.height == b.height
