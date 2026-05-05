"""Тесты apply_movement_force — гейтинг по on_ground."""
import pytest

from src.entities.ball import Ball
from src.game.movement import apply_movement_force


MAG = 800.0


def test_force_applied_on_ground(space):
    space.gravity = (0, 0)
    ball = Ball(100, 100, space=space)

    applied = apply_movement_force(ball, (1.0, 0.0), on_ground=True, magnitude=MAG)
    space.step(1 / 60.0)

    assert applied is True
    assert ball.body.velocity.x > 0


def test_no_force_in_air(space):
    """Главное поведение фикса: в воздухе стрелки не двигают мяч."""
    space.gravity = (0, 0)
    ball = Ball(100, 100, space=space)
    initial_vx = ball.body.velocity.x

    applied = apply_movement_force(ball, (1.0, 0.0), on_ground=False, magnitude=MAG)
    space.step(1 / 60.0)

    assert applied is False
    assert ball.body.velocity.x == pytest.approx(initial_vx)


def test_zero_movement_is_noop(space):
    space.gravity = (0, 0)
    ball = Ball(100, 100, space=space)

    applied = apply_movement_force(ball, (0.0, 0.0), on_ground=True, magnitude=MAG)
    space.step(1 / 60.0)

    assert applied is False
    assert ball.body.velocity.x == pytest.approx(0)
    assert ball.body.velocity.y == pytest.approx(0)


@pytest.mark.parametrize(
    "movement,axis,direction",
    [
        ((1.0, 0.0), "x", 1),
        ((-1.0, 0.0), "x", -1),
        ((0.0, 1.0), "y", 1),
        ((0.0, -1.0), "y", -1),
    ],
)
def test_force_direction_when_on_ground(space, movement, axis, direction):
    space.gravity = (0, 0)
    ball = Ball(100, 100, space=space)

    apply_movement_force(ball, movement, on_ground=True, magnitude=MAG)
    space.step(1 / 60.0)

    velocity_component = getattr(ball.body.velocity, axis)
    assert velocity_component * direction > 0


def test_inertia_preserved_in_air(space):
    """Если мяч уже движется и оторвался — он продолжает лететь по инерции,
    стрелки в воздухе не могут его ни ускорить, ни затормозить."""
    space.gravity = (0, 0)
    ball = Ball(100, 100, space=space)
    ball.apply_impulse((100, 0))  # даём начальный импульс
    initial_vx = ball.body.velocity.x

    # пытаемся ускорить в воздухе
    apply_movement_force(ball, (1.0, 0.0), on_ground=False, magnitude=MAG)
    # пытаемся затормозить в воздухе
    apply_movement_force(ball, (-1.0, 0.0), on_ground=False, magnitude=MAG)
    space.step(1 / 60.0)

    # без сил velocity не должна вырасти, только AIR_RESISTANCE из custom_velocity_func
    # должна была чуть уменьшить её — то есть |vx| ≤ |initial_vx|
    assert abs(ball.body.velocity.x) <= abs(initial_vx)


def test_diagonal_movement_on_ground(space):
    space.gravity = (0, 0)
    ball = Ball(100, 100, space=space)

    apply_movement_force(ball, (1.0, -1.0), on_ground=True, magnitude=MAG)
    space.step(1 / 60.0)

    assert ball.body.velocity.x > 0
    assert ball.body.velocity.y < 0
