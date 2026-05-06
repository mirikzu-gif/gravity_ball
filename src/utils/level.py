"""
Утилиты для создания уровней
"""
from ..entities.goal import Goal
from ..entities.obstacle import Obstacle
from ..entities.platform import Platform
from ..utils.config import HEIGHT, WIDTH


def create_level(space):
    """Создает уровень: возвращает (obstacles, platforms, goal)."""
    obstacles = []
    platforms = []

    # Платформы
    platforms.append(Platform(200, 600, 300, 20, space))
    platforms.append(Platform(500, 500, 200, 20, space))
    platforms.append(Platform(750, 400, 250, 20, space))
    platforms.append(Platform(400, 350, 150, 20, space))
    platforms.append(Platform(100, 450, 180, 20, space))

    # Препятствия
    obstacles.append(Obstacle(350, 550, 40, 80, True, space))
    obstacles.append(Obstacle(600, 450, 60, 60, True, space))
    obstacles.append(Obstacle(800, 350, 50, 100, True, space))
    obstacles.append(Obstacle(250, 400, 40, 40, True, space))
    obstacles.append(Obstacle(500, 250, 80, 30, True, space))

    # Стены
    obstacles.append(Obstacle(0, HEIGHT // 2, 10, HEIGHT, True, space))
    obstacles.append(Obstacle(WIDTH, HEIGHT // 2, 10, HEIGHT, True, space))
    obstacles.append(Obstacle(WIDTH // 2, HEIGHT, WIDTH, 10, True, space))

    # Цель — над верхней правой платформой
    goal = Goal(880, 350, width=40, height=60, space=space)

    return obstacles, platforms, goal
