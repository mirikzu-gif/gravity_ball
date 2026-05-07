"""Project font helpers.

Title text uses Press Start 2P; regular UI text uses Public Pixel. Both files
live in assets/fonts and fall back to pygame's default font if unavailable.
"""
from functools import lru_cache
from pathlib import Path

import pygame


FONTS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "fonts"
TITLE_FONT_PATH = FONTS_DIR / "PressStart2P-Regular.ttf"
UI_FONT_PATH = FONTS_DIR / "PublicPixel.ttf"


@lru_cache(maxsize=32)
def _load_font(path: str, size: int) -> pygame.font.Font:
    font_path = Path(path)
    if font_path.is_file():
        try:
            return pygame.font.Font(str(font_path), size)
        except pygame.error:
            pass
    return pygame.font.Font(None, size)


def title(size: int) -> pygame.font.Font:
    """Font for large headings."""
    return _load_font(str(TITLE_FONT_PATH), size)


def ui(size: int) -> pygame.font.Font:
    """Font for menus, labels, and hints."""
    return _load_font(str(UI_FONT_PATH), size)


def hud(size: int) -> pygame.font.Font:
    """Font for compact in-game HUD text."""
    return ui(size)


def reset_cache() -> None:
    """Clears cached pygame Font objects before pygame.quit/re-init cycles."""
    _load_font.cache_clear()
