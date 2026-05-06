"""Smoke-тесты game.main()."""
import pygame


def test_main_exits_on_quit_event(monkeypatch):
    """main() должен дойти до конца цикла и выйти при QUIT."""
    import game

    quit_event = pygame.event.Event(pygame.QUIT)
    call_count = {"n": 0}

    def fake_get():
        call_count["n"] += 1
        return [quit_event] if call_count["n"] == 1 else []

    monkeypatch.setattr(pygame.event, "get", fake_get)

    game.main()

    assert call_count["n"] >= 1


def test_main_processes_at_least_one_frame_before_quit(monkeypatch):
    """main() обрабатывает хотя бы один кадр (через MenuScene) до выхода."""
    import game

    quit_event = pygame.event.Event(pygame.QUIT)
    frames = {"n": 0}

    def fake_get():
        frames["n"] += 1
        return [quit_event] if frames["n"] >= 2 else []

    monkeypatch.setattr(pygame.event, "get", fake_get)

    game.main()

    assert frames["n"] >= 2
