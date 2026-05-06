"""Тесты PauseScene."""
import pygame

from src.scenes.menu import MenuScene
from src.scenes.pause import PauseScene
from src.scenes.play import GameScene


def _ev(type_, **attrs):
    return pygame.event.Event(type_, **attrs)


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