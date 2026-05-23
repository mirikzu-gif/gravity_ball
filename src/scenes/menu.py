"""MenuScene — заглавный экран."""
from typing import Optional

import pygame

from ..utils import audio, fonts
from ..utils.config import BLACK, HEIGHT, WHITE, WIDTH
from .base import Scene


class MenuScene(Scene):
    """Стартовый экран. Enter/Space → выбранный раздел; Esc/Q → выход."""

    LEVELS_INDEX = 0
    SKINS_INDEX = 1
    EDITOR_INDEX = 2
    BUTTONS = ("Уровни", "Скины", "Редактор")
    BUTTON_WIDTH = 300
    BUTTON_HEIGHT = 64
    BUTTON_GAP = 18

    def __init__(self) -> None:
        super().__init__()
        audio.stop_background()
        self.selected = self.LEVELS_INDEX

        self._title_font = fonts.title(46)
        self._button_font = fonts.ui(26)
        self._hint_font = fonts.ui(22)

        self._title = self._title_font.render("Gravity Ball", True, BLACK)
        self._hint = self._hint_font.render(
            "↑↓ — выбор    Enter — открыть    Esc — выход", True, BLACK
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.BUTTONS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.BUTTONS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._open_selected()
            elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        if event.type == pygame.MOUSEMOTION:
            hovered = self._button_at_pos(event.pos)
            if hovered is not None:
                self.selected = hovered
        elif (
            event.type == pygame.MOUSEBUTTONDOWN
            and getattr(event, "button", None) == 1
        ):
            clicked = self._button_at_pos(event.pos)
            if clicked is not None:
                self.selected = clicked
                self._open_selected()

    def render(self, screen: pygame.Surface, alpha: float = 1.0) -> None:
        screen.fill(WHITE)
        title_rect = self._title.get_rect(center=(WIDTH // 2, 190))
        screen.blit(self._title, title_rect)

        for i, label in enumerate(self.BUTTONS):
            self._draw_button(screen, i, label)

        hint_rect = self._hint.get_rect(center=(WIDTH // 2, HEIGHT - 80))
        screen.blit(self._hint, hint_rect)

    # ------------------------------------------------------------------
    # Внутреннее
    # ------------------------------------------------------------------
    def _open_selected(self) -> None:
        if self.selected == self.LEVELS_INDEX:
            from .level_select import LevelSelectScene

            self.next_scene = LevelSelectScene()
        elif self.selected == self.SKINS_INDEX:
            from .skin_select import SkinSelectScene

            self.next_scene = SkinSelectScene()
        else:
            from .level_editor import LevelEditorScene

            self.next_scene = LevelEditorScene()

    def _button_rect(self, index: int) -> pygame.Rect:
        total_height = len(self.BUTTONS) * self.BUTTON_HEIGHT
        total_height += (len(self.BUTTONS) - 1) * self.BUTTON_GAP
        y = (HEIGHT - total_height) // 2 + 35
        y += index * (self.BUTTON_HEIGHT + self.BUTTON_GAP)
        return pygame.Rect(
            (WIDTH - self.BUTTON_WIDTH) // 2,
            y,
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT,
        )

    def _button_at_pos(self, pos) -> Optional[int]:
        for i in range(len(self.BUTTONS)):
            if self._button_rect(i).collidepoint(pos):
                return i
        return None

    def _draw_button(
        self,
        screen: pygame.Surface,
        index: int,
        label: str,
    ) -> None:
        rect = self._button_rect(index)
        is_selected = index == self.selected
        bg = (255, 246, 220) if is_selected else (242, 246, 250)
        border = (220, 160, 40) if is_selected else (160, 170, 185)

        pygame.draw.rect(screen, bg, rect)
        pygame.draw.rect(screen, border, rect, 3 if is_selected else 2)

        text = self._button_font.render(label, True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
