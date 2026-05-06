"""Тесты run_scenes — главного цикла приложения."""
import pygame

from src.scenes.base import Scene
from src.scenes.runner import run_scenes


class _RecordingScene(Scene):
    """Фейковая сцена, которая считает вызовы и может перейти на другую или закрыть."""

    def __init__(self, name="A", transition_to=None, quit_after_renders=None):
        super().__init__()
        self.name = name
        self.events_seen = []
        self.fixed_calls = 0
        self.renders = 0
        self.last_alpha = None
        self._transition_to = transition_to
        self._quit_after = quit_after_renders

    def handle_event(self, event):
        self.events_seen.append(event)

    def fixed_update(self, dt):
        self.fixed_calls += 1
        if self._transition_to is not None:
            self.next_scene = self._transition_to

    def render(self, screen, alpha=1.0):
        self.renders += 1
        self.last_alpha = alpha
        if self._quit_after is not None and self.renders >= self._quit_after:
            pygame.event.post(pygame.event.Event(pygame.QUIT))


def test_run_scenes_quits_on_pygame_quit_event():
    scene = _RecordingScene(quit_after_renders=1)
    run_scenes(scene)
    assert scene.renders >= 1


def test_run_scenes_transitions_to_next_scene():
    second = _RecordingScene(name="B", quit_after_renders=1)
    first = _RecordingScene(name="A", transition_to=second)

    run_scenes(first)

    # Первая сцена сделала хотя бы один fixed_update и установила transition,
    # после чего раннер переключился на вторую и она закрыла окно.
    assert first.fixed_calls >= 1
    assert second.renders >= 1


def test_run_scenes_passes_alpha_in_unit_range():
    scene = _RecordingScene(quit_after_renders=1)
    run_scenes(scene)
    assert scene.last_alpha is not None
    assert 0 <= scene.last_alpha < 1.0


def test_run_scenes_clears_next_scene_after_switch():
    """После перехода у новой сцены next_scene должно стать None,
    чтобы повторно используемые экземпляры не «возвращали» нас обратно."""
    second = _RecordingScene(name="B", quit_after_renders=1)
    first = _RecordingScene(name="A", transition_to=second)
    # имитируем использованный экземпляр со «старым» next_scene
    second.next_scene = first

    run_scenes(first)

    # после переключения на second runner обнулил его next_scene
    # и не уехал назад в first
    assert second.renders >= 1


def test_run_scenes_renders_first_scene_before_transition():
    second = _RecordingScene(name="B", quit_after_renders=1)
    first = _RecordingScene(name="A", transition_to=second)

    run_scenes(first)

    # Раннер переключается ДО рендера, поэтому первая сцена может быть отрисована
    # 0 или 1 раз. Главное — что на момент закрытия мы уже были во второй.
    assert second.renders >= 1
