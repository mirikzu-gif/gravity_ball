"""Обработчик ввода: pygame events → игровые команды.

Хранит множество нажатых клавиш и переводит события в InputAction. Команды
движения вычисляются по запросу (вектор -1..1 по каждой оси).
"""
from enum import Enum
from typing import Optional, Set, Tuple

import pygame


class InputAction(Enum):
    QUIT = "quit"
    JUMP_PRESS = "jump_press"
    JUMP_RELEASE = "jump_release"


class InputHandler:
    """Преобразует pygame-события в InputAction и отслеживает зажатые клавиши."""

    def __init__(self) -> None:
        self._held_keys: Set[int] = set()

    @property
    def held_keys(self) -> Set[int]:
        return frozenset(self._held_keys)  # копия только для чтения

    def process_event(self, event) -> Optional[InputAction]:
        """Обрабатывает один pygame-event и возвращает действие, если есть."""
        if event.type == pygame.QUIT:
            return InputAction.QUIT
        if event.type == pygame.KEYDOWN:
            self._held_keys.add(event.key)
            if event.key == pygame.K_SPACE:
                return InputAction.JUMP_PRESS
        elif event.type == pygame.KEYUP:
            self._held_keys.discard(event.key)
            if event.key == pygame.K_SPACE:
                return InputAction.JUMP_RELEASE
        return None

    def get_movement(self) -> Tuple[float, float]:
        """Вектор движения (dx, dy) в диапазоне [-1, 1] по каждой оси."""
        dx = 0.0
        dy = 0.0
        if pygame.K_LEFT in self._held_keys:
            dx -= 1.0
        if pygame.K_RIGHT in self._held_keys:
            dx += 1.0
        if pygame.K_UP in self._held_keys:
            dy -= 1.0
        if pygame.K_DOWN in self._held_keys:
            dy += 1.0
        return (dx, dy)

    def clear(self) -> None:
        """Сбрасывает состояние зажатых клавиш при смене контекста ввода."""
        self._held_keys.clear()
