"""
Физические утилиты и функции
"""
import math
import pymunk


# Конус «низа» мяча — 60°...120° от оси X (т.е. ±30° от строго вниз).
# Контакт сбоку (стена) или сверху (потолок) больше не считается «на земле».
_GROUND_PROBE_ANGLES = (
    math.pi / 3,
    math.pi / 2,
    2 * math.pi / 3,
)


def is_on_ground(ball, space):
    """Проверяет, касается ли мяч поверхности нижней частью.

    Зондируется только нижняя треть окружности мяча — благодаря этому
    касание стены сбоку или потолка сверху не даёт ложного True.
    """
    for angle in _GROUND_PROBE_ANGLES:
        offset_x = math.cos(angle) * (ball.radius + 1)
        offset_y = math.sin(angle) * (ball.radius + 1)
        check_point = ball.body.position + (offset_x, offset_y)
        for query in space.point_query(check_point, 0, pymunk.ShapeFilter()):
            if query.shape != ball.shape and not query.shape.sensor:
                return True
    return False
