"""Юнит-тесты физических утилит: is_on_ground и custom_velocity_func."""
import math

import pymunk
import pytest

from src.entities.ball import Ball
from src.entities.obstacle import Obstacle
from src.entities.platform import Platform
from src.utils.config import AIR_RESISTANCE
from src.utils.physics import custom_velocity_func, is_on_ground


# ---------------------------------------------------------------------------
# is_on_ground
# ---------------------------------------------------------------------------


def test_is_on_ground_alone_in_space_returns_false(space):
    """Мяч сам по себе (без других shape) не считается «на земле»."""
    ball = Ball(500, 100, space=space)
    assert is_on_ground(ball, space) is False


def test_is_on_ground_high_in_air_returns_false(space):
    """Мяч высоко над платформой — не на земле."""
    ball = Ball(500, 100, space=space)
    Platform(500, 600, 200, 20, space=space)
    assert is_on_ground(ball, space) is False


def test_is_on_ground_resting_on_platform_returns_true(space):
    """Мяч прямо на платформе — на земле."""
    Platform(500, 600, 200, 20, space=space)
    # Платформа: центр y=600, верх y=590. Мяч радиуса 20 центром в y=580 →
    # точка проверки снизу (radius+1=21) попадает в y=601 — внутри платформы.
    ball = Ball(500, 580, space=space)
    assert is_on_ground(ball, space) is True


def test_is_on_ground_touching_wall_returns_true(space):
    """Текущая реализация считает «на земле» любой контакт, в т.ч. со стеной сбоку.

    Этот тест фиксирует существующее поведение — если оно изменится при рефакторинге,
    тест осознанно упадёт.
    """
    # Вертикальная стена: центр (0, 350), 10×700 → x ∈ [-5, 5], y ∈ [0, 700]
    Obstacle(0, 350, 10, 700, static=True, space=space)
    # Мяч с центром x=21 — левая контрольная точка x=0, y=100 внутри стены.
    ball = Ball(21, 100, space=space)
    assert is_on_ground(ball, space) is True


def test_is_on_ground_ignores_own_shape(space):
    """Если бы функция не отфильтровывала собственную shape мяча, она бы всегда возвращала True."""
    ball = Ball(500, 100, space=space)
    # Без других объектов — ровно случай, когда мяч мог бы «найти сам себя».
    # Текущая реализация фильтрует — должна вернуть False.
    assert is_on_ground(ball, space) is False


def test_is_on_ground_just_above_surface_returns_false(space):
    """Мяч на 5px выше платформы — ещё не на земле."""
    Platform(500, 600, 200, 20, space=space)
    # Верх платформы y=590, мяч с центром y=569 → нижняя точка y=569+21=590 — край.
    # Берём с запасом: центр y=550, нижняя точка y=571.
    ball = Ball(500, 550, space=space)
    assert is_on_ground(ball, space) is False


# ---------------------------------------------------------------------------
# custom_velocity_func
# ---------------------------------------------------------------------------


def _make_test_body(space, velocity=(0, 0)):
    body = pymunk.Body(1.0, pymunk.moment_for_circle(1.0, 0, 5))
    body.position = (0, 0)
    body.velocity = velocity
    body.velocity_func = custom_velocity_func
    shape = pymunk.Circle(body, 5)
    space.add(body, shape)
    return body


def test_custom_velocity_func_applies_air_resistance(space):
    """Без гравитации скорость падает геометрически с коэффициентом AIR_RESISTANCE."""
    space.gravity = (0, 0)
    space.damping = 1.0
    body = _make_test_body(space, velocity=(100, 0))

    n_steps = 10
    dt = 1 / 60.0
    for _ in range(n_steps):
        space.step(dt)

    expected = 100 * (AIR_RESISTANCE ** n_steps)
    assert body.velocity.x == pytest.approx(expected, rel=1e-6)


def test_custom_velocity_func_applies_gravity(space):
    """С гравитацией и нулевой начальной скоростью тело набирает скорость вниз."""
    space.gravity = (0, 980)
    space.damping = 1.0
    body = _make_test_body(space, velocity=(0, 0))

    space.step(1 / 60.0)

    # update_velocity: vy = 0 + 980 * (1/60) ≈ 16.33
    # затем * AIR_RESISTANCE = 0.99 → ≈ 16.17
    expected = 980 * (1 / 60.0) * AIR_RESISTANCE
    assert body.velocity.y == pytest.approx(expected, rel=1e-3)


def test_custom_velocity_func_horizontal_decays(space):
    """Горизонтальная скорость не растёт со временем (только убывает)."""
    space.gravity = (0, 980)
    space.damping = 1.0
    body = _make_test_body(space, velocity=(200, 0))

    history = []
    for _ in range(60):
        space.step(1 / 60.0)
        history.append(body.velocity.x)

    # монотонное убывание
    for prev, curr in zip(history, history[1:]):
        assert curr < prev
    assert history[-1] < 200


def test_custom_velocity_func_does_not_affect_static_bodies(space):
    """Статические тела не имеют velocity_func — проверяем что функция к ним не применяется."""
    space.gravity = (0, 980)
    plat = Platform(100, 100, 200, 20, space=space)
    initial = (plat.body.position.x, plat.body.position.y)

    for _ in range(60):
        space.step(1 / 60.0)

    assert plat.body.position.x == initial[0]
    assert plat.body.position.y == initial[1]


def test_custom_velocity_func_signature_matches_pymunk():
    """Сигнатура совместима с pymunk: (body, gravity, damping, dt)."""
    body = pymunk.Body(1.0, pymunk.moment_for_circle(1.0, 0, 5))
    body.velocity = (10, 0)
    custom_velocity_func(body, (0, 0), 1.0, 1 / 60.0)
    # Должна примениться только air resistance — гравитация 0, damping 1.
    assert body.velocity.x == pytest.approx(10 * AIR_RESISTANCE)


# ---------------------------------------------------------------------------
# Интеграция: мяч + поверхность + гравитация
# ---------------------------------------------------------------------------


def test_ball_falls_under_gravity(space):
    space.gravity = (0, 980)
    ball = Ball(500, 100, space=space)
    initial_y = ball.body.position.y

    for _ in range(30):
        space.step(1 / 60.0)

    assert ball.body.position.y > initial_y
    assert ball.body.velocity.y > 0
