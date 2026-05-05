"""Контроллер прыжка с явной state-машиной.

Не зависит от pygame и pymunk — принимает on_ground как параметр.
Тесты должны покрывать все переходы и формулу силы.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class JumpState(Enum):
    IDLE = "idle"
    CHARGING = "charging"


@dataclass(frozen=True)
class JumpEvent:
    """Возвращается контроллером, когда нужно применить силу прыжка к мячу."""
    force: Tuple[float, float]


class JumpController:
    """State-машина зарядки и выполнения прыжка.

    Состояния: IDLE ↔ CHARGING.
    Внешние события: press(), release(), update(dt). Все принимают on_ground.

    Сила прыжка: JUMP_FORCE * (min_factor + (1 - min_factor) * charge_ratio),
    где charge_ratio = min(charge_time / max_charge_time, 1.0).
    """

    def __init__(
        self,
        max_charge_time: float,
        jump_force: float,
        min_factor: float = 0.3,
    ):
        if max_charge_time <= 0:
            raise ValueError("max_charge_time must be positive")
        if jump_force <= 0:
            raise ValueError("jump_force must be positive")
        if not 0.0 <= min_factor <= 1.0:
            raise ValueError("min_factor must be in [0, 1]")

        self.max_charge_time = max_charge_time
        self.jump_force = jump_force
        self.min_factor = min_factor

        self._state = JumpState.IDLE
        self._charge_time = 0.0
        self._space_pressed = False

    # ------------------------------------------------------------------
    # Свойства состояния
    # ------------------------------------------------------------------
    @property
    def state(self) -> JumpState:
        return self._state

    @property
    def is_charging(self) -> bool:
        return self._state == JumpState.CHARGING

    @property
    def charge_time(self) -> float:
        return self._charge_time

    @property
    def charge_ratio(self) -> float:
        """Нормализованная зарядка в [0, 1]."""
        return min(self._charge_time / self.max_charge_time, 1.0)

    @property
    def space_pressed(self) -> bool:
        return self._space_pressed

    # ------------------------------------------------------------------
    # События
    # ------------------------------------------------------------------
    def press(self, *, on_ground: bool) -> None:
        """KEYDOWN SPACE: запоминаем нажатие; если на земле — начинаем зарядку."""
        self._space_pressed = True
        if self._state == JumpState.IDLE and on_ground:
            self._start_charging()

    def release(self, *, on_ground: bool) -> Optional[JumpEvent]:
        """KEYUP SPACE: возвращает событие прыжка, если он должен сработать."""
        self._space_pressed = False
        event: Optional[JumpEvent] = None
        if self._state == JumpState.CHARGING:
            if on_ground:
                event = JumpEvent(force=(0.0, -self._compute_force()))
            self._reset()
        return event

    def update(self, dt: float, *, on_ground: bool) -> None:
        """Покадровое обновление: автозарядка при касании земли и инкремент таймера."""
        if (
            self._space_pressed
            and self._state == JumpState.IDLE
            and on_ground
        ):
            self._start_charging()

        if self._state == JumpState.CHARGING:
            self._charge_time = min(
                self._charge_time + dt, self.max_charge_time
            )

    # ------------------------------------------------------------------
    # Внутренние помощники
    # ------------------------------------------------------------------
    def _start_charging(self) -> None:
        self._state = JumpState.CHARGING
        self._charge_time = 0.0

    def _reset(self) -> None:
        self._state = JumpState.IDLE
        self._charge_time = 0.0

    def _compute_force(self) -> float:
        factor = self.min_factor + (1.0 - self.min_factor) * self.charge_ratio
        return self.jump_force * factor
