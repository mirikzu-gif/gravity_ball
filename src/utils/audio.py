"""Минимальный аудио-движок: синтез простых звуков через WAV-байты.

Без зависимости от numpy: WAV-данные собираются вручную через struct.
Звуки кэшируются — лениво создаются при первом запросе.
"""
import io
import math
import struct
from pathlib import Path
from typing import Optional

import pygame


_SAMPLE_RATE = 22050
_BIT_DEPTH = 16
_MAX_AMP = 2 ** (_BIT_DEPTH - 1) - 1
DEFAULT_BACKGROUND_MUSIC_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "assets"
    / "background_music.ogg"
)


def _wav_bytes(samples) -> bytes:
    """Упаковывает список int16 семплов в моно-WAV."""
    n = len(samples)
    byte_rate = _SAMPLE_RATE * 2
    block_align = 2

    buf = io.BytesIO()
    buf.write(b"RIFF")
    buf.write(struct.pack("<I", 36 + n * 2))
    buf.write(b"WAVE")
    buf.write(b"fmt ")
    buf.write(struct.pack("<I", 16))
    buf.write(struct.pack("<H", 1))            # PCM
    buf.write(struct.pack("<H", 1))            # mono
    buf.write(struct.pack("<I", _SAMPLE_RATE))
    buf.write(struct.pack("<I", byte_rate))
    buf.write(struct.pack("<H", block_align))
    buf.write(struct.pack("<H", _BIT_DEPTH))
    buf.write(b"data")
    buf.write(struct.pack("<I", n * 2))
    buf.write(struct.pack("<%dh" % n, *samples))
    return buf.getvalue()


def _make_tone(freq: float, duration: float, volume: float = 0.4) -> "pygame.mixer.Sound":
    """Синусоида с плавным затуханием амплитуды (без щелчка в конце)."""
    n = int(_SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        # линейное затухание от 1 до 0 — крайне простая огибающая
        envelope = 1.0 - (i / n)
        sample = int(volume * _MAX_AMP * envelope * math.sin(2 * math.pi * freq * i / _SAMPLE_RATE))
        samples.append(sample)
    return pygame.mixer.Sound(buffer=_wav_bytes(samples))


def _make_sweep(start_freq: float, end_freq: float, duration: float, volume: float = 0.4) -> "pygame.mixer.Sound":
    """Линейный sweep частоты — для прыжка приятнее звучит."""
    n = int(_SAMPLE_RATE * duration)
    samples = []
    phase = 0.0
    for i in range(n):
        t = i / n
        freq = start_freq + (end_freq - start_freq) * t
        phase += 2 * math.pi * freq / _SAMPLE_RATE
        envelope = 1.0 - t
        sample = int(volume * _MAX_AMP * envelope * math.sin(phase))
        samples.append(sample)
    return pygame.mixer.Sound(buffer=_wav_bytes(samples))


# Кэш — звуки создаются лениво и переиспользуются.
_cache: dict = {}
_background_channel: Optional["pygame.mixer.Channel"] = None


def _configure_channels() -> None:
    """Reserves channel 0 for background audio so SFX do not steal it."""
    try:
        pygame.mixer.set_num_channels(8)
        pygame.mixer.set_reserved(1)
    except pygame.error:
        pass


def _get_or_init_mixer() -> bool:
    """Возвращает True, если миксер удалось инициализировать."""
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init(frequency=_SAMPLE_RATE, size=-_BIT_DEPTH, channels=1)
        except pygame.error:
            return False
    _configure_channels()
    return True


def _make_background_loop(duration: float = 4.0, volume: float = 0.18) -> "pygame.mixer.Sound":
    """Small ambient loop with soft arpeggio notes under the game action."""
    n = int(_SAMPLE_RATE * duration)
    samples = []
    notes = (110.0, 146.83, 164.81, 220.0)  # A2, D3, E3, A3
    step = duration / len(notes)
    for i in range(n):
        t = i / _SAMPLE_RATE
        value = 0.0

        # Quiet drone.
        value += 0.30 * math.sin(2 * math.pi * 55.0 * t)
        value += 0.18 * math.sin(2 * math.pi * 110.0 * t)

        # Soft note envelope for the current arpeggio step.
        note_index = int(t / step) % len(notes)
        note_t = (t - note_index * step) / step
        attack = min(note_t / 0.12, 1.0)
        release = max(0.0, 1.0 - max(0.0, note_t - 0.45) / 0.55)
        envelope = attack * release
        freq = notes[note_index]
        value += 0.52 * envelope * math.sin(2 * math.pi * freq * t)
        value += 0.18 * envelope * math.sin(2 * math.pi * freq * 2.0 * t)

        # Fade loop edges slightly to avoid clicks when pygame repeats it.
        edge = min(i / (_SAMPLE_RATE * 0.05), (n - i - 1) / (_SAMPLE_RATE * 0.05), 1.0)
        sample = int(volume * _MAX_AMP * max(0.0, edge) * value)
        samples.append(sample)

    return pygame.mixer.Sound(buffer=_wav_bytes(samples))


def _load_background_sound() -> "pygame.mixer.Sound":
    """Loads downloaded background music, falling back to the synthesized loop."""
    if DEFAULT_BACKGROUND_MUSIC_PATH.is_file():
        try:
            snd = pygame.mixer.Sound(str(DEFAULT_BACKGROUND_MUSIC_PATH))
            snd.set_volume(0.55)
            return snd
        except pygame.error:
            pass

    snd = _make_background_loop()
    snd.set_volume(0.55)
    return snd


def play_jump() -> None:
    if not _get_or_init_mixer():
        return
    snd = _cache.get("jump")
    if snd is None:
        snd = _make_sweep(220, 660, 0.18, volume=0.35)
        _cache["jump"] = snd
    snd.play()


def play_bounce() -> None:
    if not _get_or_init_mixer():
        return
    snd = _cache.get("bounce")
    if snd is None:
        snd = _make_sweep(180, 60, 0.08, volume=0.22)
        _cache["bounce"] = snd
    snd.play()


def play_goal() -> None:
    if not _get_or_init_mixer():
        return
    snd = _cache.get("goal")
    if snd is None:
        # короткий аккорд: 523, 659, 784 — C major triad
        n = int(_SAMPLE_RATE * 0.45)
        samples = []
        freqs = (523.25, 659.25, 783.99)
        for i in range(n):
            t = i / n
            envelope = 1.0 - t
            value = sum(math.sin(2 * math.pi * f * i / _SAMPLE_RATE) for f in freqs) / len(freqs)
            sample = int(0.5 * _MAX_AMP * envelope * value)
            samples.append(sample)
        snd = pygame.mixer.Sound(buffer=_wav_bytes(samples))
        _cache["goal"] = snd
    snd.play()


def play_background() -> None:
    """Starts the background loop once; repeated calls are no-ops while playing."""
    global _background_channel
    if not _get_or_init_mixer():
        return
    snd = _cache.get("background")
    if snd is None:
        snd = _load_background_sound()
        _cache["background"] = snd

    channel = pygame.mixer.Channel(0)
    if channel.get_busy():
        _background_channel = channel
        return

    channel.play(snd, loops=-1, fade_ms=500)
    _background_channel = channel


def stop_background(fade_ms: int = 250) -> None:
    """Stops the background loop if it is active."""
    global _background_channel
    if _background_channel is not None:
        try:
            _background_channel.fadeout(fade_ms)
        except pygame.error:
            pass
    _background_channel = None


def reset_cache() -> None:
    """Сброс — нужно в тестах, чтобы не таскать Sound между прогонами."""
    stop_background(fade_ms=0)
    _cache.clear()
