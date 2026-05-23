"""WinScene — финальный экран после прохождения всех уровней."""
import pygame

from ..utils import audio, best_times, fonts
from ..utils.config import BLACK, HEIGHT, WHITE, WIDTH
from .base import Scene


def _fmt(secs: float) -> str:
    minutes, seconds = divmod(secs, 60)
    return f"{int(minutes):02d}:{seconds:05.2f}"


class WinScene(Scene):
    """Экран после прохождения последнего уровня. Enter — заново с первого; Esc/Q — выход."""

    def __init__(self, total_time: float = 0.0, record_total: bool = True) -> None:
        super().__init__()
        audio.stop_background()
        self.total_time = total_time
        self.record_total = record_total

        previous_best = best_times.best_total()
        if record_total:
            # Если время лучше предыдущего рекорда — обновляем; запоминаем для UI.
            self.is_new_record = best_times.record_total(total_time)
            self.best_total = previous_best if not self.is_new_record else total_time
        else:
            self.is_new_record = False
            self.best_total = previous_best

        self._title_font = fonts.title(28)
        self._time_font = fonts.ui(26)
        self._hint_font = fonts.ui(20)

        self._title = self._title_font.render(
            "Все уровни пройдены!", True, (0, 120, 0)
        )
        self._time_label = self._time_font.render(
            f"Общее время: {_fmt(total_time)}",
            True,
            BLACK,
        )
        if self.is_new_record:
            self._record_label = self._hint_font.render(
                "★ Новый рекорд! ★", True, (200, 100, 0)
            )
        elif not self.record_total:
            self._record_label = self._hint_font.render(
                "Общий рекорд считается при старте с первого уровня",
                True,
                BLACK,
            )
        elif self.best_total is not None:
            self._record_label = self._hint_font.render(
                f"Лучшее время: {_fmt(self.best_total)}", True, BLACK
            )
        else:
            self._record_label = None

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
        title_rect = self._title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        time_rect = self._time_label.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
        screen.blit(self._title, title_rect)
        screen.blit(self._time_label, time_rect)

        if self._record_label is not None:
            rec_rect = self._record_label.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 + 40)
            )
            screen.blit(self._record_label, rec_rect)

        hint_rect = self._hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        screen.blit(self._hint, hint_rect)
