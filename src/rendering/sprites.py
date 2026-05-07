"""Sprite loading, caching, and transform management."""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

import pygame


@dataclass(frozen=True)
class SpriteSpec:
    """Declarative description of one sprite asset."""

    filename: str
    size: Optional[Tuple[int, int]] = None
    alpha: bool = True


DEFAULT_SPRITES: Dict[str, SpriteSpec] = {
    "ball": SpriteSpec("ball.png", alpha=True),
    "background": SpriteSpec("background.png", alpha=False),
    "goal": SpriteSpec("goal.png", alpha=True),
    "obstacle": SpriteSpec("obstacle.png", alpha=True),
    "platform": SpriteSpec("platform.png", alpha=True),
}


class SpriteManager:
    """Loads sprites lazily and caches raw and scaled surfaces.

    `sprite_id` can be a registered id from `specs` or a direct filename. Direct
    filenames keep compatibility with the previous assets.get_image("foo.png")
    API while allowing scenes to migrate to stable ids such as "ball".
    """

    def __init__(
        self,
        root: Path,
        specs: Optional[Dict[str, SpriteSpec]] = None,
    ) -> None:
        self.root = Path(root)
        self.specs = dict(specs or {})
        self._raw: Dict[str, Optional[pygame.Surface]] = {}
        self._scaled: Dict[
            Tuple[str, Tuple[int, int]], Optional[pygame.Surface]
        ] = {}
        self._tiled: Dict[
            Tuple[str, Tuple[int, int]], Optional[pygame.Surface]
        ] = {}

    def get(self, sprite_id: str) -> Optional[pygame.Surface]:
        """Returns a cached sprite surface or None if the asset cannot be loaded."""
        if sprite_id in self._raw:
            return self._raw[sprite_id]

        spec = self._spec_for(sprite_id)
        path = self.root / spec.filename
        if not path.is_file():
            self._raw[sprite_id] = None
            return None

        try:
            surface = pygame.image.load(str(path))
            if pygame.display.get_surface() is not None:
                surface = surface.convert_alpha() if spec.alpha else surface.convert()
            if spec.size is not None and surface.get_size() != spec.size:
                surface = pygame.transform.smoothscale(surface, spec.size)
        except pygame.error:
            surface = None

        self._raw[sprite_id] = surface
        return surface

    def get_scaled(
        self,
        sprite_id: str,
        size: Tuple[int, int],
    ) -> Optional[pygame.Surface]:
        """Returns a cached scaled sprite variant."""
        key = (sprite_id, size)
        if key in self._scaled:
            return self._scaled[key]

        surface = self.get(sprite_id)
        if surface is None:
            self._scaled[key] = None
            return None

        if surface.get_size() == size:
            scaled = surface
        else:
            scaled = pygame.transform.smoothscale(surface, size)
        self._scaled[key] = scaled
        return scaled

    def get_tiled(
        self,
        sprite_id: str,
        size: Tuple[int, int],
    ) -> Optional[pygame.Surface]:
        """Returns a cached surface filled by repeating the source sprite."""
        key = (sprite_id, size)
        if key in self._tiled:
            return self._tiled[key]

        tile = self.get(sprite_id)
        if tile is None:
            self._tiled[key] = None
            return None

        surface = pygame.Surface(size, pygame.SRCALPHA)
        tile_width, tile_height = tile.get_size()
        for y in range(0, size[1], tile_height):
            for x in range(0, size[0], tile_width):
                surface.blit(tile, (x, y))

        self._tiled[key] = surface
        return surface

    def preload(self, sprite_ids) -> None:
        """Loads multiple sprites into the raw cache."""
        for sprite_id in sprite_ids:
            self.get(sprite_id)

    def reset(self) -> None:
        """Clears raw and transformed sprite caches."""
        self._raw.clear()
        self._scaled.clear()
        self._tiled.clear()

    def _spec_for(self, sprite_id: str) -> SpriteSpec:
        if sprite_id in self.specs:
            return self.specs[sprite_id]
        return SpriteSpec(sprite_id)
