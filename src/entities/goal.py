"""Цель уровня — sensor-блок, в который надо привести мяч."""
import pygame
import pymunk

from ..utils.config import BLACK, YELLOW


class Goal:
    """Прямоугольный сенсор. Не блокирует движение мяча, но детектирует касание.

    sensor=True означает, что pymunk не разрешает столкновения и не отскакивает,
    но shape_query / shapes_collide всё ещё работают.
    """

    def __init__(self, x, y, width=40, height=60, space=None):
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
        """True, если форма мяча сейчас пересекает зону цели.

        Использует Space.shape_query — Shape.shapes_collide в pymunk 7.2.0
        ассертит при отсутствии пересечения (известный баг).
        """
        space = self.body.space
        if space is None:
            return False
        for info in space.shape_query(self.shape):
            if info.shape is ball.shape:
                return True
        return False

    def draw(self, screen):
        pos = int(self.body.position.x), int(self.body.position.y)
        rect = pygame.Rect(
            pos[0] - self.width // 2,
            pos[1] - self.height // 2,
            self.width,
            self.height,
        )
        pygame.draw.rect(screen, YELLOW, rect)
        pygame.draw.rect(screen, BLACK, rect, 3)
        # «флажок» — поставить точку в центре, чтобы цель отличалась от платформ
        pygame.draw.circle(screen, BLACK, pos, 4)
