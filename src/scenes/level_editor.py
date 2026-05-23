"""In-game custom level editor scene.

The standalone editor in tools/level_editor.py remains the developer tool for
campaign levels. This scene only edits local custom levels, so campaign progress
and speedrun records cannot be changed from the player-facing UI.
"""
from typing import List, Optional, Tuple

import pygame

from ..utils import fonts
from ..utils import level as level_utils
from ..utils.config import BLACK, HEIGHT, WHITE, WIDTH
from .base import Scene
from tools import level_editor as editor_model


CANVAS_RECT = pygame.Rect(20, 92, 720, 504)
PANEL_RECT = pygame.Rect(760, 92, 220, 504)
MAJOR_GRID = editor_model.GRID * 5
CUSTOM_LEVELS_DIR = editor_model.PROJECT_ROOT / "custom_levels"
CUSTOM_MANIFEST_PATH = CUSTOM_LEVELS_DIR / "manifest.json"
DEFAULT_LEVEL_ID = "level_001"


class LevelEditorScene(Scene):
    """Player-facing editor embedded in the game scene system."""

    def __init__(self, selected: int = 0) -> None:
        super().__init__()
        self.level_ids = self._load_or_create_catalog()

        if not 0 <= selected < len(self.level_ids):
            selected = 0
        self.index = selected
        self.path = self._path_for_index(self.index)
        self.draft = editor_model.load_level_draft(self.path)

        self.mode = "select"
        self.selection: Optional[editor_model.Selection] = None
        self.dragging = False
        self.dirty = False
        self.message = "Готово"

        self._title_font = fonts.title(28)
        self._panel_font = fonts.ui(18)
        self._small_font = fonts.ui(14)
        self._tiny_font = fonts.ui(12)
        self._title = self._title_font.render("Мои уровни", True, BLACK)

    # ------------------------------------------------------------------
    # Scene API
    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            self._handle_key(event)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", None) == 1:
            self._mouse_down(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and getattr(event, "button", None) == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._drag_to(event.pos)

    def render(self, screen: pygame.Surface, alpha: float = 1.0) -> None:
        screen.fill(WHITE)
        title_rect = self._title.get_rect(center=(WIDTH // 2, 44))
        screen.blit(self._title, title_rect)

        self._draw_canvas(screen)
        self._draw_panel(screen)

        hint = self._small_font.render(
            "Enter — тест    Esc — назад    Ctrl+S — сохранить    Ctrl+N — новый",
            True,
            BLACK,
        )
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 28)))

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    def _handle_key(self, event: pygame.event.Event) -> None:
        mods = pygame.key.get_mods()
        if event.key == pygame.K_ESCAPE:
            if self.dirty:
                self.message = "Есть несохраненные изменения: Ctrl+S сохранить, Ctrl+R отменить"
                return
            from .menu import MenuScene

            self.next_scene = MenuScene()
            return

        if event.key == pygame.K_n and mods & pygame.KMOD_CTRL:
            self._create_level()
        elif event.key == pygame.K_s and mods & pygame.KMOD_CTRL:
            self._save_current()
        elif event.key == pygame.K_r and mods & pygame.KMOD_CTRL:
            self._load_current()
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._play_current()
        elif event.key in (pygame.K_RIGHTBRACKET, pygame.K_PAGEUP):
            self._switch_level(1)
        elif event.key in (pygame.K_LEFTBRACKET, pygame.K_PAGEDOWN):
            self._switch_level(-1)
        elif event.key == pygame.K_1:
            self._set_mode("select")
        elif event.key == pygame.K_2:
            self._set_mode("platform")
        elif event.key == pygame.K_3:
            self._set_mode("obstacle")
        elif event.key == pygame.K_4:
            self._set_mode("goal")
        elif event.key == pygame.K_5:
            self._set_mode("ball")
        elif event.key == pygame.K_6:
            self._set_mode("spring")
        elif event.key == pygame.K_7:
            self._set_mode("spike")
        elif event.key == pygame.K_TAB:
            self._cycle_selection()
        elif event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
            self._delete_selected()
        elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
            amount = 20 if mods & pygame.KMOD_SHIFT else editor_model.GRID
            self._nudge_selected(event.key, amount)
        elif event.key in (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s):
            amount = 20 if mods & pygame.KMOD_SHIFT else editor_model.GRID
            self._resize_selected(event.key, amount)

    def _mouse_down(self, pos: Tuple[int, int]) -> None:
        world_pos = self._world_from_screen(pos)
        if world_pos is None:
            return

        x, y = world_pos
        if self.mode == "platform":
            self.draft.platforms.append([x, y, 180, 20])
            self.selection = ("platform", len(self.draft.platforms) - 1)
            self.dirty = True
            self.dragging = True
            return

        if self.mode == "obstacle":
            self.draft.obstacles.append([x, y, 50, 80])
            self.selection = ("obstacle", len(self.draft.obstacles) - 1)
            self.dirty = True
            self.dragging = True
            return

        if self.mode == "spring":
            self.draft.springs.append([x, y, 90, 24])
            self.selection = ("spring", len(self.draft.springs) - 1)
            self.dirty = True
            self.dragging = True
            return

        if self.mode == "spike":
            self.draft.spikes.append([x, y, 90, 34])
            self.selection = ("spike", len(self.draft.spikes) - 1)
            self.dirty = True
            self.dragging = True
            return

        if self.mode == "goal":
            self.draft.goal[0] = x
            self.draft.goal[1] = y
            editor_model.clamp_block(self.draft.goal)
            self.selection = ("goal", -1)
            self.dirty = True
            self.dragging = True
            return

        if self.mode == "ball":
            self.draft.ball_start[:] = [x, y]
            editor_model.clamp_point(self.draft.ball_start)
            self.selection = ("ball", -1)
            self.dirty = True
            self.dragging = True
            return

        self.selection = editor_model.hit_test(self.draft, (x, y))
        self.dragging = self.selection is not None

    def _drag_to(self, pos: Tuple[int, int]) -> None:
        if self.selection is None:
            return
        world_pos = self._world_from_screen(pos)
        if world_pos is None:
            return
        x, y = world_pos
        kind, _ = self.selection
        if kind == "ball":
            self.draft.ball_start[:] = [x, y]
            editor_model.clamp_point(self.draft.ball_start)
        else:
            block = editor_model.selected_block(self.draft, self.selection)
            if block is None:
                return
            block[0], block[1] = x, y
            editor_model.clamp_block(block)
        self.dirty = True

    # ------------------------------------------------------------------
    # Draft operations
    # ------------------------------------------------------------------
    def _load_or_create_catalog(self) -> List[str]:
        CUSTOM_LEVELS_DIR.mkdir(parents=True, exist_ok=True)
        if not CUSTOM_MANIFEST_PATH.exists():
            level_ids = [DEFAULT_LEVEL_ID]
            editor_model.save_manifest(level_ids, CUSTOM_MANIFEST_PATH)
            editor_model.save_level_draft(
                CUSTOM_LEVELS_DIR / f"{DEFAULT_LEVEL_ID}.json",
                editor_model.create_default_draft(1),
            )
            return level_ids

        level_ids = list(editor_model.load_manifest(CUSTOM_MANIFEST_PATH))
        if level_ids:
            return level_ids

        level_ids = [DEFAULT_LEVEL_ID]
        editor_model.save_manifest(level_ids, CUSTOM_MANIFEST_PATH)
        editor_model.save_level_draft(
            CUSTOM_LEVELS_DIR / f"{DEFAULT_LEVEL_ID}.json",
            editor_model.create_default_draft(1),
        )
        return level_ids

    def _path_for_index(self, index: int):
        return CUSTOM_LEVELS_DIR / f"{self.level_ids[index]}.json"

    def _load_current(self) -> None:
        self.path = self._path_for_index(self.index)
        self.draft = editor_model.load_level_draft(self.path)
        self.selection = None
        self.dragging = False
        self.dirty = False
        self.message = f"Загружен {self.path.name}"

    def _save_current(self) -> None:
        editor_model.save_level_draft(self.path, self.draft)
        self.dirty = False
        self.message = f"Сохранено: {self.path.name}"

    def _create_level(self) -> None:
        if self.dirty:
            self.message = "Есть несохраненные изменения: Ctrl+S сохранить, Ctrl+R отменить"
            return
        level_id = editor_model.next_level_id(self.level_ids, CUSTOM_LEVELS_DIR)
        draft = editor_model.create_default_draft(len(self.level_ids) + 1)
        path = CUSTOM_LEVELS_DIR / f"{level_id}.json"
        editor_model.save_level_draft(path, draft)

        self.level_ids.append(level_id)
        editor_model.save_manifest(self.level_ids, CUSTOM_MANIFEST_PATH)
        self.index = len(self.level_ids) - 1
        self._load_current()
        self.message = f"Создан {path.name}"

    def _play_current(self) -> None:
        from .play import GameScene

        self.next_scene = GameScene(
            level_def=self._draft_to_level_def(),
            return_scene=self,
            record_progress=False,
            campaign_run=False,
        )

    def _draft_to_level_def(self) -> level_utils.LevelDef:
        def blocks(items):
            return tuple(level_utils.Block(*block) for block in items)

        return level_utils.LevelDef(
            name=self.draft.name,
            ball_start=tuple(self.draft.ball_start),
            platforms=blocks(self.draft.platforms),
            obstacles=blocks(self.draft.obstacles),
            goal=level_utils.Block(*self.draft.goal),
            springs=blocks(self.draft.springs),
            spikes=blocks(self.draft.spikes),
        )

    def _switch_level(self, delta: int) -> None:
        if self.dirty:
            self.message = "Есть несохраненные изменения: Ctrl+S сохранить, Ctrl+R отменить"
            return
        self.index = (self.index + delta) % len(self.level_ids)
        self._load_current()

    def _set_mode(self, mode: str) -> None:
        self.mode = mode
        self.message = f"Режим: {mode}"

    def _cycle_selection(self) -> None:
        items: List[editor_model.Selection] = [("ball", -1), ("goal", -1)]
        items.extend(("platform", i) for i in range(len(self.draft.platforms)))
        items.extend(("obstacle", i) for i in range(len(self.draft.obstacles)))
        items.extend(("spring", i) for i in range(len(self.draft.springs)))
        items.extend(("spike", i) for i in range(len(self.draft.spikes)))
        if self.selection not in items:
            self.selection = items[0]
            return
        self.selection = items[(items.index(self.selection) + 1) % len(items)]

    def _delete_selected(self) -> None:
        if self.selection is None:
            return
        kind, index = self.selection
        if kind == "platform":
            del self.draft.platforms[index]
        elif kind == "obstacle":
            del self.draft.obstacles[index]
        elif kind == "spring":
            del self.draft.springs[index]
        elif kind == "spike":
            del self.draft.spikes[index]
        else:
            self.message = "Старт и цель нельзя удалить"
            return
        self.selection = None
        self.dirty = True

    def _nudge_selected(self, key: int, amount: int) -> None:
        if self.selection is None:
            return
        dx = dy = 0
        if key == pygame.K_LEFT:
            dx = -amount
        elif key == pygame.K_RIGHT:
            dx = amount
        elif key == pygame.K_UP:
            dy = -amount
        elif key == pygame.K_DOWN:
            dy = amount

        kind, _ = self.selection
        if kind == "ball":
            self.draft.ball_start[0] += dx
            self.draft.ball_start[1] += dy
            editor_model.clamp_point(self.draft.ball_start)
        else:
            block = editor_model.selected_block(self.draft, self.selection)
            if block is None:
                return
            block[0] += dx
            block[1] += dy
            editor_model.clamp_block(block)
        self.dirty = True

    def _resize_selected(self, key: int, amount: int) -> None:
        block = editor_model.selected_block(self.draft, self.selection)
        if block is None:
            return
        if key == pygame.K_a:
            block[2] -= amount
        elif key == pygame.K_d:
            block[2] += amount
        elif key == pygame.K_w:
            block[3] -= amount
        elif key == pygame.K_s:
            block[3] += amount
        editor_model.clamp_block(block)
        self.dirty = True

    # ------------------------------------------------------------------
    # Coordinate transforms
    # ------------------------------------------------------------------
    @property
    def _scale_x(self) -> float:
        return CANVAS_RECT.width / WIDTH

    @property
    def _scale_y(self) -> float:
        return CANVAS_RECT.height / HEIGHT

    def _screen_from_world(self, x: float, y: float) -> Tuple[int, int]:
        return (
            CANVAS_RECT.left + int(round(x * self._scale_x)),
            CANVAS_RECT.top + int(round(y * self._scale_y)),
        )

    def _world_from_screen(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        if not CANVAS_RECT.collidepoint(pos):
            return None
        x = (pos[0] - CANVAS_RECT.left) / self._scale_x
        y = (pos[1] - CANVAS_RECT.top) / self._scale_y
        return (
            editor_model.snap(int(round(x))),
            editor_model.snap(int(round(y))),
        )

    def _screen_rect_from_block(self, block: editor_model.Block) -> pygame.Rect:
        x, y, width, height = block
        return pygame.Rect(
            CANVAS_RECT.left + int(round((x - width / 2) * self._scale_x)),
            CANVAS_RECT.top + int(round((y - height / 2) * self._scale_y)),
            max(1, int(round(width * self._scale_x))),
            max(1, int(round(height * self._scale_y))),
        )

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def _draw_canvas(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, editor_model.COLOR_BG, CANVAS_RECT)
        self._draw_grid(screen)

        for i, block in enumerate(self.draft.platforms):
            self._draw_block(
                screen,
                block,
                editor_model.COLOR_PLATFORM,
                self.selection == ("platform", i),
            )
        for i, block in enumerate(self.draft.springs):
            self._draw_spring(
                screen,
                block,
                self.selection == ("spring", i),
            )
        for i, block in enumerate(self.draft.obstacles):
            self._draw_block(
                screen,
                block,
                editor_model.COLOR_OBSTACLE,
                self.selection == ("obstacle", i),
            )
        for i, block in enumerate(self.draft.spikes):
            self._draw_spike(
                screen,
                block,
                self.selection == ("spike", i),
            )
        self._draw_block(
            screen,
            self.draft.goal,
            editor_model.COLOR_GOAL,
            self.selection == ("goal", -1),
        )

        bx, by = self.draft.ball_start
        ball_pos = self._screen_from_world(bx, by)
        ball_radius = max(4, int(round(editor_model.BALL_RADIUS * self._scale_x)))
        pygame.draw.circle(screen, editor_model.COLOR_BALL, ball_pos, ball_radius)
        pygame.draw.circle(
            screen,
            editor_model.COLOR_SELECTED
            if self.selection == ("ball", -1)
            else (45, 20, 20),
            ball_pos,
            ball_radius,
            2,
        )
        pygame.draw.rect(screen, (45, 50, 60), CANVAS_RECT, 2)

    def _draw_grid(self, screen: pygame.Surface) -> None:
        for x in range(0, WIDTH + 1, editor_model.GRID):
            sx, _ = self._screen_from_world(x, 0)
            color = editor_model.COLOR_GRID if x % MAJOR_GRID == 0 else editor_model.COLOR_GRID_MINOR
            pygame.draw.line(screen, color, (sx, CANVAS_RECT.top), (sx, CANVAS_RECT.bottom), 1)
        for y in range(0, HEIGHT + 1, editor_model.GRID):
            _, sy = self._screen_from_world(0, y)
            color = editor_model.COLOR_GRID if y % MAJOR_GRID == 0 else editor_model.COLOR_GRID_MINOR
            pygame.draw.line(screen, color, (CANVAS_RECT.left, sy), (CANVAS_RECT.right, sy), 1)

    def _draw_block(self, screen, block, color, selected: bool) -> None:
        rect = self._screen_rect_from_block(block)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(
            screen,
            editor_model.COLOR_SELECTED if selected else (30, 34, 42),
            rect,
            2,
        )
        if selected:
            for point in (rect.topleft, rect.topright, rect.bottomleft, rect.bottomright):
                handle = pygame.Rect(0, 0, 6, 6)
                handle.center = point
                pygame.draw.rect(screen, editor_model.COLOR_SELECTED, handle)

    def _draw_spring(self, screen, block, selected: bool) -> None:
        self._draw_block(screen, block, editor_model.COLOR_SPRING, selected)
        rect = self._screen_rect_from_block(block)
        left = rect.left + 5
        right = rect.right - 5
        if right <= left:
            return
        mid_y = rect.centery
        amp = max(2, min(rect.height // 3, 8))
        points = []
        for i in range(7):
            x = left + int((right - left) * i / 6)
            y = mid_y + (amp if i % 2 else -amp)
            points.append((x, y))
        pygame.draw.lines(screen, (20, 60, 70), False, points, 2)

    def _draw_spike(self, screen, block, selected: bool) -> None:
        rect = self._screen_rect_from_block(block)
        pygame.draw.rect(screen, (120, 30, 36), rect)
        count = max(1, rect.width // max(10, rect.height))
        step = rect.width / count
        for i in range(count):
            left = rect.left + int(i * step)
            right = rect.left + int((i + 1) * step)
            points = [
                (left, rect.bottom),
                ((left + right) // 2, rect.top),
                (right, rect.bottom),
            ]
            pygame.draw.polygon(screen, editor_model.COLOR_SPIKE, points)
            pygame.draw.polygon(screen, (45, 20, 20), points, 1)
        pygame.draw.rect(
            screen,
            editor_model.COLOR_SELECTED if selected else (30, 34, 42),
            rect,
            2,
        )

    def _draw_panel(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, (34, 38, 46), PANEL_RECT)
        x = PANEL_RECT.left + 14
        y = PANEL_RECT.top + 14
        dirty = "*" if self.dirty else ""
        lines = [
            f"{self.index + 1}/{len(self.level_ids)} {self.draft.name}{dirty}",
            self.path.name,
            "",
            f"Режим: {self.mode}",
            f"Выбор: {self._selection_label()}",
            "",
            "[ / ] уровень",
            "Enter тест",
            "1 выбор",
            "2 платформа",
            "3 препятствие",
            "4 цель",
            "5 старт",
            "6 пружина",
            "7 шип",
            "Стрелки двигать",
            "A/D ширина",
            "W/S высота",
            "Del удалить",
        ]
        for line in lines:
            if not line:
                y += 8
                continue
            font = self._panel_font if y == PANEL_RECT.top + 14 else self._small_font
            y = self._draw_line(screen, line, x, y, font)

        self._draw_wrapped(
            screen,
            self.message,
            x,
            PANEL_RECT.bottom - 58,
            PANEL_RECT.width - 28,
        )

    def _draw_line(self, screen, text, x, y, font, color=editor_model.COLOR_PANEL_TEXT):
        surf = font.render(text, True, color)
        screen.blit(surf, (x, y))
        return y + surf.get_height() + 5

    def _draw_wrapped(self, screen, text: str, x: int, y: int, max_width: int) -> None:
        words = text.split()
        line = ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if self._tiny_font.size(candidate)[0] <= max_width:
                line = candidate
                continue
            if line:
                y = self._draw_line(screen, line, x, y, self._tiny_font, editor_model.COLOR_MUTED)
            line = word
        if line:
            self._draw_line(screen, line, x, y, self._tiny_font, editor_model.COLOR_MUTED)

    def _selection_label(self) -> str:
        if self.selection is None:
            return "-"
        kind, index = self.selection
        if index >= 0:
            return f"{kind} #{index + 1}"
        return kind
