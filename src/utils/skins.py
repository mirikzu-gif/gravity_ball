"""Skin catalog and in-memory selection for the player ball."""
from dataclasses import dataclass
from typing import Tuple


Color = Tuple[int, int, int]


@dataclass(frozen=True)
class Skin:
    """Visual palette and sprite id for drawing the ball."""

    name: str
    sprite_id: str
    fill: Color
    shade: Color
    outline: Color
    highlight: Color


SKINS: Tuple[Skin, ...] = (
    Skin(
        name="Красный шарик",
        sprite_id="skin_red_ball",
        fill=(255, 70, 70),
        shade=(180, 30, 30),
        outline=(40, 0, 0),
        highlight=(255, 220, 220),
    ),
    Skin(
        name="Покеболл",
        sprite_id="skin_pokeball",
        fill=(245, 245, 245),
        shade=(220, 40, 40),
        outline=(20, 20, 20),
        highlight=(255, 255, 255),
    ),
    Skin(
        name="Амогус",
        sprite_id="skin_amogus",
        fill=(210, 35, 45),
        shade=(120, 20, 35),
        outline=(35, 20, 24),
        highlight=(170, 230, 245),
    ),
    Skin(
        name="Дитто",
        sprite_id="skin_ditto",
        fill=(190, 115, 210),
        shade=(120, 70, 160),
        outline=(76, 42, 105),
        highlight=(236, 190, 245),
    ),
    Skin(
        name="Редболл",
        sprite_id="skin_redball",
        fill=(230, 30, 35),
        shade=(150, 18, 25),
        outline=(45, 0, 0),
        highlight=(255, 165, 165),
    ),
    Skin(
        name="Патрик",
        sprite_id="skin_patrick",
        fill=(245, 130, 165),
        shade=(180, 75, 120),
        outline=(92, 40, 70),
        highlight=(255, 200, 215),
    ),
    Skin(
        name="Волторб",
        sprite_id="skin_voltorb",
        fill=(245, 245, 245),
        shade=(220, 35, 40),
        outline=(20, 20, 20),
        highlight=(255, 255, 255),
    ),
    Skin(
        name="Камень",
        sprite_id="skin_stone",
        fill=(105, 115, 135),
        shade=(55, 65, 85),
        outline=(25, 30, 42),
        highlight=(170, 180, 195),
    ),
)

DEFAULT_SKIN_INDEX = 0
_selected_index = DEFAULT_SKIN_INDEX


def skin_count() -> int:
    return len(SKINS)


def get_skin(index: int) -> Skin:
    return SKINS[index]


def get_selected_index() -> int:
    return _selected_index


def get_selected_skin() -> Skin:
    return SKINS[_selected_index]


def select_skin(index: int) -> None:
    if not 0 <= index < len(SKINS):
        raise IndexError(f"skin index {index} вне диапазона [0, {len(SKINS)})")

    global _selected_index
    _selected_index = index


def reset_selection() -> None:
    select_skin(DEFAULT_SKIN_INDEX)
