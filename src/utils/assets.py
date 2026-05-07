"""Совместимый фасад для менеджера спрайтов.

Файлы ищутся в `assets/` в корне проекта. Если файла нет — get_image
возвращает None, и вызывающий код может нарисовать сцену процедурно.
Это позволяет пользователю подменять/удалять PNG без правки кода.
"""
from pathlib import Path
from typing import Optional

import pygame

from ..rendering.sprites import DEFAULT_SPRITES, SpriteManager


ASSETS_DIR: Path = (
    Path(__file__).resolve().parent.parent.parent / "assets"
)

_manager: Optional[SpriteManager] = None
_manager_root: Optional[Path] = None


def get_sprite_manager() -> SpriteManager:
    """Возвращает дефолтный SpriteManager для assets/.

    Менеджер пересоздаётся, если тесты или рантайм подменили ASSETS_DIR.
    """
    global _manager, _manager_root
    root = Path(ASSETS_DIR)
    if _manager is None or _manager_root != root:
        _manager = SpriteManager(root, DEFAULT_SPRITES)
        _manager_root = root
    return _manager


def get_image(name: str) -> Optional[pygame.Surface]:
    """Загружает assets/<name> с кэшем. Возвращает None, если файла нет."""
    return get_sprite_manager().get(name)


def reset_cache() -> None:
    """Сброс кэша — нужен в тестах между сценариями."""
    get_sprite_manager().reset()
