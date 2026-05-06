"""WinScene — финальный экран после прохождения всех уровней."""
import pygame

from ..utils.config import BLACK, HEIGHT, WHITE, WIDTH
from .base import Scene


class WinScene(Scene):
    """Экран после прохождения последнего уровня. Enter — заново с первого; Esc/Q — выход."""

    def __init__(self) -> None:
        super().__init__()
        self._title_font = pygame.font.Font(None, 72)
        self._hint_font = pygame.font.Font(None, 32)

        self._title = self._title_font.render(
            "Все уровни пройдены!", True, (0, 120, 0)
        )
        self._hint = self._hint_font.render(
            "Enter — играть заново    Esc — выход", True, BLACK
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            from .play import GameScene

            self.next_scene = GameScene(level_index=0)
        elif event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def render(self, screen: pygame.Surface, alpha: float = 1.0) -> None:
        screen.fill(WHITE)
        title_rect = self._title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        hint_rect = self._hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        screen.blit(self._title, title_rect)
        screen.blit(self._hint, hint_rect)
