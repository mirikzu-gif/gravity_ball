"""Тесты вращательного управления мячом."""
import pytest

from src.entities.ball import Ball
from src.game.movement import apply_movement_force, apply_roll_torque


MAG = 800.0


def test_roll_torque_applied_on_ground(space):
    space.gravity = (0, 0)
    ball = Ball(100, 100, space=space)

    applied = apply_roll_torque(ball, (1.0, 0.0), on_ground=True, magnitude=MAG)
    space.step(1 / 60.0)

    assert applied is True
    assert ball.body.angular_velocity > 0


def test_roll_torque_left_and_right_have_opposite_signs(space):
    space.gravity = (0, 0)
    right = Ball(100, 100, space=space)
    left = Ball(150, 100, space=space)

    apply_roll_torque(right, (1.0, 0.0), on_ground=True, magnitude=MAG)
    apply_roll_torque(left, (-1.0, 0.0), on_ground=True, magnitude=MAG)
    space.step(1 / 60.0)

    assert right.body.angular_velocity > 0
    assert left.body.angular_velocity < 0


def test_roll_torque_applied_in_air(space):
    space.gravity = (0, 0)
    ball = Ball(100, 100, space=space)

    applied = apply_roll_torque(ball, (1.0, 0.0), on_ground=False, magnitude=MAG)
    space.step(1 / 60.0)

    assert applied is True
    assert ball.body.angular_velocity > 0


def test_zero_horizontal_movement_is_noop(space):
    space.gravity = (0, 0)
    ball = Ball(100, 100, space=space)

    applied = apply_roll_torque(ball, (0.0, 0.0), on_ground=True, magnitude=MAG)
    vertical = apply_roll_torque(ball, (0.0, -1.0), on_ground=True, magnitude=MAG)
    space.step(1 / 60.0)

    assert applied is False
    assert vertical is False
    assert ball.body.angular_velocity == pytest.approx(0)


def test_roll_torque_does_not_directly_push_ball(space):
    space.gravity = (0, 0)
    ball = Ball(100, 100, space=space)

    apply_roll_torque(ball, (1.0, 0.0), on_ground=True, magnitude=MAG)
    space.step(1 / 60.0)

    assert ball.body.velocity.x == pytest.approx(0)
    assert ball.body.velocity.y == pytest.approx(0)


def test_air_spin_does_not_push_ball(space):
    """В воздухе стрелки крутят мяч, но не толкают его по горизонтали."""
    space.gravity = (0, 0)
    ball = Ball(100, 100, space=space)
    ball.apply_impulse((100, 0))
    initial_vx = ball.body.velocity.x

    apply_roll_torque(ball, (1.0, 0.0), on_ground=False, magnitude=MAG)
    space.step(1 / 60.0)

    assert ball.body.velocity.x == pytest.approx(initial_vx)
    assert ball.body.angular_velocity > 0


def test_legacy_helper_name_uses_roll_torque(space):
    space.gravity = (0, 0)
    ball = Ball(100, 100, space=space)

    applied = apply_movement_force(ball, (1.0, 0.0), on_ground=True, magnitude=MAG)
    space.step(1 / 60.0)

    assert applied is True
    assert ball.body.angular_velocity > 0
