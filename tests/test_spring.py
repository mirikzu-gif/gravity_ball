"""Tests for the Spring entity."""
import pygame

from src.entities.ball import Ball
from src.entities.spring import Spring


def test_spring_shape_is_sensor(space):
    spring = Spring(100, 200, 90, 24, space)
    assert spring.shape.sensor is True


def test_spring_registered_in_space(space):
    spring = Spring(100, 200, 90, 24, space)
    assert spring.shape in space.shapes


def test_spring_detects_ball_touch(space):
    ball = Ball(100, 200, space=space)
    spring = Spring(100, 200, 90, 24, space)
    assert spring.is_touched_by(ball) is True


def test_spring_launch_applies_upward_impulse(space):
    ball = Ball(100, 200, space=space)
    ball.body.velocity = (0, 500)
    spring = Spring(100, 200, 90, 24, space, impulse=3000)

    spring.launch(ball)

    assert ball.body.velocity.y < 0


def test_spring_draw_does_not_crash(space):
    spring = Spring(100, 200, 90, 24, space)
    screen = pygame.Surface((240, 240))
    spring.draw(screen)
