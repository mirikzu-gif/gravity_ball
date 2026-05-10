"""Тесты PauseScene."""
import pygame

from src.scenes.menu import MenuScene
from src.scenes.pause import PauseScene
from src.scenes.play import GameScene


def _ev(type_, **attrs):
    return pygame.event.Event(type_, **attrs)


def _put_ball_on_level_platform(scene):
    radius = scene._ball.radius
    for platform in scene.level_def.platforms:
        top = platform.y - platform.height / 2
        y = top - radius + 5
        candidates = (
            platform.x,
            platform.x - platform.width / 4,
            platform.x + platform.width / 4,
        )
        for x in candidates:
            blocked = False
            for obstacle in scene.level_def.obstacles:
                left = obstacle.x - obstacle.width / 2 - radius
                right = obstacle.x + obstacle.width / 2 + radius
                upper = obstacle.y - obstacle.height / 2 - radius
                lower = obstacle.y + obstacle.height / 2 + radius
                if left <= x <= right and upper <= y <= lower:
                    blocked = True
                    break
            if not blocked:
                scene._ball.body.position = (x, y)
                scene._ball.body.velocity = (0, 0)
                return
    raise AssertionError("нет свободной платформы для теста")


def test_pause_keeps_game_reference():
    game = GameScene()
    pause = PauseScene(game)
    assert pause._game is game


def test_p_resumes_game():
    game = GameScene()
    pause = PauseScene(game)
    pause.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_p))
    assert pause.next_scene is game


def test_escape_resumes_game():
    game = GameScene()
    pause = PauseScene(game)
    pause.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert pause.next_scene is game


def test_enter_resumes_game():
    game = GameScene()
    pause = PauseScene(game)
    pause.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert pause.next_scene is game


def test_m_goes_to_menu():
    game = GameScene()
    pause = PauseScene(game)
    pause.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_m))
    assert isinstance(pause.next_scene, MenuScene)


def test_q_posts_quit():
    game = GameScene()
    pause = PauseScene(game)
    pause.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_q))
    posted = [e for e in pygame.event.get() if e.type == pygame.QUIT]
    assert len(posted) == 1


def test_unrelated_key_does_nothing():
    game = GameScene()
    pause = PauseScene(game)
    pause.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_a))
    assert pause.next_scene is None


def test_render_does_not_crash():
    game = GameScene()
    pause = PauseScene(game)
    screen = pygame.Surface((1000, 700))
    pause.render(screen)
    pause.render(screen, alpha=0.5)


# ---------------------------------------------------------------------------
# Интеграция: GameScene создаёт PauseScene по P/Esc
# ---------------------------------------------------------------------------


def test_game_p_key_creates_pause_scene():
    scene = GameScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_p))
    assert isinstance(scene.next_scene, PauseScene)
    assert scene.next_scene._game is scene


def test_game_escape_creates_pause_scene():
    scene = GameScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert isinstance(scene.next_scene, PauseScene)


def test_game_p_does_not_affect_jump_controller():
    """Нажатие P не должно случайно зайти в JumpController."""
    from src.game.jump_controller import JumpState

    scene = GameScene()
    # ставим мяч на платформу и убедимся что в IDLE
    scene._ball.body.position = (500, 595)
    scene._ball.body.velocity = (0, 0)
    assert scene._jump.state == JumpState.IDLE

    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_p))

    assert scene._jump.state == JumpState.IDLE  # пробел был бы CHARGING — P нет


def test_game_pause_clears_held_movement_keys():
    scene = GameScene()
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_RIGHT))
    assert scene._input.get_movement() == (1.0, 0.0)

    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_p))

    assert scene._input.held_keys == frozenset()
    assert scene._input.get_movement() == (0.0, 0.0)


def test_game_pause_cancels_charged_jump():
    from src.game.jump_controller import JumpState

    scene = GameScene()
    _put_ball_on_level_platform(scene)
    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_SPACE))
    assert scene._jump.state == JumpState.CHARGING

    scene.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_p))

    assert scene._jump.state == JumpState.IDLE
    assert scene._jump.space_pressed is False


def test_resume_clears_game_input_state():
    game = GameScene()
    game.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_RIGHT))
    pause = PauseScene(game)

    pause.handle_event(_ev(pygame.KEYDOWN, key=pygame.K_p))

    assert pause.next_scene is game
    assert game._input.held_keys == frozenset()
