"""Вращательное управление мячом по стрелкам."""
from typing import Tuple


def apply_roll_torque(
    ball,
    movement: Tuple[float, float],
    on_ground: bool,
    magnitude: float,
) -> bool:
    """Крутит мяч влево/вправо, если направление ненулевое.

    `on_ground` оставлен в сигнатуре для совместимости со старым вызовом:
    теперь мяч можно раскручивать и в воздухе.
    Возвращает True, если сила была применена, иначе False.
    """
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
