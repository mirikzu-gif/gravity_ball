"""Тесты InputHandler.

pygame импортируется, но pygame.init() не вызывается — мы используем только
константы и собственные fake-объекты событий.
"""
from types import SimpleNamespace

import pygame
import pytest

from src.game.input_handler import InputAction, InputHandler


def _ev(type_, key=None):
    """Простая подделка pygame.event с .type и .key."""
    return SimpleNamespace(type=type_, key=key)


@pytest.fixture
def handler():
    return InputHandler()


# ---------------------------------------------------------------------------
# Базовые действия
# ---------------------------------------------------------------------------


def test_quit_event_returns_quit_action(handler):
    action = handler.process_event(_ev(pygame.QUIT))
    assert action is InputAction.QUIT


def test_space_keydown_returns_jump_press(handler):
    action = handler.process_event(_ev(pygame.KEYDOWN, pygame.K_SPACE))
    assert action is InputAction.JUMP_PRESS


def test_space_keyup_returns_jump_release(handler):
    action = handler.process_event(_ev(pygame.KEYUP, pygame.K_SPACE))
    assert action is InputAction.JUMP_RELEASE


@pytest.mark.parametrize(
    "key", [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]
)
def test_arrow_keydown_returns_no_action_but_tracked(handler, key):
    action = handler.process_event(_ev(pygame.KEYDOWN, key))
    assert action is None
    assert key in handler.held_keys


@pytest.mark.parametrize(
    "key", [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]
)
def test_arrow_keyup_removes_key(handler, key):
    handler.process_event(_ev(pygame.KEYDOWN, key))
    handler.process_event(_ev(pygame.KEYUP, key))
    assert key not in handler.held_keys


def test_unknown_event_type_returns_none(handler):
    action = handler.process_event(_ev(pygame.MOUSEMOTION))
    assert action is None


def test_keyup_on_unpressed_key_is_safe(handler):
    """KEYUP без предварительного KEYDOWN не должен бросать исключение."""
    action = handler.process_event(_ev(pygame.KEYUP, pygame.K_LEFT))
    assert action is None
    assert pygame.K_LEFT not in handler.held_keys


# ---------------------------------------------------------------------------
# Отслеживание зажатых клавиш
# ---------------------------------------------------------------------------


def test_initial_held_keys_empty(handler):
    assert handler.held_keys == frozenset()


def test_held_keys_returns_immutable_view(handler):
    handler.process_event(_ev(pygame.KEYDOWN, pygame.K_LEFT))
    keys = handler.held_keys
    assert isinstance(keys, frozenset)
    # модификации внутреннего состояния не должны влиять на уже полученный snapshot
    handler.process_event(_ev(pygame.KEYUP, pygame.K_LEFT))
    assert pygame.K_LEFT in keys


def test_space_keydown_also_tracked_in_held_keys(handler):
    handler.process_event(_ev(pygame.KEYDOWN, pygame.K_SPACE))
    assert pygame.K_SPACE in handler.held_keys


# ---------------------------------------------------------------------------
# get_movement
# ---------------------------------------------------------------------------


def test_no_keys_returns_zero_movement(handler):
    assert handler.get_movement() == (0.0, 0.0)


@pytest.mark.parametrize(
    "key,expected",
    [
        (pygame.K_LEFT, (-1.0, 0.0)),
        (pygame.K_RIGHT, (1.0, 0.0)),
        (pygame.K_UP, (0.0, -1.0)),
        (pygame.K_DOWN, (0.0, 1.0)),
    ],
)
def test_single_arrow_movement(handler, key, expected):
    handler.process_event(_ev(pygame.KEYDOWN, key))
    assert handler.get_movement() == expected


def test_left_and_right_cancel_out(handler):
    handler.process_event(_ev(pygame.KEYDOWN, pygame.K_LEFT))
    handler.process_event(_ev(pygame.KEYDOWN, pygame.K_RIGHT))
    assert handler.get_movement() == (0.0, 0.0)


def test_up_and_down_cancel_out(handler):
    handler.process_event(_ev(pygame.KEYDOWN, pygame.K_UP))
    handler.process_event(_ev(pygame.KEYDOWN, pygame.K_DOWN))
    assert handler.get_movement() == (0.0, 0.0)


def test_diagonal_movement(handler):
    handler.process_event(_ev(pygame.KEYDOWN, pygame.K_LEFT))
    handler.process_event(_ev(pygame.KEYDOWN, pygame.K_UP))
    assert handler.get_movement() == (-1.0, -1.0)


def test_releasing_one_arrow_keeps_other(handler):
    handler.process_event(_ev(pygame.KEYDOWN, pygame.K_LEFT))
    handler.process_event(_ev(pygame.KEYDOWN, pygame.K_UP))
    handler.process_event(_ev(pygame.KEYUP, pygame.K_LEFT))
    assert handler.get_movement() == (0.0, -1.0)


def test_space_does_not_affect_movement(handler):
    handler.process_event(_ev(pygame.KEYDOWN, pygame.K_SPACE))
    assert handler.get_movement() == (0.0, 0.0)
