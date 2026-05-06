"""Тесты GameScene."""
import pygame
import pytest

from src.game.jump_controller import JumpState
from src.scenes.play import JUMP_IMPULSE, GameScene
from src.scenes.win import WinScene
from src.utils.config import FIXED_DT, JUMP_FORCE


def _ev(type_, **attrs):
    return pygame.event.Event(type_, **attrs)


def _put_ball_on_platform(scene):
    """Кладёт мяч на верхнюю платформу (200, 600) с лёгким перекрытием.

    Платформа: y ∈ [590, 610]. Мяч center y=580 → нижний probe (radius+1=21)
    окажется в y=601, гарантированно внутри платформы.
    """
    scene._ball.body.position = (200, 580)
    scene._ball.body.velocity = (0, 0)


def test_jump_impulse_derivation():
    """JUMP_IMPULSE = JUMP_FORCE * FIXED_DT — преобразование per-frame силы в импульс."""
    assert JUMP_IMPULSE == pytest.approx(JUMP_FORCE * FIXED_DT)


def test_init_creates_world_with_objects():
    scene = GameScene()
    assert scene._space is not None
    assert scene._ball is not None
    assert scene._goal is not None
    assert len(scene._platforms) == 5
    assert scene._ball.shape in scene._space.shapes


def test_fixed_update_advances_physics():
    scene = GameScene()
    initial_y = scene._ball.body.position.y

    for _ in range(60):  # 1 секунда симуляции
        scene.fixed_update(FIXED_DT)

    # должен упасть под гравитацией
    assert scene._ball.body.position.y > initial_y


def test_render_does_not_crash():
    scene = GameScene()
    screen = pygame.Surface((1000, 700))
    scene.render(screen)


def test_handle_quit_posts_pygame_quit():
    scene = GameScene()
    scene.handle_event(_ev(pygame.QUIT))
    posted = [e for e in pygame.event.get() if e.type == pygame.QUIT]
    assert len(posted) == 1


def test_space_keydown_starts_jump_charging_when_on_ground():
    """Мяч стоит на платформе → нажатие пробела стартует зарядку."""
    scene = GameScene()
    _put_ball_on_platform(scene)

    assert scene._jump.state == JumpState.IDLE
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_SPACE))
    assert scene._jump.state == JumpState.CHARGING


def test_space_keyup_releases_jump_when_charging_on_ground():
    scene = GameScene()
    _put_ball_on_platform(scene)

    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_SPACE))
    initial_velocity_y = scene._ball.body.velocity.y

    scene.handle_event(_ev(pygame.KEYUP, key=pygame.K_SPACE))

    # импульс направлен вверх — velocity.y становится отрицательнее
    assert scene._ball.body.velocity.y < initial_velocity_y


def test_goal_touch_transitions_to_win_scene():
    """Если мяч телепортировать в Goal и сделать шаг — сцена сменится."""
    scene = GameScene()
    # Goal в (880, 350) — переносим мяч прямо туда
    scene._ball.body.position = (880, 350)

    scene.fixed_update(FIXED_DT)

    assert isinstance(scene.next_scene, WinScene)


def test_no_goal_touch_keeps_scene():
    scene = GameScene()
    scene.fixed_update(FIXED_DT)
    assert scene.next_scene is None
