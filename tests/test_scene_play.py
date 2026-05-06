"""Тесты GameScene."""
import pygame
import pytest

from src.game.jump_controller import JumpState
from src.scenes.play import JUMP_IMPULSE, GameScene
from src.scenes.win import WinScene
from src.utils.config import FIXED_DT, JUMP_FORCE
from src.utils.level import LEVELS


def _ev(type_, **attrs):
    return pygame.event.Event(type_, **attrs)


def _put_ball_on_first_level_platform(scene):
    """Кладёт мяч на широкую платформу 1-го уровня (500, 620, 800, 20).

    Платформа top y=610. Мяч center y=595 → нижний probe (radius+1=21)
    в y=616 — внутри платформы [610, 630].
    """
    scene._ball.body.position = (500, 595)
    scene._ball.body.velocity = (0, 0)


def test_jump_impulse_derivation():
    """JUMP_IMPULSE = JUMP_FORCE * FIXED_DT — преобразование per-frame силы в импульс."""
    assert JUMP_IMPULSE == pytest.approx(JUMP_FORCE * FIXED_DT)


def test_init_creates_world_with_objects():
    scene = GameScene()
    assert scene._space is not None
    assert scene._ball is not None
    assert scene._goal is not None
    assert len(scene._platforms) >= 1
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


def test_render_accepts_alpha_for_interpolation():
    scene = GameScene()
    screen = pygame.Surface((1000, 700))
    scene.render(screen, alpha=0.0)
    scene.render(screen, alpha=0.5)
    scene.render(screen, alpha=0.99)


def test_prev_ball_pos_initialized_to_start():
    scene = GameScene()
    assert scene._prev_ball_pos.x == scene._ball.body.position.x
    assert scene._prev_ball_pos.y == scene._ball.body.position.y


def test_prev_ball_pos_updated_before_step():
    """После fixed_update prev_ball_pos должна равняться позиции ДО шага."""
    scene = GameScene()
    # сделаем мяч заметно подвижным
    scene._ball.body.position = (200, 580)
    scene._ball.body.velocity = (0, 0)

    pos_before = (scene._ball.body.position.x, scene._ball.body.position.y)
    scene.fixed_update(FIXED_DT)

    # prev записывается в начале fixed_update — равна позиции до шага
    assert scene._prev_ball_pos.x == pos_before[0]
    assert scene._prev_ball_pos.y == pos_before[1]


def test_handle_quit_posts_pygame_quit():
    scene = GameScene()
    scene.handle_event(_ev(pygame.QUIT))
    posted = [e for e in pygame.event.get() if e.type == pygame.QUIT]
    assert len(posted) == 1


def test_space_keydown_starts_jump_charging_when_on_ground():
    """Мяч стоит на платформе → нажатие пробела стартует зарядку."""
    scene = GameScene()
    _put_ball_on_first_level_platform(scene)

    assert scene._jump.state == JumpState.IDLE
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_SPACE))
    assert scene._jump.state == JumpState.CHARGING


def test_space_keyup_releases_jump_when_charging_on_ground():
    scene = GameScene()
    _put_ball_on_first_level_platform(scene)

    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_SPACE))
    initial_velocity_y = scene._ball.body.velocity.y

    scene.handle_event(_ev(pygame.KEYUP, key=pygame.K_SPACE))

    # импульс направлен вверх — velocity.y становится отрицательнее
    assert scene._ball.body.velocity.y < initial_velocity_y


def test_goal_touch_on_non_last_level_transitions_to_next_level():
    """Касание цели на уровне < последнего → переход в следующий GameScene."""
    assert len(LEVELS) >= 2, "тест требует ≥ 2 уровней"
    scene = GameScene(level_index=0)
    goal = scene.level_def.goal
    scene._ball.body.position = (goal.x, goal.y)

    scene.fixed_update(FIXED_DT)

    assert isinstance(scene.next_scene, GameScene)
    assert scene.next_scene.level_index == 1


def test_goal_touch_on_last_level_transitions_to_win_scene():
    last_index = len(LEVELS) - 1
    scene = GameScene(level_index=last_index)
    goal = scene.level_def.goal
    scene._ball.body.position = (goal.x, goal.y)

    scene.fixed_update(FIXED_DT)

    assert isinstance(scene.next_scene, WinScene)


def test_no_goal_touch_keeps_scene():
    scene = GameScene()
    scene.fixed_update(FIXED_DT)
    assert scene.next_scene is None


def test_invalid_level_index_raises():
    with pytest.raises(ValueError):
        GameScene(level_index=-1)
    with pytest.raises(ValueError):
        GameScene(level_index=len(LEVELS))


def test_default_level_index_is_zero():
    scene = GameScene()
    assert scene.level_index == 0


def test_r_restarts_current_level():
    scene = GameScene(level_index=1)
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_r))
    assert isinstance(scene.next_scene, GameScene)
    assert scene.next_scene.level_index == 1
    assert scene.next_scene is not scene


def test_r_does_not_pass_to_input_handler():
    """R не должен затрагивать движение/прыжок."""
    from src.game.jump_controller import JumpState

    scene = GameScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_r))
    assert scene._jump.state == JumpState.IDLE


# ---------------------------------------------------------------------------
# Таймер
# ---------------------------------------------------------------------------


def test_timer_starts_at_zero():
    scene = GameScene()
    assert scene._elapsed == 0.0
    assert scene._total_elapsed_before == 0.0


def test_timer_accumulates_in_fixed_update():
    scene = GameScene()
    scene.fixed_update(FIXED_DT)
    scene.fixed_update(FIXED_DT)
    assert scene._elapsed == pytest.approx(2 * FIXED_DT)


def test_total_elapsed_carries_to_next_level():
    """Завершение уровня → следующий GameScene получает накопленное время."""
    scene = GameScene(level_index=0)
    # пусть прошла секунда
    for _ in range(60):
        scene.fixed_update(FIXED_DT)
    elapsed_before_goal = scene._elapsed

    # перенесём мяч в цель и запустим шаг
    goal = scene.level_def.goal
    scene._ball.body.position = (goal.x, goal.y)
    scene.fixed_update(FIXED_DT)

    assert isinstance(scene.next_scene, GameScene)
    assert scene.next_scene._total_elapsed_before == pytest.approx(
        elapsed_before_goal + FIXED_DT
    )


def test_total_elapsed_carries_to_win_scene():
    last_index = len(LEVELS) - 1
    scene = GameScene(level_index=last_index, total_elapsed=5.0)
    goal = scene.level_def.goal
    scene._ball.body.position = (goal.x, goal.y)
    scene.fixed_update(FIXED_DT)

    assert isinstance(scene.next_scene, WinScene)
    assert scene.next_scene.total_time == pytest.approx(5.0 + FIXED_DT)


def test_goal_reached_records_level_best_time():
    from src.utils import best_times

    scene = GameScene(level_index=0)
    # имитируем длительное прохождение
    for _ in range(60):
        scene.fixed_update(FIXED_DT)
    elapsed = scene._elapsed

    goal = scene.level_def.goal
    scene._ball.body.position = (goal.x, goal.y)
    scene.fixed_update(FIXED_DT)

    assert best_times.best_for_level(scene.level_def.name) == pytest.approx(
        elapsed + FIXED_DT
    )


def test_r_resets_level_timer_but_keeps_total():
    scene = GameScene(level_index=0, total_elapsed=10.0)
    for _ in range(60):
        scene.fixed_update(FIXED_DT)

    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_r))

    new_scene = scene.next_scene
    assert isinstance(new_scene, GameScene)
    assert new_scene._elapsed == 0.0
    assert new_scene._total_elapsed_before == 10.0  # время прошлых уровней цело


def test_scene_uses_level_def_ball_start():
    last_index = len(LEVELS) - 1
    scene = GameScene(level_index=last_index)
    assert scene._ball.body.position.x == LEVELS[last_index].ball_start[0]
    assert scene._ball.body.position.y == LEVELS[last_index].ball_start[1]


@pytest.mark.parametrize("level_index", range(len(LEVELS)))
def test_render_does_not_crash_for_each_level(level_index):
    scene = GameScene(level_index=level_index)
    screen = pygame.Surface((1000, 700))
    scene.render(screen)
