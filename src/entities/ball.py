"""
Класс мяча
"""
import pygame
import pymunk
from ..utils.config import MATERIALS, RED, BLACK


class Ball:
    def __init__(self, x, y, radius=20, space=None):
        self.radius = radius
        self.space = space

        material = MATERIALS['ball']
        self.mass = material['mass']
        self.elasticity = material['elasticity']

        moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, moment)
        self.body.position = x, y

        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = self.elasticity
        self.shape.friction = material['friction']

        if space:
            space.add(self.body, self.shape)
        
    def apply_force(self, force):
        """Применяет силу к мячу (действует один шаг space.step)."""
        self.body.apply_force_at_world_point(force, self.body.position)

    def apply_impulse(self, impulse):
        """Применяет мгновенный импульс — изменяет velocity сразу, не зависит от dt."""
        self.body.apply_impulse_at_world_point(impulse, self.body.position)

    def draw(self, screen, position=None):
        """Рисует мяч. position позволяет передать интерполированную позицию для рендера."""
        if position is None:
            position = self.body.position
        pos = int(position[0]), int(position[1])
        pygame.draw.circle(screen, RED, pos, self.radius)
        pygame.draw.circle(screen, BLACK, pos, self.radius, 2)
