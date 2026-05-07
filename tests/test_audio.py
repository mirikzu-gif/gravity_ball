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


def test_play_bounce_does_not_raise():
    audio.reset_cache()
    audio.play_bounce()


def test_play_background_does_not_raise():
    audio.reset_cache()
    audio.play_background()


def test_default_background_music_exists():
    assert audio.DEFAULT_BACKGROUND_MUSIC_PATH.exists()


def test_stop_background_does_not_raise():
    audio.reset_cache()
    audio.play_background()
    audio.stop_background(fade_ms=0)


def test_repeated_play_uses_cache():
    """Повторный вызов не пересоздаёт Sound."""
    audio.reset_cache()
    audio.play_jump()
    if "jump" in audio._cache:
        first = audio._cache["jump"]
        audio.play_jump()
        assert audio._cache["jump"] is first


def test_repeated_background_uses_cache():
    audio.reset_cache()
    audio.play_background()
    if "background" in audio._cache:
        first = audio._cache["background"]
        audio.play_background()
        assert audio._cache["background"] is first


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


def test_background_with_mixer_initialized():
    """Если миксер запущен — background создаётся как pygame.mixer.Sound."""
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1)
        except pygame.error:
            return

    audio.reset_cache()
    audio.play_background()
    assert "background" in audio._cache
    assert isinstance(audio._cache["background"], pygame.mixer.Sound)


def test_background_falls_back_when_file_missing(monkeypatch, tmp_path):
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1)
        except pygame.error:
            return

    monkeypatch.setattr(
        audio,
        "DEFAULT_BACKGROUND_MUSIC_PATH",
        tmp_path / "missing.ogg",
    )
    audio.reset_cache()
    audio.play_background()
    assert "background" in audio._cache
    assert isinstance(audio._cache["background"], pygame.mixer.Sound)
