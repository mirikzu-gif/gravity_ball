"""Юнит-тесты Ball: инициализация, регистрация в Space и apply_force."""
import pymunk
import pytest

from src.entities.ball import Ball
from src.utils.config import MATERIALS


def test_ball_default_radius(space):
    ball = Ball(100, 200, space=space)
    assert ball.radius == 20


def test_ball_custom_radius(space):
    ball = Ball(0, 0, radius=42, space=space)
    assert ball.radius == 42


def test_ball_position(space):
    ball = Ball(150, 250, space=space)
    assert ball.body.position.x == 150
    assert ball.body.position.y == 250


def test_ball_uses_material_properties(space):
    ball = Ball(0, 0, space=space)
    material = MATERIALS["ball"]
    assert ball.mass == material["mass"]
    assert ball.elasticity == material["elasticity"]
    assert ball.shape.elasticity == material["elasticity"]
    assert ball.shape.friction == material["friction"]


def test_ball_body_mass_matches_material(space):
    ball = Ball(0, 0, space=space)
    assert ball.body.mass == MATERIALS["ball"]["mass"]


def test_ball_shape_is_circle(space):
    ball = Ball(0, 0, radius=15, space=space)
    assert isinstance(ball.shape, pymunk.Circle)
    assert ball.shape.radius == 15


def test_ball_registered_in_space(space):
    ball = Ball(0, 0, space=space)
    assert ball.body in space.bodies
    assert ball.shape in space.shapes


def test_ball_without_space_is_not_registered():
    ball = Ball(0, 0, space=None)
    assert ball.body is not None
    assert ball.shape is not None


def test_ball_has_custom_velocity_func(space):
    from src.utils.physics import custom_velocity_func

    ball = Ball(0, 0, space=space)
    assert ball.body.velocity_func is custom_velocity_func


def test_apply_force_changes_velocity(space):
    space.gravity = (0, 0)  # отключаем гравитацию для чистоты теста
    ball = Ball(100, 100, space=space)
    initial_velocity = pymunk.Vec2d(*ball.body.velocity)

    ball.apply_force((1000, 0))
    space.step(1 / 60.0)

    assert ball.body.velocity.x > initial_velocity.x


@pytest.mark.parametrize(
    "force,axis,direction",
    [
        ((1000, 0), "x", 1),
        ((-1000, 0), "x", -1),
        ((0, 1000), "y", 1),
        ((0, -1000), "y", -1),
    ],
)
def test_apply_force_direction(space, force, axis, direction):
    space.gravity = (0, 0)
    ball = Ball(100, 100, space=space)

    ball.apply_force(force)
    space.step(1 / 60.0)

    velocity_component = getattr(ball.body.velocity, axis)
    assert velocity_component * direction > 0


def test_moment_of_inertia_is_positive(space):
    ball = Ball(0, 0, space=space)
    assert ball.body.moment > 0
