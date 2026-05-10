"""Вращательное управление мячом по стрелкам.

Крутящий момент работает только когда мяч касается поверхности — в воздухе мяч
летит только по инерции (нельзя раскручивать его для управления полётом).
"""
from typing import Tuple


def apply_roll_torque(
    ball,
    movement: Tuple[float, float],
    on_ground: bool,
    magnitude: float,
) -> bool:
    """Крутит мяч влево/вправо, если он на земле и направление ненулевое.

    Возвращает True, если сила была применена, иначе False.
    """
    if not on_ground:
        return False
    dx, _ = movement
    if dx == 0:
        return False
    ball.apply_torque(dx * magnitude * ball.radius)
    return True


def apply_movement_force(
    ball,
    movement: Tuple[float, float],
    on_ground: bool,
    magnitude: float,
) -> bool:
    """Backward-compatible alias for the old movement helper name."""
    return apply_roll_torque(ball, movement, on_ground, magnitude)
