"""
Класс платформы
"""
import pygame
import pymunk
from ..utils import assets
from ..utils.config import MATERIALS, GREEN, BLACK


class Platform:
    def __init__(self, x, y, width, height, space=None):
        self.width = width
        self.height = height
        self.space = space
        
        # Используем конфигурацию материалов
        material = MATERIALS['wood']
        
        # Создаем статическую платформу
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = x, y
        
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
    
    def draw(self, screen, sprites=None):
        """Рисует платформу"""
        pos = int(self.body.position.x), int(self.body.position.y)
        rect = pygame.Rect(
            pos[0] - self.width // 2,
            pos[1] - self.height // 2,
            self.width,
            self.height,
        )
        if sprites is None:
            sprites = assets.get_sprite_manager()

        sprite = sprites.get_tiled("platform", (int(self.width), int(self.height)))
        if sprite is not None:
            screen.blit(sprite, rect)
            pygame.draw.rect(screen, BLACK, rect, 3)
            return

        pygame.draw.rect(screen, GREEN, rect)
        pygame.draw.rect(screen, BLACK, rect, 3)
