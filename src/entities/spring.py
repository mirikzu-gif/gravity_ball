"""Spring block: a sensor that launches the ball upward."""
import pygame
import pymunk

from ..utils import assets
from ..utils.config import BLACK


class Spring:
    """Static sensor block that applies an upward impulse on touch."""

    def __init__(self, x, y, width, height, space=None, impulse=5200.0):
        self.width = width
        self.height = height
        self.impulse = impulse
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

    def launch(self, ball) -> None:
        vx, vy = ball.body.velocity
        ball.body.velocity = (vx, min(vy, 0))
        ball.apply_impulse((0, -self.impulse))

    def draw(self, screen, sprites=None):
        pos = int(self.body.position.x), int(self.body.position.y)
        rect = pygame.Rect(
            pos[0] - self.width // 2,
            pos[1] - self.height // 2,
            self.width,
            self.height,
        )
        if sprites is None:
            sprites = assets.get_sprite_manager()

        sprite = sprites.get_scaled("spring", (int(self.width), int(self.height)))
        if sprite is not None:
            screen.blit(sprite, rect)
            return

        pygame.draw.rect(screen, (80, 220, 230), rect)
        pygame.draw.rect(screen, BLACK, rect, 3)

        left = rect.left + 8
        right = rect.right - 8
        mid_y = rect.centery
        amp = max(4, min(rect.height // 3, 10))
        points = []
        steps = 6
        for i in range(steps + 1):
            x = left + int((right - left) * i / steps)
            y = mid_y + (amp if i % 2 else -amp)
            points.append((x, y))
        if len(points) >= 2:
            pygame.draw.lines(screen, BLACK, False, points, 3)
