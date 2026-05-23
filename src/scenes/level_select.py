"""LevelSelectScene — список уровней с превью и лучшим временем."""
import pygame

from ..utils import best_times, fonts
from ..utils.config import BLACK, HEIGHT, WHITE, WIDTH
from ..utils.level import LEVELS
from .base import Scene
from .level_preview import make_preview


def _format_time(secs: float) -> str:
    minutes, seconds = divmod(secs, 60)
    return f"{int(minutes):02d}:{seconds:05.2f}"


def is_level_unlocked(index: int) -> bool:
    """Первый уровень открыт всегда, остальные — после прохождения всех предыдущих."""
    if index <= 0:
        return True
    if index >= len(LEVELS):
        return False
    for prev_index in range(index):
        if best_times.best_for_level(LEVELS[prev_index].name) is None:
            return False
    return True


class LevelSelectScene(Scene):
    """Список уровней. Стрелки ↑↓ — выбор; Enter — играть; Esc/M — назад."""

    PREVIEW_SIZE = (220, 154)
    ROW_HEIGHT = 180
    LIST_TOP = 130
    VISIBLE_ROWS = 3

    def __init__(self, selected: int = 0) -> None:
        super().__init__()
        if not 0 <= selected < len(LEVELS):
            selected = 0
        self.selected = selected

        self._title_font = fonts.title(28)
        self._row_font = fonts.ui(22)
        self._meta_font = fonts.ui(16)
        self._hint_font = fonts.ui(16)

        self._title = self._title_font.render("Выбери уровень", True, BLACK)
        self._hint = self._hint_font.render(
            "↑↓ — выбор    Enter — играть    Esc — назад", True, BLACK
        )

        # Превью кэшируются по индексу — рисуются один раз.
        self._previews = {
            i: make_preview(LEVELS[i], self.PREVIEW_SIZE) for i in range(len(LEVELS))
        }

    # ------------------------------------------------------------------
    # Scene API
    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_UP, pygame.K_w):
            self.selected = (self.selected - 1) % len(LEVELS)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected = (self.selected + 1) % len(LEVELS)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if not is_level_unlocked(self.selected):
                return
            from .play import GameScene

            self.next_scene = GameScene(level_index=self.selected)
        elif event.key in (pygame.K_ESCAPE, pygame.K_m):
            from .menu import MenuScene

            self.next_scene = MenuScene()
        elif event.key == pygame.K_q:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def render(self, screen: pygame.Surface, alpha: float = 1.0) -> None:
        screen.fill(WHITE)

        title_rect = self._title.get_rect(center=(WIDTH // 2, 60))
        screen.blit(self._title, title_rect)

        # Рисуем окно из нескольких строк вокруг выбранного уровня.
        max_start = max(0, len(LEVELS) - self.VISIBLE_ROWS)
        scroll_start = min(
            max(0, self.selected - self.VISIBLE_ROWS // 2),
            max_start,
        )
        scroll_end = min(len(LEVELS), scroll_start + self.VISIBLE_ROWS)

        for row, i in enumerate(range(scroll_start, scroll_end)):
            y = self.LIST_TOP + row * self.ROW_HEIGHT
            preview = self._previews[i]
            unlocked = is_level_unlocked(i)

            # Highlight активной строки
            if i == self.selected:
                hl_rect = pygame.Rect(
                    50, y - 10, WIDTH - 100, self.PREVIEW_SIZE[1] + 20
                )
                bg = (255, 240, 200) if unlocked else (225, 228, 232)
                border = (220, 160, 40) if unlocked else (140, 145, 152)
                pygame.draw.rect(screen, bg, hl_rect)
                pygame.draw.rect(screen, border, hl_rect, 3)

            # Превью (по центру окна)
            preview_rect = preview.get_rect(
                topleft=(WIDTH // 2 - self.PREVIEW_SIZE[0] // 2, y)
            )
            screen.blit(preview, preview_rect)
            if not unlocked:
                overlay = pygame.Surface(self.PREVIEW_SIZE, pygame.SRCALPHA)
                overlay.fill((235, 238, 242, 160))
                screen.blit(overlay, preview_rect)

            # Слева — номер и имя
            text_color = BLACK if unlocked else (125, 130, 138)
            label = self._row_font.render(
                f"{i + 1}. {LEVELS[i].name}", True, text_color
            )
            label_rect = label.get_rect(
                midright=(WIDTH // 2 - self.PREVIEW_SIZE[0] // 2 - 20,
                          y + self.PREVIEW_SIZE[1] // 2 - 10)
            )
            screen.blit(label, label_rect)

            # Справа — лучшее время
            best = best_times.best_for_level(LEVELS[i].name)
            if not unlocked:
                time_text = "Закрыт"
            else:
                time_text = (
                    f"Лучшее: {_format_time(best)}" if best is not None else "—"
                )
            time_label = self._meta_font.render(time_text, True, text_color)
            time_rect = time_label.get_rect(
                midleft=(WIDTH // 2 + self.PREVIEW_SIZE[0] // 2 + 20,
                         y + self.PREVIEW_SIZE[1] // 2 - 10)
            )
            screen.blit(time_label, time_rect)

        hint_rect = self._hint.get_rect(center=(WIDTH // 2, HEIGHT - 30))
        screen.blit(self._hint, hint_rect)
