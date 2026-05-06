"""Smoke-тесты для game.main().

Проверяют, что главный цикл собирается, делает один кадр и корректно завершается
по QUIT — без открытия реального окна (SDL_VIDEODRIVER=dummy в conftest).
"""
import pygame
import pytest


def test_main_exits_on_quit_event(monkeypatch):
    """main() должен дойти до конца цикла и выйти при первом QUIT."""
    import game

    quit_event = pygame.event.Event(pygame.QUIT)
    call_count = {"n": 0}

    def fake_get():
        call_count["n"] += 1
        # на первом тике сразу шлём QUIT
        return [quit_event] if call_count["n"] == 1 else []

    monkeypatch.setattr(pygame.event, "get", fake_get)

    # должно завершиться без исключений
    game.main()

    assert call_count["n"] >= 1


def test_main_processes_at_least_one_frame_before_quit(monkeypatch):
    """main() обрабатывает хотя бы один полный кадр (физика, рендер) до выхода."""
    import game

    quit_event = pygame.event.Event(pygame.QUIT)
    frames = {"n": 0}

    def fake_get():
        frames["n"] += 1
        return [quit_event] if frames["n"] >= 2 else []

    monkeypatch.setattr(pygame.event, "get", fake_get)

    game.main()

    assert frames["n"] >= 2  # хотя бы один тик прошёл «нормально», и затем QUIT


def test_jump_impulse_derivation():
    """JUMP_IMPULSE = JUMP_FORCE * FIXED_DT — преобразование из per-frame силы в импульс."""
    import game
    from src.utils.config import FIXED_DT, JUMP_FORCE

    assert game.JUMP_IMPULSE == pytest.approx(JUMP_FORCE * FIXED_DT)
