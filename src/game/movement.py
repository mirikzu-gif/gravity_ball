"""Применение силы движения по стрелкам.

Сила работает только когда мяч касается поверхности — в воздухе мяч
летит только по инерции (нельзя тормозить или ускоряться в воздухе).
"""
from typing import Tuple


def apply_movement_force(
    ball,
    movement: Tuple[float, float],
    on_ground: bool,
    magnitude: float,
) -> bool:
    """Применяет силу к мячу, если он на земле и направление ненулевое.

    Возвращает True, если сила была применена, иначе False.
    """
    if not on_ground:
        return False
    dx, dy = movement
    if dx == 0 and dy == 0:
        return False
    ball.apply_force((dx * magnitude, dy * magnitude))
    return True
