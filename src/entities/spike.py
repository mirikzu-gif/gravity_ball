"""Spike block: a hazard sensor that restarts the current level."""
import pygame
import pymunk

from ..rendering.spike_texture import draw_spike_block


class Spike:
    """Static sensor hazard. Touching it is handled by GameScene."""

    def __init__(self, x, y, width, height, space=None):
        self.width = width
        self.height = height
        self.space = space

        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = x, y

        vertices = [
            (-width / 2, -height / 2),
            (width / 2, -height / 2),
            (width / 2, height / 2),
            (-width / 2, height / 2),
        ]
        self.shape = pymunk.Poly(self.body, vertices)
        self.shape.sensor = True

        if space:
            space.add(self.body, self.shape)

    def is_touched_by(self, ball) -> bool:
        space = self.body.space
        if space is None:
            return False
        for info in space.shape_query(self.shape):
            if info.shape is ball.shape:
                return True
        return False

    def draw(self, screen, sprites=None):
        pos = int(self.body.position.x), int(self.body.position.y)
        rect = pygame.Rect(
            pos[0] - self.width // 2,
            pos[1] - self.height // 2,
            self.width,
            self.height,
        )
        draw_spike_block(screen, rect, sprites=sprites)
