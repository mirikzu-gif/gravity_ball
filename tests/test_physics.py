"""Юнит-тесты is_on_ground и интеграции с pymunk-физикой."""
import pymunk
import pytest

from src.entities.ball import Ball
from src.entities.goal import Goal
from src.entities.obstacle import Obstacle
from src.entities.platform import Platform
from src.entities.spike import Spike
from src.entities.spring import Spring
from src.utils.physics import is_on_ground


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


def test_is_on_ground_touching_wall_side_returns_false(space):
    """Касание стены сбоку не должно считаться «на земле» — иначе можно прыгать у стены."""
    # Вертикальная стена: центр (0, 350), 10×700 → x ∈ [-5, 5], y ∈ [0, 700]
    Obstacle(0, 350, 10, 700, static=True, space=space)
    # Мяч в воздухе вплотную к стене слева.
    ball = Ball(21, 100, space=space)
    assert is_on_ground(ball, space) is False


def test_is_on_ground_touching_ceiling_returns_false(space):
    """Касание потолка сверху не считается «на земле»."""
    # Потолок: горизонтальная плита прямо над мячом.
    Obstacle(500, 100, 400, 20, static=True, space=space)
    # Мяч под потолком: его верхушка в потолке, а низ — в воздухе.
    ball = Ball(500, 130, space=space)
    assert is_on_ground(ball, space) is False


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


@pytest.mark.parametrize(
    "factory",
    [
        lambda space: Spring(500, 601, 200, 20, space=space),
        lambda space: Spike(500, 601, 200, 20, space=space),
        lambda space: Goal(500, 601, 200, 20, space=space),
    ],
)
def test_is_on_ground_ignores_sensor_shapes(space, factory):
    """Сенсоры цели/пружин/шипов не должны разрешать зарядку прыжка."""
    ball = Ball(500, 580, space=space)
    factory(space)
    assert is_on_ground(ball, space) is False


# ---------------------------------------------------------------------------
# Затухание через space.damping (pymunk per-second damping)
# ---------------------------------------------------------------------------


def test_space_damping_decays_horizontal_velocity(space):
    """С damping<1 горизонтальная скорость убывает со временем."""
    space.gravity = (0, 0)
    space.damping = 0.5
    ball = Ball(0, 0, space=space)
    ball.body.velocity = (200, 0)

    history = []
    for _ in range(60):
        space.step(1 / 60.0)
        history.append(ball.body.velocity.x)

    for prev, curr in zip(history, history[1:]):
        assert curr < prev
    assert history[-1] < 200


def test_space_damping_one_does_not_decay(space):
    """damping=1.0 — затухания нет."""
    space.gravity = (0, 0)
    space.damping = 1.0
    ball = Ball(0, 0, space=space)
    ball.body.velocity = (100, 0)

    for _ in range(60):
        space.step(1 / 60.0)

    assert ball.body.velocity.x == pytest.approx(100, rel=1e-6)


# ---------------------------------------------------------------------------
# Интеграция: мяч + гравитация
# ---------------------------------------------------------------------------


def test_ball_falls_under_gravity(space):
    space.gravity = (0, 980)
    ball = Ball(500, 100, space=space)
    initial_y = ball.body.position.y

    for _ in range(30):
        space.step(1 / 60.0)

    assert ball.body.position.y > initial_y
    assert ball.body.velocity.y > 0
