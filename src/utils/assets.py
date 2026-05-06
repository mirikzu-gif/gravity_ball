"""Менеджер ассетов: ленивая загрузка PNG с кэшем и None-фолбэком.

Файлы ищутся в `assets/` в корне проекта. Если файла нет — get_image
возвращает None, и вызывающий код может нарисовать сцену процедурно.
Это позволяет пользователю подменять/удалять PNG без правки кода.
"""
from pathlib import Path
from typing import Dict, Optional

import pygame


ASSETS_DIR: Path = (
    Path(__file__).resolve().parent.parent.parent / "assets"
)

_cache: Dict[str, Optional[pygame.Surface]] = {}


def get_image(name: str) -> Optional[pygame.Surface]:
    """Загружает assets/<name> с кэшем. Возвращает None, если файла нет.

    Не вызывает Surface.convert*() — этот вызов требует выставленный display
    mode и не нужен для простых рендеров. Скорость в 2D-играх не критична.
    """
    if name in _cache:
        return _cache[name]
    path = ASSETS_DIR / name
    if not path.is_file():
        _cache[name] = None
        return None
    try:
        surf = pygame.image.load(str(path))
    except pygame.error:
        _cache[name] = None
        return None
    _cache[name] = surf
    return surf


def reset_cache() -> None:
    """Сброс кэша — нужен в тестах между сценариями."""
    _cache.clear()
