"""MenuScene — заглавный экран."""
import pygame

from ..utils.config import BLACK, HEIGHT, WHITE, WIDTH
from .base import Scene


class MenuScene(Scene):
    """Стартовый экран. Enter/Space → играть; Esc/Q → закрыть приложение."""

    def __init__(self) -> None:
        super().__init__()
        self._title_font = pygame.font.Font(None, 96)
        self._hint_font = pygame.font.Font(None, 32)

        self._title = self._title_font.render("Gravity Ball", True, BLACK)
        self._hint = self._hint_font.render(
            "Enter — играть    Esc — выход", True, BLACK
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            from .play import GameScene

            self.next_scene = GameScene()
        elif event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def render(self, screen: pygame.Surface, alpha: float = 1.0) -> None:
        screen.fill(WHITE)
        title_rect = self._title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        hint_rect = self._hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        screen.blit(self._title, title_rect)
        screen.blit(self._hint, hint_rect)
