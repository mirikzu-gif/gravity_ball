"""Интеграционные тесты отскока мяча от поверхностей.

Используется детерминированный pymunk.Space с фиксированным dt=1/60.
"""
import pymunk
import pytest

from src.entities.ball import Ball
from src.entities.obstacle import Obstacle
from src.entities.platform import Platform
from src.utils.config import GRAVITY, MATERIALS


DT = 1 / 60.0


def _new_space():
    sp = pymunk.Space()
    sp.gravity = GRAVITY
    return sp


def _simulate_drop(make_floor, steps=300, ball_y=100):
    """Бросает мяч с указанной высоты, возвращает (max_upward_velocity, min_y_after_contact, final_y)."""
    sp = _new_space()
    ball = Ball(500, ball_y, space=sp)
    make_floor(sp)

    max_upward = 0.0  # минимальное (наиболее отрицательное) vy
    min_y_after_contact = ball.body.position.y
    contacted = False

    for _ in range(steps):
        sp.step(DT)
        if ball.body.position.y > 500:  # мяч прошёл значительное расстояние вниз
            contacted = True
        if contacted:
            max_upward = min(max_upward, ball.body.velocity.y)
            min_y_after_contact = min(min_y_after_contact, ball.body.position.y)

    return abs(max_upward), min_y_after_contact, ball.body.position.y


# ---------------------------------------------------------------------------
# Базовый отскок
# ---------------------------------------------------------------------------


def test_ball_bounces_off_static_obstacle():
    """После падения на камень мяч получает заметную скорость вверх."""
    max_up, _, _ = _simulate_drop(
        lambda sp: Obstacle(500, 600, 400, 20, static=True, space=sp)
    )
    assert max_up > 50, f"ожидалась скорость отскока > 50, получено {max_up}"


def test_ball_bounces_off_platform():
    """После падения на деревянную платформу мяч отскакивает."""
    max_up, _, _ = _simulate_drop(
        lambda sp: Platform(500, 600, 400, 20, space=sp)
    )
    assert max_up > 50


# ---------------------------------------------------------------------------
# Закон сохранения энергии: отскок не выше начальной высоты
# ---------------------------------------------------------------------------


def test_bounce_does_not_exceed_initial_height_stone():
    """Combined elasticity stone+ball = 0.45 < 1 — отскок не возвращает мяч на старт."""
    initial_y = 100
    _, min_y, _ = _simulate_drop(
        lambda sp: Obstacle(500, 600, 400, 20, static=True, space=sp),
        ball_y=initial_y,
    )
    assert min_y >= initial_y, (
        f"мяч отскочил выше точки старта: {min_y} < {initial_y} "
        "(возможно elasticity > 1 без учёта потерь)"
    )


def test_bounce_does_not_exceed_initial_height_wood():
    """Combined elasticity wood+ball = 0.75 < 1 — отскок ниже точки старта."""
    initial_y = 100
    _, min_y, _ = _simulate_drop(
        lambda sp: Platform(500, 600, 400, 20, space=sp),
        ball_y=initial_y,
    )
    assert min_y >= initial_y


# ---------------------------------------------------------------------------
# Сравнение материалов: дерево упруже камня
# ---------------------------------------------------------------------------


def test_wood_bounces_higher_than_stone():
    """Дерево (elasticity 0.5) даёт более высокий отскок чем камень (elasticity 0.3)."""
    stone_max_v, _, _ = _simulate_drop(
        lambda sp: Obstacle(500, 600, 400, 20, static=True, space=sp)
    )
    wood_max_v, _, _ = _simulate_drop(
        lambda sp: Platform(500, 600, 400, 20, space=sp)
    )
    assert wood_max_v > stone_max_v, (
        f"wood {wood_max_v:.1f} should > stone {stone_max_v:.1f}"
    )


def test_material_constants_consistency():
    """Зависимость теста выше: предполагает elasticity wood > elasticity stone."""
    assert MATERIALS["wood"]["elasticity"] > MATERIALS["stone"]["elasticity"]


# ---------------------------------------------------------------------------
# Затухание: серия отскоков убывает
# ---------------------------------------------------------------------------


def test_bounce_energy_decays_over_time():
    """Каждый последующий отскок имеет меньшую амплитуду скорости."""
    sp = _new_space()
    ball = Ball(500, 100, space=sp)
    Obstacle(500, 600, 400, 20, static=True, space=sp)

    upward_peaks = []
    in_upward_phase = False
    current_peak = 0.0

    for _ in range(600):  # 10 секунд
        sp.step(DT)
        vy = ball.body.velocity.y
        if vy < -10:  # летит вверх
            if not in_upward_phase:
                in_upward_phase = True
                current_peak = abs(vy)
            else:
                current_peak = max(current_peak, abs(vy))
        else:  # летит вниз или почти стоит
            if in_upward_phase:
                upward_peaks.append(current_peak)
                in_upward_phase = False
                current_peak = 0.0

    # должно быть как минимум 2 отскока
    assert len(upward_peaks) >= 2, f"ожидалось ≥2 отскоков, получено {len(upward_peaks)}"
    # каждый последующий — меньше предыдущего
    for prev, curr in zip(upward_peaks, upward_peaks[1:]):
        assert curr < prev, f"отскоки не затухают: {upward_peaks}"


# ---------------------------------------------------------------------------
# Стабилизация: мяч в итоге останавливается на полу
# ---------------------------------------------------------------------------


def test_ball_eventually_settles_on_floor():
    """После достаточного времени мяч лежит на полу с малой скоростью."""
    sp = _new_space()
    ball = Ball(500, 100, space=sp)
    # пол достаточно широкий
    Obstacle(500, 680, 800, 20, static=True, space=sp)

    for _ in range(1200):  # 20 секунд
        sp.step(DT)

    assert abs(ball.body.velocity.y) < 5
    # мяч у пола (центр в районе y=650)
    assert 600 < ball.body.position.y < 680


# ---------------------------------------------------------------------------
# Без поверхности — мяч уходит в бесконечность
# ---------------------------------------------------------------------------


def test_ball_falls_indefinitely_without_floor():
    """Без пола мяч продолжает падать."""
    sp = _new_space()
    ball = Ball(500, 100, space=sp)

    for _ in range(60):
        sp.step(DT)
    y_after_1s = ball.body.position.y

    for _ in range(60):
        sp.step(DT)
    y_after_2s = ball.body.position.y

    assert y_after_2s > y_after_1s
    assert ball.body.velocity.y > 0
