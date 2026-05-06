"""PauseScene — оверлей паузы поверх замороженной GameScene."""
import pygame

from ..utils.config import BLACK, HEIGHT, WIDTH
from .base import Scene


class PauseScene(Scene):
    """Пауза с сохранением состояния игры.

    Хранит ссылку на GameScene и возвращает её при resume — pymunk-пространство
    и позиции остаются нетронутыми, физика просто не шагается, пока пауза активна.
    Рендер: рисуем застывшую игру, затем полупрозрачный затемняющий слой
    и текст «ПАУЗА».
    """

    def __init__(self, paused_game: Scene) -> None:
        super().__init__()
        self._game = paused_game

        self._title_font = pygame.font.Font(None, 96)
        self._hint_font = pygame.font.Font(None, 32)

        self._title = self._title_font.render("Пауза", True, (255, 255, 255))
        self._hint = self._hint_font.render(
            "P / Esc — продолжить    M — меню    Q — выход",
            True,
            (240, 240, 240),
        )

        self._overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 140))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_p, pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
            # resume — возвращаемся в ту же GameScene
            self.next_scene = self._game
        elif event.key == pygame.K_m:
            from .menu import MenuScene

            self.next_scene = MenuScene()
        elif event.key == pygame.K_q:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def render(self, screen: pygame.Surface, alpha: float = 1.0) -> None:
        # alpha=1.0: используем последнее физ. состояние, без интерполяции, чтобы
        # картинка не «дрейфовала» во время паузы.
        self._game.render(screen, alpha=1.0)
        screen.blit(self._overlay, (0, 0))
        title_rect = self._title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        hint_rect = self._hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        screen.blit(self._title, title_rect)
        screen.blit(self._hint, hint_rect)
