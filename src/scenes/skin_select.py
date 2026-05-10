"""SkinSelectScene — выбор внешнего вида мяча."""
from typing import Optional

import pygame

from ..utils import assets, fonts, skins
from ..utils.config import BLACK, HEIGHT, WHITE, WIDTH
from .base import Scene


class SkinSelectScene(Scene):
    """Выбор скина. Стрелки — выбор; Enter — применить; Esc/M — назад."""

    CARD_COLUMNS = 4
    CARD_WIDTH = 150
    CARD_HEIGHT = 190
    CARD_GAP = 18
    ROW_GAP = 18
    CARD_TOP = 150

    def __init__(self, selected: Optional[int] = None) -> None:
        super().__init__()
        current = skins.get_selected_index()
        if selected is None or not 0 <= selected < skins.skin_count():
            selected = current
        self.selected = selected

        self._title_font = fonts.title(28)
        self._card_font = fonts.ui(12)
        self._meta_font = fonts.ui(14)
        self._hint_font = fonts.ui(16)

        self._title = self._title_font.render("Выбери скин", True, BLACK)
        self._hint = self._hint_font.render(
            "←→ — выбор    Enter — применить    Esc — назад", True, BLACK
        )
        self._sprites = assets.get_sprite_manager()

    # ------------------------------------------------------------------
    # Scene API
    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_UP, pygame.K_a, pygame.K_w):
                self.selected = (self.selected - 1) % skins.skin_count()
            elif event.key in (
                pygame.K_RIGHT,
                pygame.K_DOWN,
                pygame.K_d,
                pygame.K_s,
            ):
                self.selected = (self.selected + 1) % skins.skin_count()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._apply_and_return()
            elif event.key in (pygame.K_ESCAPE, pygame.K_m):
                self._return_to_menu()
            elif event.key == pygame.K_q:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        if event.type == pygame.MOUSEMOTION:
            hovered = self._skin_at_pos(event.pos)
            if hovered is not None:
                self.selected = hovered
        elif (
            event.type == pygame.MOUSEBUTTONDOWN
            and getattr(event, "button", None) == 1
        ):
            clicked = self._skin_at_pos(event.pos)
            if clicked is not None:
                self.selected = clicked
                self._apply_and_return()

    def render(self, screen: pygame.Surface, alpha: float = 1.0) -> None:
        screen.fill(WHITE)

        title_rect = self._title.get_rect(center=(WIDTH // 2, 70))
        screen.blit(self._title, title_rect)

        for i, skin in enumerate(skins.SKINS):
            rect = self._card_rect(i)
            is_cursor = i == self.selected
            is_active = i == skins.get_selected_index()

            bg = (255, 246, 220) if is_cursor else (242, 246, 250)
            border = (220, 160, 40) if is_cursor else (160, 170, 185)
            pygame.draw.rect(screen, bg, rect)
            pygame.draw.rect(screen, border, rect, 3 if is_cursor else 2)

            self._draw_skin_sample(screen, skin, rect.centerx, rect.y + 62)

            name = self._card_font.render(skin.name, True, BLACK)
            name_rect = name.get_rect(center=(rect.centerx, rect.y + 122))
            screen.blit(name, name_rect)

            if is_active:
                active = self._meta_font.render("Выбран", True, (0, 110, 40))
                active_rect = active.get_rect(center=(rect.centerx, rect.y + 155))
                screen.blit(active, active_rect)

        hint_rect = self._hint.get_rect(center=(WIDTH // 2, HEIGHT - 34))
        screen.blit(self._hint, hint_rect)

    # ------------------------------------------------------------------
    # Внутреннее
    # ------------------------------------------------------------------
    def _apply_and_return(self) -> None:
        skins.select_skin(self.selected)
        self._return_to_menu()

    def _return_to_menu(self) -> None:
        from .menu import MenuScene

        self.next_scene = MenuScene()

    def _card_rect(self, index: int) -> pygame.Rect:
        col = index % self.CARD_COLUMNS
        row = index // self.CARD_COLUMNS
        visible_columns = min(self.CARD_COLUMNS, skins.skin_count())
        total_width = (
            visible_columns * self.CARD_WIDTH
            + (visible_columns - 1) * self.CARD_GAP
        )
        x = (WIDTH - total_width) // 2 + col * (self.CARD_WIDTH + self.CARD_GAP)
        y = self.CARD_TOP + row * (self.CARD_HEIGHT + self.ROW_GAP)
        return pygame.Rect(x, y, self.CARD_WIDTH, self.CARD_HEIGHT)

    def _skin_at_pos(self, pos) -> Optional[int]:
        for i in range(skins.skin_count()):
            if self._card_rect(i).collidepoint(pos):
                return i
        return None

    def _draw_skin_sample(
        self,
        screen: pygame.Surface,
        skin: skins.Skin,
        x: int,
        y: int,
    ) -> None:
        radius = 36
        sprite = self._sprites.get_scaled(skin.sprite_id, (radius * 2, radius * 2))
        if sprite is not None:
            rect = sprite.get_rect(center=(x, y))
            screen.blit(sprite, rect)
            return

        center = (x, y)
        fill_center = (x - radius // 5, y + radius // 5)
        highlight = (x - radius // 3, y - radius // 3)

        pygame.draw.circle(screen, skin.shade, center, radius)
        pygame.draw.circle(screen, skin.fill, fill_center, radius - 8)
        pygame.draw.circle(screen, skin.highlight, highlight, radius // 3)
        pygame.draw.circle(screen, skin.outline, center, radius, 3)
