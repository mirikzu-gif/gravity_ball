"""Юнит-тесты класса Goal."""
import pymunk
import pytest

from src.entities.ball import Ball
from src.entities.goal import Goal


def test_goal_default_dimensions(space):
    goal = Goal(500, 300, space=space)
    assert goal.width == 40
    assert goal.height == 60


def test_goal_custom_dimensions(space):
    goal = Goal(0, 0, width=80, height=120, space=space)
    assert goal.width == 80
    assert goal.height == 120


def test_goal_position(space):
    goal = Goal(123, 456, space=space)
    assert goal.body.position.x == 123
    assert goal.body.position.y == 456


def test_goal_has_static_body(space):
    goal = Goal(0, 0, space=space)
    assert goal.body.body_type == pymunk.Body.STATIC


def test_goal_shape_is_sensor(space):
    """Sensor=True означает, что мяч проходит сквозь, но контакт регистрируется."""
    goal = Goal(0, 0, space=space)
    assert goal.shape.sensor is True


def test_goal_is_polygon(space):
    goal = Goal(0, 0, space=space)
    assert isinstance(goal.shape, pymunk.Poly)


def test_goal_registered_in_space(space):
    goal = Goal(0, 0, space=space)
    assert goal.shape in space.shapes


def test_goal_does_not_block_ball(space):
    """Мяч должен пролетать сквозь sensor."""
    space.gravity = (0, 980)
    space.damping = 1.0
    Goal(500, 300, space=space)
    ball = Ball(500, 250, space=space)

    for _ in range(60):
        space.step(1 / 60.0)

    # без sensor мяч застрял бы наверху или отскочил; с sensor — продолжает падать
    assert ball.body.position.y > 350


# ---------------------------------------------------------------------------
# is_touched_by
# ---------------------------------------------------------------------------


def test_is_touched_by_when_ball_inside(space):
    goal = Goal(500, 300, width=40, height=60, space=space)
    ball = Ball(500, 300, space=space)  # центр прямо в цели
    assert goal.is_touched_by(ball) is True


def test_is_touched_by_when_ball_far_away(space):
    goal = Goal(500, 300, width=40, height=60, space=space)
    ball = Ball(100, 100, space=space)
    assert goal.is_touched_by(ball) is False


def test_is_touched_by_at_edge_overlap(space):
    """Мяч слегка касается края цели."""
    goal = Goal(500, 300, width=40, height=60, space=space)
    # Goal extends x in [480, 520]. Мяч с центром x=540, radius=20 → правый край мяча на x=560,
    # левый край на x=520 — касается границы цели.
    ball = Ball(539, 300, space=space)
    assert goal.is_touched_by(ball) is True


def test_is_touched_by_ball_just_outside(space):
    goal = Goal(500, 300, width=40, height=60, space=space)
    # Мяч далеко от правого края (x=520+20+5=545 минимум).
    ball = Ball(560, 300, space=space)
    assert goal.is_touched_by(ball) is False
