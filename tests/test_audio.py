"""Тесты модуля audio.

В headless-окружении pygame.mixer.init может молча провалиться (нет аудио-устройства).
Главное — функции play_* не должны падать ни в каких условиях.
"""
import pygame

from src.utils import audio


def test_play_jump_does_not_raise():
    audio.reset_cache()
    audio.play_jump()  # не должно падать ни при каком состоянии mixer'а


def test_play_goal_does_not_raise():
    audio.reset_cache()
    audio.play_goal()


def test_repeated_play_uses_cache():
    """Повторный вызов не пересоздаёт Sound."""
    audio.reset_cache()
    audio.play_jump()
    if "jump" in audio._cache:
        first = audio._cache["jump"]
        audio.play_jump()
        assert audio._cache["jump"] is first


def test_reset_cache_clears():
    audio._cache["dummy"] = object()
    audio.reset_cache()
    assert audio._cache == {}


def test_play_with_mixer_initialized():
    """Если миксер запущен — звук создаётся как pygame.mixer.Sound."""
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1)
        except pygame.error:
            return  # на этой машине нет аудио — тест пропускается без падения

    audio.reset_cache()
    audio.play_jump()
    assert "jump" in audio._cache
    assert isinstance(audio._cache["jump"], pygame.mixer.Sound)
