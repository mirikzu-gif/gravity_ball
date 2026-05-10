"""Tests for the Spike entity."""
import pygame

from src.entities.ball import Ball
from src.entities.spike import Spike


class _Sprites:
    def __init__(self):
        self.scaled_calls = []

    def get_scaled(self, sprite_id, size):
        self.scaled_calls.append((sprite_id, size))
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill((200, 20, 30))
        return surface


def test_spike_shape_is_sensor(space):
    spike = Spike(100, 200, 90, 34, space)
    assert spike.shape.sensor is True


def test_spike_registered_in_space(space):
    spike = Spike(100, 200, 90, 34, space)
    assert spike.shape in space.shapes


def test_spike_detects_ball_touch(space):
    ball = Ball(100, 200, space=space)
    spike = Spike(100, 200, 90, 34, space)
    assert spike.is_touched_by(ball) is True


def test_spike_draw_does_not_crash(space):
    spike = Spike(100, 200, 90, 34, space)
    screen = pygame.Surface((240, 240))
    spike.draw(screen)


def test_spike_draw_tiles_texture_without_width_stretch(space):
    sprites = _Sprites()
    spike = Spike(120, 120, 180, 40, space)
    screen = pygame.Surface((260, 220), pygame.SRCALPHA)

    spike.draw(screen, sprites=sprites)

    assert ("spike", (24, 40)) in sprites.scaled_calls
    assert ("spike", (180, 40)) not in sprites.scaled_calls
