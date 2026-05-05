"""
Класс препятствия
"""
import pygame
import pymunk
from ..utils.config import MATERIALS, BLUE, BLACK


class Obstacle:
    def __init__(self, x, y, width, height, static=True, space=None):
        self.width = width
        self.height = height
        self.static = static
        self.space = space
        
        # Используем конфигурацию материалов
        material = MATERIALS['stone']
        
        if static:
            self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:
            self.body = pymunk.Body(10, pymunk.moment_for_box(10, (width, height)))
        
        self.body.position = x, y
        
        # Создаем прямоугольную форму
        vertices = [
            (-width/2, -height/2),
            (width/2, -height/2),
            (width/2, height/2),
            (-width/2, height/2)
        ]
        self.shape = pymunk.Poly(self.body, vertices)
        self.shape.elasticity = material['elasticity']
        self.shape.friction = material['friction']
        
        if space:
            space.add(self.body, self.shape)
    
    def draw(self, screen):
        """Рисует препятствие"""
        pos = int(self.body.position.x), int(self.body.position.y)
        
        # Получаем углы прямоугольника с учетом вращения
        vertices = []
        for v in self.shape.get_vertices():
            x = v.rotated(self.body.angle).x + self.body.position.x
            y = v.rotated(self.body.angle).y + self.body.position.y
            vertices.append((int(x), int(y)))
        
        pygame.draw.polygon(screen, BLUE, vertices)
        pygame.draw.polygon(screen, BLACK, vertices, 3)
