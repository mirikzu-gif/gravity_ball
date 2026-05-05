"""Юнит-тесты Obstacle: статическое/динамическое тело и материал."""
import pymunk
import pytest

from src.entities.obstacle import Obstacle
from src.utils.config import MATERIALS


def test_static_obstacle_has_static_body(space):
    obs = Obstacle(100, 100, 40, 80, static=True, space=space)
    assert obs.body.body_type == pymunk.Body.STATIC


def test_dynamic_obstacle_has_dynamic_body(space):
    obs = Obstacle(100, 100, 40, 80, static=False, space=space)
    assert obs.body.body_type == pymunk.Body.DYNAMIC


def test_obstacle_position(space):
    obs = Obstacle(123, 456, 40, 80, static=True, space=space)
    assert obs.body.position.x == 123
    assert obs.body.position.y == 456


def test_obstacle_dimensions_stored(space):
    obs = Obstacle(0, 0, 40, 80, static=True, space=space)
    assert obs.width == 40
    assert obs.height == 80


def test_obstacle_uses_stone_material(space):
    obs = Obstacle(0, 0, 40, 80, static=True, space=space)
    stone = MATERIALS["stone"]
    assert obs.shape.elasticity == stone["elasticity"]
    assert obs.shape.friction == stone["friction"]


def test_obstacle_shape_is_polygon(space):
    obs = Obstacle(0, 0, 40, 80, static=True, space=space)
    assert isinstance(obs.shape, pymunk.Poly)


def test_obstacle_polygon_vertices_match_dimensions(space):
    obs = Obstacle(0, 0, 40, 80, static=True, space=space)
    vertices = obs.shape.get_vertices()
    assert len(vertices) == 4
    xs = [v.x for v in vertices]
    ys = [v.y for v in vertices]
    assert max(xs) - min(xs) == pytest.approx(40)
    assert max(ys) - min(ys) == pytest.approx(80)


def test_obstacle_registered_in_space(space):
    obs = Obstacle(0, 0, 40, 80, static=True, space=space)
    assert obs.body in space.bodies or obs.body in space.static_body  # static обрабатывается отдельно
    assert obs.shape in space.shapes


def test_static_attribute(space):
    static_obs = Obstacle(0, 0, 40, 80, static=True, space=space)
    dynamic_obs = Obstacle(0, 0, 40, 80, static=False, space=space)
    assert static_obs.static is True
    assert dynamic_obs.static is False


def test_dynamic_obstacle_has_positive_mass(space):
    obs = Obstacle(0, 0, 40, 80, static=False, space=space)
    assert obs.body.mass > 0
    assert obs.body.moment > 0


def test_static_obstacle_does_not_fall_under_gravity(space):
    space.gravity = (0, 980)
    obs = Obstacle(100, 100, 40, 80, static=True, space=space)
    initial_y = obs.body.position.y
    for _ in range(60):
        space.step(1 / 60.0)
    assert obs.body.position.y == initial_y
