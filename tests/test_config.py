"""Тесты схемы и диапазонов config.MATERIALS и игровых констант."""
import pytest

from src.utils import config


def test_materials_has_required_keys():
    assert set(config.MATERIALS) == {"ball", "stone", "wood"}


@pytest.mark.parametrize("name", ["ball", "stone", "wood"])
def test_material_has_elasticity_and_friction(name):
    material = config.MATERIALS[name]
    assert "elasticity" in material
    assert "friction" in material
    assert isinstance(material["elasticity"], (int, float))
    assert isinstance(material["friction"], (int, float))


@pytest.mark.parametrize("name", ["ball", "stone", "wood"])
def test_friction_in_valid_range(name):
    friction = config.MATERIALS[name]["friction"]
    assert 0 <= friction <= 1


@pytest.mark.parametrize("name", ["ball", "stone", "wood"])
def test_elasticity_non_negative(name):
    assert config.MATERIALS[name]["elasticity"] >= 0


def test_ball_has_mass_and_it_is_positive():
    assert "mass" in config.MATERIALS["ball"]
    assert config.MATERIALS["ball"]["mass"] > 0


def test_screen_dimensions_are_positive():
    assert config.WIDTH > 0
    assert config.HEIGHT > 0


def test_gravity_pulls_down():
    gx, gy = config.GRAVITY
    assert gx == 0
    assert gy > 0  # в pygame ось Y направлена вниз


def test_damping_in_unit_range():
    assert 0 < config.DAMPING <= 1
    assert 0 < config.AIR_RESISTANCE <= 1


def test_forces_are_positive():
    assert config.MOVE_FORCE > 0
    assert config.JUMP_FORCE > 0


def test_max_charge_time_is_positive():
    assert config.MAX_CHARGE_TIME > 0


@pytest.mark.parametrize(
    "color_name", ["WHITE", "BLACK", "RED", "BLUE", "GREEN", "GRAY", "YELLOW"]
)
def test_colors_are_valid_rgb(color_name):
    color = getattr(config, color_name)
    assert len(color) == 3
    assert all(0 <= c <= 255 for c in color)
