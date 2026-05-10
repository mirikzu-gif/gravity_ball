"""Юнит-тесты Ball: инициализация, регистрация в Space и apply_force."""
import pygame
import pymunk
import pytest

from src.entities.ball import Ball
from src.utils.config import MATERIALS


def test_ball_default_radius(space):
    ball = Ball(100, 200, space=space)
    assert ball.radius == 20


def test_ball_custom_radius(space):
    ball = Ball(0, 0, radius=42, space=space)
    assert ball.radius == 42


def test_ball_position(space):
    ball = Ball(150, 250, space=space)
    assert ball.body.position.x == 150
    assert ball.body.position.y == 250


def test_ball_uses_material_properties(space):
    ball = Ball(0, 0, space=space)
    material = MATERIALS["ball"]
    assert ball.mass == material["mass"]
    assert ball.elasticity == material["elasticity"]
    assert ball.shape.elasticity == material["elasticity"]
    assert ball.shape.friction == material["friction"]


def test_ball_body_mass_matches_material(space):
    ball = Ball(0, 0, space=space)
    assert ball.body.mass == MATERIALS["ball"]["mass"]


def test_ball_shape_is_circle(space):
    ball = Ball(0, 0, radius=15, space=space)
    assert isinstance(ball.shape, pymunk.Circle)
    assert ball.shape.radius == 15


def test_ball_registered_in_space(space):
    ball = Ball(0, 0, space=space)
    assert ball.body in space.bodies
    assert ball.shape in space.shapes


def test_ball_without_space_is_not_registered():
    ball = Ball(0, 0, space=None)
    assert ball.body is not None
    assert ball.shape is not None


def test_apply_force_changes_velocity(space):
    space.gravity = (0, 0)  # отключаем гравитацию для чистоты теста
    ball = Ball(100, 100, space=space)
    initial_velocity = pymunk.Vec2d(*ball.body.velocity)

    ball.apply_force((1000, 0))
    space.step(1 / 60.0)

    assert ball.body.velocity.x > initial_velocity.x


@pytest.mark.parametrize(
    "force,axis,direction",
    [
        ((1000, 0), "x", 1),
        ((-1000, 0), "x", -1),
        ((0, 1000), "y", 1),
        ((0, -1000), "y", -1),
    ],
)
def test_apply_force_direction(space, force, axis, direction):
    space.gravity = (0, 0)
    ball = Ball(100, 100, space=space)

    ball.apply_force(force)
    space.step(1 / 60.0)

    velocity_component = getattr(ball.body.velocity, axis)
    assert velocity_component * direction > 0


def test_moment_of_inertia_is_positive(space):
    ball = Ball(0, 0, space=space)
    assert ball.body.moment > 0


def test_apply_torque_changes_angular_velocity(space):
    space.gravity = (0, 0)
    ball = Ball(100, 100, space=space)

    ball.apply_torque(1000)
    space.step(1 / 60.0)

    assert ball.body.angular_velocity > 0


# ---------------------------------------------------------------------------
# apply_impulse — мгновенное изменение скорости, не зависит от dt
# ---------------------------------------------------------------------------


def test_apply_impulse_changes_velocity_immediately(space):
    """Импульс меняет velocity сразу, без вызова space.step."""
    space.gravity = (0, 0)
    ball = Ball(100, 100, space=space)
    assert ball.body.velocity == pymunk.Vec2d(0, 0)

    ball.apply_impulse((0, -100))

    assert ball.body.velocity.y == pytest.approx(-100 / ball.mass)
    assert ball.body.velocity.x == 0


def test_apply_impulse_velocity_change_is_unaffected_by_dt(space):
    """Δv от импульса — мгновенная и не масштабируется dt последующих шагов."""
    space.gravity = (0, 0)
    # space.damping = 1.0 по умолчанию у pymunk — без сил velocity не должна меняться
    ball = Ball(100, 100, space=space)

    ball.apply_impulse((0, -100))
    v_after_impulse = ball.body.velocity.y

    for _ in range(10):
        space.step(1 / 60.0)

    assert ball.body.velocity.y == pytest.approx(v_after_impulse)


@pytest.mark.parametrize(
    "impulse,axis,direction",
    [
        ((100, 0), "x", 1),
        ((-100, 0), "x", -1),
        ((0, 100), "y", 1),
        ((0, -100), "y", -1),
    ],
)
def test_apply_impulse_direction(space, impulse, axis, direction):
    space.gravity = (0, 0)
    ball = Ball(100, 100, space=space)

    ball.apply_impulse(impulse)

    velocity_component = getattr(ball.body.velocity, axis)
    assert velocity_component * direction > 0


# ---------------------------------------------------------------------------
# draw с переопределением позиции (для интерполяции)
# ---------------------------------------------------------------------------


def test_draw_uses_body_position_by_default(space):
    """Если position=None — используется текущая позиция body."""
    pygame_module = pytest.importorskip("pygame")
    pygame_module.init()
    surface = pygame_module.Surface((200, 200))
    ball = Ball(100, 100, space=space)
    # просто не должно падать
    ball.draw(surface)


def test_draw_falls_back_to_circle_when_no_sprite(monkeypatch, space, tmp_path):
    """Если ассет ball.png отсутствует — используется процедурный круг (drawing call)."""
    from src.utils import assets

    monkeypatch.setattr(assets, "ASSETS_DIR", tmp_path)
    assets.reset_cache()

    surface = pygame.Surface((200, 200))
    ball = Ball(100, 100, space=space)
    ball.draw(surface)  # не должно падать без спрайта


def test_draw_uses_sprite_when_available(monkeypatch, space, tmp_path):
    from src.utils import assets

    monkeypatch.setattr(assets, "ASSETS_DIR", tmp_path)
    assets.reset_cache()

    sprite_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    sprite_surf.fill((123, 45, 67))
    pygame.image.save(sprite_surf, str(tmp_path / "ball.png"))

    target = pygame.Surface((200, 200))
    target.fill((0, 0, 0))
    ball = Ball(100, 100, space=space)
    ball.draw(target)

    # центр мяча должен иметь цвет из спрайта (не чёрный фон)
    px = target.get_at((100, 100))
    assert (px[0], px[1], px[2]) == (123, 45, 67)


def test_draw_uses_selected_skin_sprite_instead_of_default_sprite(
    monkeypatch, space, tmp_path
):
    from src.utils import assets, skins

    monkeypatch.setattr(assets, "ASSETS_DIR", tmp_path)
    assets.reset_cache()

    sprite_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    sprite_surf.fill((123, 45, 67))
    pygame.image.save(sprite_surf, str(tmp_path / "ball.png"))

    skin_dir = tmp_path / "skins"
    skin_dir.mkdir()
    skin_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    skin_surf.fill((245, 245, 245))
    pygame.image.save(skin_surf, str(skin_dir / "pokeball.png"))

    skins.select_skin(1)
    target = pygame.Surface((200, 200))
    target.fill((0, 0, 0))
    ball = Ball(100, 100, space=space)
    ball.draw(target)

    px = target.get_at((100, 100))
    assert (px[0], px[1], px[2]) == skins.get_selected_skin().fill


def test_draw_accepts_override_position(space):
    """Можно нарисовать мяч в произвольной позиции для интерполяции."""
    pygame_module = pytest.importorskip("pygame")
    pygame_module.init()
    surface = pygame_module.Surface((200, 200))
    ball = Ball(100, 100, space=space)
    ball.draw(surface, position=(50.5, 75.5))


def test_draw_accepts_vec2d_position(space):
    """Vec2d должен работать как position."""
    pygame_module = pytest.importorskip("pygame")
    pygame_module.init()
    surface = pygame_module.Surface((200, 200))
    ball = Ball(100, 100, space=space)
    ball.draw(surface, position=pymunk.Vec2d(60, 80))


def test_draw_accepts_rotated_ball(space):
    pygame_module = pytest.importorskip("pygame")
    pygame_module.init()
    surface = pygame_module.Surface((200, 200))
    ball = Ball(100, 100, space=space)
    ball.body.angle = 0.75
    ball.draw(surface)
