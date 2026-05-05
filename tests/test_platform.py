"""Юнит-тесты Platform: статическое тело, геометрия и материал wood."""
import pymunk
import pytest

from src.entities.platform import Platform
from src.utils.config import MATERIALS


def test_platform_has_static_body(space):
    plat = Platform(100, 100, 200, 20, space=space)
    assert plat.body.body_type == pymunk.Body.STATIC


def test_platform_position(space):
    plat = Platform(321, 654, 200, 20, space=space)
    assert plat.body.position.x == 321
    assert plat.body.position.y == 654


def test_platform_dimensions_stored(space):
    plat = Platform(0, 0, 200, 20, space=space)
    assert plat.width == 200
    assert plat.height == 20


def test_platform_uses_wood_material(space):
    plat = Platform(0, 0, 200, 20, space=space)
    wood = MATERIALS["wood"]
    assert plat.shape.elasticity == wood["elasticity"]
    assert plat.shape.friction == wood["friction"]


def test_platform_shape_is_polygon(space):
    plat = Platform(0, 0, 200, 20, space=space)
    assert isinstance(plat.shape, pymunk.Poly)


def test_platform_polygon_vertices_match_dimensions(space):
    plat = Platform(0, 0, 200, 20, space=space)
    vertices = plat.shape.get_vertices()
    assert len(vertices) == 4
    xs = [v.x for v in vertices]
    ys = [v.y for v in vertices]
    assert max(xs) - min(xs) == pytest.approx(200)
    assert max(ys) - min(ys) == pytest.approx(20)


def test_platform_registered_in_space(space):
    plat = Platform(0, 0, 200, 20, space=space)
    assert plat.shape in space.shapes


def test_platform_does_not_move_under_gravity(space):
    space.gravity = (0, 980)
    plat = Platform(100, 100, 200, 20, space=space)
    initial_position = (plat.body.position.x, plat.body.position.y)
    for _ in range(60):
        space.step(1 / 60.0)
    assert plat.body.position.x == initial_position[0]
    assert plat.body.position.y == initial_position[1]
