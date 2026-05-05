"""
Физические утилиты и функции
"""
import math
import pymunk
from .config import AIR_RESISTANCE


def is_on_ground(ball, space):
    """Проверяет, касается ли мяч поверхности"""
    # Проверяем столкновения по всему периметру мяча
    # Создаем несколько точек вокруг мяча для проверки
    check_points = []
    num_points = 8  # Проверяем 8 точек вокруг мяча
    
    for i in range(num_points):
        angle = (2 * math.pi * i) / num_points
        offset_x = math.cos(angle) * (ball.radius + 1)
        offset_y = math.sin(angle) * (ball.radius + 1)
        check_point = ball.body.position + (offset_x, offset_y)
        check_points.append(check_point)
    
    # Проверяем каждую точку на столкновения
    for point in check_points:
        point_query = space.point_query(point, 0, pymunk.ShapeFilter())
        if len(point_query) > 0:
            # Нашли столкновение, проверяем что это не сам мяч
            for query in point_query:
                if query.shape != ball.shape:
                    return True
    
    return False


def custom_velocity_func(body, gravity, damping, dt):
    """Кастомная функция скорости для реалистичной физики"""
    # Применяем гравитацию
    pymunk.Body.update_velocity(body, gravity, damping, dt)
    
    # Добавляем небольшое сопротивление воздуха
    body.velocity = body.velocity * AIR_RESISTANCE
