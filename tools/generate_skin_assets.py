"""Generate ball skin PNG files in assets/skins/."""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from src.utils import skins  # noqa: E402


ASSETS_DIR = PROJECT_ROOT / "assets"
SKINS_DIR = ASSETS_DIR / "skins"
FILENAMES = {
    "skin_red_ball": "red_ball.png",
    "skin_pokeball": "pokeball.png",
    "skin_amogus": "amogus.png",
    "skin_ditto": "ditto.png",
    "skin_redball": "redball.png",
    "skin_patrick": "patrick.png",
    "skin_voltorb": "voltorb.png",
    "skin_stone": "stone.png",
}


def make_skin_surface(skin: skins.Skin, radius: int = 32) -> pygame.Surface:
    diameter = radius * 2
    surface = pygame.Surface((diameter + 4, diameter + 4), pygame.SRCALPHA)
    center = (surface.get_width() // 2, surface.get_height() // 2)

    if skin.sprite_id == "skin_pokeball":
        _draw_pokeball(surface, center, radius, skin)
    elif skin.sprite_id == "skin_amogus":
        _draw_amogus(surface, center, radius, skin)
    elif skin.sprite_id == "skin_ditto":
        _draw_ditto(surface, center, radius, skin)
    elif skin.sprite_id == "skin_redball":
        _draw_redball(surface, center, radius, skin)
    elif skin.sprite_id == "skin_patrick":
        _draw_patrick(surface, center, radius, skin)
    elif skin.sprite_id == "skin_voltorb":
        _draw_voltorb(surface, center, radius, skin)
    elif skin.sprite_id == "skin_stone":
        _draw_stone(surface, center, radius, skin)
    else:
        _draw_red_ball(surface, center, radius, skin)

    return surface


def _draw_base_ball(
    surface: pygame.Surface,
    center,
    radius: int,
    skin: skins.Skin,
) -> None:
    shade_pos = (center[0] - radius // 5, center[1] + radius // 5)
    pygame.draw.circle(surface, skin.shade, center, radius)
    pygame.draw.circle(surface, skin.fill, shade_pos, max(2, radius - 6))

    highlight_pos = (
        center[0] - radius // 3,
        center[1] - radius // 3,
    )
    pygame.draw.circle(surface, skin.highlight, highlight_pos, max(2, radius // 3))
    pygame.draw.line(
        surface,
        skin.outline,
        (center[0] + radius // 3, center[1]),
        (center[0] + radius - 7, center[1]),
        4,
    )
    pygame.draw.circle(surface, skin.outline, center, radius, 3)


def _draw_red_ball(
    surface: pygame.Surface,
    center,
    radius: int,
    skin: skins.Skin,
) -> None:
    _draw_base_ball(surface, center, radius, skin)


def _draw_pokeball(
    surface: pygame.Surface,
    center,
    radius: int,
    skin: skins.Skin,
) -> None:
    clip = pygame.Rect(center[0] - radius, center[1] - radius, radius * 2, radius * 2)
    pygame.draw.circle(surface, (245, 245, 245), center, radius)
    top = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(top, (225, 35, 35), center, radius)
    top_clip = pygame.Rect(clip.x, clip.y, clip.width, radius)
    surface.blit(top, top_clip.topleft, top_clip)
    pygame.draw.line(
        surface,
        skin.outline,
        (center[0] - radius, center[1]),
        (center[0] + radius, center[1]),
        7,
    )
    pygame.draw.circle(surface, skin.outline, center, radius // 3)
    pygame.draw.circle(surface, (242, 242, 242), center, radius // 5)
    pygame.draw.circle(surface, skin.outline, center, radius, 3)
    pygame.draw.circle(
        surface,
        (255, 190, 190),
        (center[0] - radius // 3, center[1] - radius // 2),
        radius // 5,
    )


def _draw_amogus(
    surface: pygame.Surface,
    center,
    radius: int,
    skin: skins.Skin,
) -> None:
    body = pygame.Rect(0, 0, radius + 16, radius * 2 - 8)
    body.center = (center[0] - 2, center[1] + 3)
    pygame.draw.rect(surface, skin.shade, body.move(4, 4), border_radius=radius // 2)
    pygame.draw.rect(surface, skin.fill, body, border_radius=radius // 2)
    pack = pygame.Rect(center[0] + radius // 3, center[1], radius // 3, radius)
    pygame.draw.rect(surface, skin.shade, pack, border_radius=8)
    visor = pygame.Rect(center[0] - radius // 2, center[1] - radius // 2, radius, radius // 2)
    pygame.draw.rect(surface, (100, 170, 200), visor, border_radius=10)
    pygame.draw.rect(surface, skin.highlight, visor.inflate(-6, -6), border_radius=8)
    leg_w = radius // 3
    pygame.draw.rect(
        surface,
        skin.fill,
        (center[0] - radius // 3, center[1] + radius // 2, leg_w, radius // 2),
        border_radius=5,
    )
    pygame.draw.rect(
        surface,
        skin.fill,
        (center[0] + radius // 5, center[1] + radius // 2, leg_w, radius // 2),
        border_radius=5,
    )
    pygame.draw.rect(surface, skin.outline, body, width=3, border_radius=radius // 2)
    pygame.draw.circle(surface, skin.outline, center, radius, 3)


def _draw_ditto(
    surface: pygame.Surface,
    center,
    radius: int,
    skin: skins.Skin,
) -> None:
    points = [
        (center[0] - radius, center[1] + 5),
        (center[0] - radius + 8, center[1] - radius // 2),
        (center[0] - radius // 3, center[1] - radius + 2),
        (center[0] + radius // 2, center[1] - radius + 6),
        (center[0] + radius, center[1] - radius // 5),
        (center[0] + radius - 5, center[1] + radius // 2),
        (center[0] + radius // 4, center[1] + radius),
        (center[0] - radius // 2, center[1] + radius - 2),
    ]
    pygame.draw.polygon(surface, skin.shade, [(x + 3, y + 4) for x, y in points])
    pygame.draw.polygon(surface, skin.fill, points)
    pygame.draw.polygon(surface, skin.outline, points, 3)
    pygame.draw.circle(
        surface,
        skin.highlight,
        (center[0] - radius // 3, center[1] - radius // 3),
        radius // 5,
    )
    eye_y = center[1] - 2
    pygame.draw.circle(surface, skin.outline, (center[0] - radius // 3, eye_y), 3)
    pygame.draw.circle(surface, skin.outline, (center[0] + radius // 3, eye_y), 3)
    pygame.draw.arc(
        surface,
        skin.outline,
        pygame.Rect(center[0] - 14, center[1] + 2, 28, 18),
        0.2,
        2.94,
        3,
    )


def _draw_redball(
    surface: pygame.Surface,
    center,
    radius: int,
    skin: skins.Skin,
) -> None:
    _draw_base_ball(surface, center, radius, skin)
    eye_y = center[1] - radius // 5
    for x in (center[0] - radius // 3, center[0] + radius // 3):
        pygame.draw.circle(surface, (255, 255, 255), (x, eye_y), radius // 5)
        pygame.draw.circle(surface, skin.outline, (x, eye_y), radius // 9)
    pygame.draw.arc(
        surface,
        skin.outline,
        pygame.Rect(center[0] - radius // 2, center[1], radius, radius // 2),
        0.2,
        2.94,
        4,
    )


def _draw_patrick(
    surface: pygame.Surface,
    center,
    radius: int,
    skin: skins.Skin,
) -> None:
    points = [
        (center[0], center[1] - radius),
        (center[0] + radius // 3, center[1] - radius // 4),
        (center[0] + radius - 2, center[1] - radius // 5),
        (center[0] + radius // 2, center[1] + radius // 5),
        (center[0] + radius // 2, center[1] + radius),
        (center[0], center[1] + radius // 2),
        (center[0] - radius // 2, center[1] + radius),
        (center[0] - radius // 2, center[1] + radius // 5),
        (center[0] - radius + 2, center[1] - radius // 5),
        (center[0] - radius // 3, center[1] - radius // 4),
    ]
    pygame.draw.polygon(surface, skin.shade, [(x + 3, y + 4) for x, y in points])
    pygame.draw.polygon(surface, skin.fill, points)
    pygame.draw.polygon(surface, skin.outline, points, 3)
    shorts = pygame.Rect(center[0] - radius // 2, center[1] + radius // 4, radius, radius // 2)
    pygame.draw.rect(surface, (95, 205, 95), shorts, border_radius=6)
    pygame.draw.polygon(
        surface,
        (120, 60, 150),
        [
            (shorts.left + 8, shorts.centery),
            (shorts.left + 18, shorts.top + 6),
            (shorts.left + 28, shorts.centery),
            (shorts.left + 18, shorts.bottom - 5),
        ],
    )
    pygame.draw.circle(surface, (255, 255, 255), (center[0] - 8, center[1] - 10), 6)
    pygame.draw.circle(surface, (255, 255, 255), (center[0] + 8, center[1] - 10), 6)
    pygame.draw.circle(surface, skin.outline, (center[0] - 8, center[1] - 10), 2)
    pygame.draw.circle(surface, skin.outline, (center[0] + 8, center[1] - 10), 2)
    pygame.draw.arc(
        surface,
        skin.outline,
        pygame.Rect(center[0] - 12, center[1] - 2, 24, 16),
        0.1,
        3.04,
        2,
    )


def _draw_voltorb(
    surface: pygame.Surface,
    center,
    radius: int,
    skin: skins.Skin,
) -> None:
    _draw_pokeball(surface, center, radius, skin)
    brow_y = center[1] - radius // 4
    pygame.draw.line(
        surface,
        skin.outline,
        (center[0] - radius // 2, brow_y - 8),
        (center[0] - 4, brow_y),
        4,
    )
    pygame.draw.line(
        surface,
        skin.outline,
        (center[0] + radius // 2, brow_y - 8),
        (center[0] + 4, brow_y),
        4,
    )
    pygame.draw.circle(surface, (255, 255, 255), (center[0] - 10, center[1] - 3), 6)
    pygame.draw.circle(surface, (255, 255, 255), (center[0] + 10, center[1] - 3), 6)
    pygame.draw.circle(surface, skin.outline, (center[0] - 10, center[1] - 3), 3)
    pygame.draw.circle(surface, skin.outline, (center[0] + 10, center[1] - 3), 3)
    pygame.draw.arc(
        surface,
        skin.outline,
        pygame.Rect(center[0] - 14, center[1] + 12, 28, 14),
        3.35,
        6.0,
        3,
    )


def _draw_stone(
    surface: pygame.Surface,
    center,
    radius: int,
    skin: skins.Skin,
) -> None:
    points = [
        (center[0] - radius, center[1] - radius // 4),
        (center[0] - radius // 2, center[1] - radius),
        (center[0] + radius // 2, center[1] - radius + 2),
        (center[0] + radius, center[1] - radius // 5),
        (center[0] + radius - 5, center[1] + radius // 2),
        (center[0] + radius // 3, center[1] + radius),
        (center[0] - radius // 2, center[1] + radius - 4),
    ]
    pygame.draw.polygon(surface, skin.shade, [(x + 3, y + 4) for x, y in points])
    pygame.draw.polygon(surface, skin.fill, points)
    pygame.draw.polygon(
        surface,
        skin.highlight,
        [
            (center[0] - radius + 7, center[1] - radius // 5),
            (center[0] - radius // 3, center[1] - radius + 6),
            (center[0] - radius // 6, center[1] - 4),
        ],
    )
    pygame.draw.polygon(
        surface,
        (70, 80, 100),
        [
            (center[0] + 4, center[1] - 6),
            (center[0] + radius - 8, center[1] - radius // 5),
            (center[0] + radius // 2, center[1] + radius // 3),
        ],
    )
    pygame.draw.line(surface, skin.outline, (center[0] - 10, center[1] - 4), (center[0] + 8, center[1] + 12), 3)
    pygame.draw.line(surface, skin.outline, (center[0] + 8, center[1] + 12), (center[0] + 2, center[1] + 24), 2)
    pygame.draw.polygon(surface, skin.outline, points, 3)


def main() -> None:
    pygame.init()
    SKINS_DIR.mkdir(parents=True, exist_ok=True)

    for skin in skins.SKINS:
        filename = FILENAMES[skin.sprite_id]
        path = SKINS_DIR / filename
        pygame.image.save(make_skin_surface(skin), str(path))
        print(f"saved {path}")

    pygame.quit()


if __name__ == "__main__":
    main()
