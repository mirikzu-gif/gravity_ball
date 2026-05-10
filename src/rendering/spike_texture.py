"""Tile-based rendering for spike blocks."""
import pygame

from ..utils import assets
from ..utils.config import BLACK


SPIKE_TILE_ASPECT = 0.6


def _tile_width(height: int) -> int:
    return max(4, int(round(height * SPIKE_TILE_ASPECT)))


def draw_spike_block(screen, rect: pygame.Rect, sprites=None) -> None:
    """Draws spikes by repeating a texture cell instead of stretching it."""
    if rect.width <= 0 or rect.height <= 0:
        return
    if sprites is None:
        sprites = assets.get_sprite_manager()

    tile_size = (_tile_width(rect.height), rect.height)
    sprite = sprites.get_scaled("spike", tile_size)

    old_clip = screen.get_clip()
    screen.set_clip(rect)
    if sprite is not None:
        for x in range(rect.left, rect.right, tile_size[0]):
            screen.blit(sprite, (x, rect.top))
        screen.set_clip(old_clip)
        return

    _draw_fallback_spikes(screen, rect, tile_size[0])
    screen.set_clip(old_clip)


def _draw_fallback_spikes(screen, rect: pygame.Rect, tile_width: int) -> None:
    pygame.draw.rect(screen, (120, 30, 36), rect)
    base_h = max(4, rect.height // 3)
    base_top = rect.bottom - base_h

    for x in range(rect.left, rect.right, tile_width):
        right = x + tile_width
        points = [
            (x, base_top),
            (x + tile_width // 2, rect.top),
            (right, base_top),
        ]
        pygame.draw.polygon(screen, (240, 55, 60), points)
        pygame.draw.polygon(screen, BLACK, points, 2)

    pygame.draw.line(screen, BLACK, (rect.left, base_top), (rect.right, base_top), 2)
    pygame.draw.line(screen, BLACK, rect.bottomleft, rect.bottomright, 3)
