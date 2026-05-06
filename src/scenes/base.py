"""Базовый класс сцены.

Сцены — это «экраны» приложения с собственным состоянием, обработкой ввода,
физикой и рендером. Переход между сценами осуществляется через `next_scene`.
"""
from typing import Optional

import pygame


class Scene:
    """Базовый Scene. Подклассы переопределяют нужные методы.

    Переход: установить `self.next_scene = OtherScene(...)`. Раннер заметит
    это и в следующем кадре переключится на новую сцену.

    Завершение приложения: запостить pygame.event.Event(pygame.QUIT).
    """

    def __init__(self) -> None:
        self.next_scene: Optional["Scene"] = None

    def handle_event(self, event: pygame.event.Event) -> None:
        """Обрабатывает один pygame-event."""

    def fixed_update(self, dt: float) -> None:
        """Шаг физики/логики с фиксированным dt. Может вызываться 0..N раз за кадр."""

    def render(self, screen: pygame.Surface, alpha: float = 1.0) -> None:
        """Отрисовка кадра.

        alpha ∈ [0, 1) — доля accumulator относительно FIXED_DT. Используется
        для интерполяции между последним и текущим физическим состоянием:
        render_pos = prev * (1 - alpha) + curr * alpha. Сцены без анимации
        могут просто игнорировать параметр.
        """
