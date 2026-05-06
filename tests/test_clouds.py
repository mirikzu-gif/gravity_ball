"""Тесты декоративных облаков."""
import pygame
import pytest

from src.scenes.clouds import Cloud, generate_clouds
from src.utils.config import WIDTH


def test_cloud_moves_with_velocity():
    cloud = Cloud(x=500, y=100, scale=1.0, speed=-50)
    cloud.update(1.0)
    assert cloud.x == 450


def test_cloud_wraps_around_when_off_left():
    cloud = Cloud(x=-200, y=100, scale=1.0, speed=-30)
    cloud.update(0.1)  # ушло ещё дальше влево, должно перенестись вправо
    assert cloud.x > WIDTH


def test_cloud_does_not_wrap_when_partially_visible():
    """Если правый край облака ещё на экране, оно не должно прыгать."""
    cloud = Cloud(x=-50, y=100, scale=1.0, speed=-1)
    cloud.update(0.01)
    # x ≈ -50.01, правый край ≈ 30 → ещё видно → не переносим
    assert cloud.x < 0


def test_cloud_draw_does_not_crash():
    screen = pygame.Surface((1000, 700))
    cloud = Cloud(x=500, y=100, scale=1.0, speed=-30)
    cloud.draw(screen, (255, 255, 255))


def test_generate_clouds_returns_requested_count():
    clouds = generate_clouds(count=10)
    assert len(clouds) == 10


def test_generate_clouds_is_deterministic():
    a = generate_clouds(seed=123)
    b = generate_clouds(seed=123)
    for ca, cb in zip(a, b):
        assert ca.x == cb.x
        assert ca.y == cb.y
        assert ca.scale == cb.scale
        assert ca.speed == cb.speed


def test_generate_clouds_different_seeds_differ():
    a = generate_clouds(seed=1)
    b = generate_clouds(seed=2)
    # хотя бы одно облако отличается
    diffs = [(ca.x, ca.y) != (cb.x, cb.y) for ca, cb in zip(a, b)]
    assert any(diffs)


def test_clouds_move_left():
    """Все облака движутся влево (отрицательная скорость)."""
    for c in generate_clouds():
        assert c.speed < 0


@pytest.mark.parametrize("scale", [0.4, 0.7, 1.0])
def test_smaller_clouds_move_slower_in_parallax(scale):
    """Параллакс: |speed| пропорционально scale."""
    # Все облака с одним seed дают разные позиции, но одна закономерность:
    # |speed| ≈ base * scale → удвоение масштаба удваивает скорость.
    rng_clouds = generate_clouds(seed=42)
    speeds_by_scale = sorted((c.scale, abs(c.speed)) for c in rng_clouds)
    # маленький scale → меньшая |speed|, в среднем
    avg_small = sum(s for sc, s in speeds_by_scale[:2]) / 2
    avg_big = sum(s for sc, s in speeds_by_scale[-2:]) / 2
    assert avg_big > avg_small