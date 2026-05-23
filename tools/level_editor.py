"""Interactive level editor for Gravity Ball JSON levels.

Run from the project root:
    python tools/level_editor.py

The editor writes directly to files listed in levels/manifest.json.
"""
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pygame  # noqa: E402

from src.utils.config import HEIGHT, WIDTH  # noqa: E402
from src.utils.level import load_manifest  # noqa: E402


LEVELS_DIR = PROJECT_ROOT / "levels"
MANIFEST_PATH = LEVELS_DIR / "manifest.json"
PANEL_WIDTH = 320
WINDOW_SIZE = (WIDTH + PANEL_WIDTH, HEIGHT)
GRID = 10
BALL_RADIUS = 20
MIN_BLOCK_SIZE = 10

COLOR_BG = (220, 232, 244)
COLOR_GRID_MINOR = (207, 220, 232)
COLOR_GRID = (185, 202, 218)
COLOR_PANEL = (34, 38, 46)
COLOR_PANEL_TEXT = (235, 238, 242)
COLOR_MUTED = (170, 178, 190)
COLOR_PLATFORM = (72, 164, 72)
COLOR_OBSTACLE = (80, 96, 170)
COLOR_SPRING = (80, 220, 230)
COLOR_SPIKE = (230, 55, 60)
COLOR_GOAL = (230, 205, 55)
COLOR_BALL = (225, 70, 70)
COLOR_SELECTED = (255, 180, 50)

Block = List[int]
Selection = Tuple[str, int]


@dataclass
class LevelDraft:
    """Mutable representation of one level JSON file."""

    name: str
    ball_start: List[int]
    platforms: List[Block]
    obstacles: List[Block]
    goal: Block
    springs: List[Block] = field(default_factory=list)
    spikes: List[Block] = field(default_factory=list)

    def to_json_dict(self) -> dict:
        return {
            "name": self.name,
            "ball_start": [int(self.ball_start[0]), int(self.ball_start[1])],
            "platforms": [[int(v) for v in block] for block in self.platforms],
            "obstacles": [[int(v) for v in block] for block in self.obstacles],
            "springs": [[int(v) for v in block] for block in self.springs],
            "spikes": [[int(v) for v in block] for block in self.spikes],
            "goal": [int(v) for v in self.goal],
        }


def _as_int_list(values, expected_len: int) -> List[int]:
    if len(values) != expected_len:
        raise ValueError(f"expected {expected_len} values, got {values!r}")
    return [int(round(float(value))) for value in values]


def load_level_draft(path: Path) -> LevelDraft:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return LevelDraft(
        name=str(data["name"]),
        ball_start=_as_int_list(data["ball_start"], 2),
        platforms=[_as_int_list(block, 4) for block in data["platforms"]],
        obstacles=[_as_int_list(block, 4) for block in data["obstacles"]],
        goal=_as_int_list(data["goal"], 4),
        springs=[_as_int_list(block, 4) for block in data.get("springs", [])],
        spikes=[_as_int_list(block, 4) for block in data.get("spikes", [])],
    )


def save_level_draft(path: Path, draft: LevelDraft) -> None:
    text = json.dumps(draft.to_json_dict(), indent=2, ensure_ascii=False)
    path.write_text(text + "\n", encoding="utf-8")


def save_manifest(level_ids: List[str], path: Path = MANIFEST_PATH) -> None:
    text = json.dumps({"levels": level_ids}, indent=2, ensure_ascii=False)
    path.write_text(text + "\n", encoding="utf-8")


def next_level_id(level_ids: List[str], levels_dir: Path = LEVELS_DIR) -> str:
    index = len(level_ids) + 1
    used = set(level_ids)
    while True:
        level_id = f"level_{index:03d}"
        if level_id not in used and not (levels_dir / f"{level_id}.json").exists():
            return level_id
        index += 1


def create_default_draft(number: int) -> LevelDraft:
    return LevelDraft(
        name=f"Новый уровень {number}",
        ball_start=[120, 100],
        platforms=[[500, 620, 800, 20]],
        obstacles=[],
        goal=[840, 560, 40, 60],
        springs=[],
        spikes=[],
    )


def snap(value: int, grid: int = GRID) -> int:
    return int(round(value / grid) * grid)


def block_rect(block: Block) -> pygame.Rect:
    x, y, width, height = block
    return pygame.Rect(
        int(x - width / 2),
        int(y - height / 2),
        int(width),
        int(height),
    )


def draw_editor_grid(screen: pygame.Surface, field: pygame.Rect) -> None:
    """Draws the visible editor grid at the same 10px step used by snapping."""
    major_step = GRID * 5
    for x in range(field.left, field.right + 1, GRID):
        color = COLOR_GRID if x % major_step == 0 else COLOR_GRID_MINOR
        pygame.draw.line(screen, color, (x, field.top), (x, field.bottom), 1)
    for y in range(field.top, field.bottom + 1, GRID):
        color = COLOR_GRID if y % major_step == 0 else COLOR_GRID_MINOR
        pygame.draw.line(screen, color, (field.left, y), (field.right, y), 1)


def clamp_point(point: List[int]) -> None:
    point[0] = max(BALL_RADIUS, min(WIDTH - BALL_RADIUS, point[0]))
    point[1] = max(BALL_RADIUS, min(HEIGHT - BALL_RADIUS, point[1]))


def clamp_block(block: Block) -> None:
    block[2] = max(MIN_BLOCK_SIZE, int(block[2]))
    block[3] = max(MIN_BLOCK_SIZE, int(block[3]))
    half_w = block[2] // 2
    half_h = block[3] // 2
    block[0] = max(half_w, min(WIDTH - half_w, int(block[0])))
    block[1] = max(half_h, min(HEIGHT - half_h, int(block[1])))


def selected_block(draft: LevelDraft, selection: Optional[Selection]) -> Optional[Block]:
    if selection is None:
        return None
    kind, index = selection
    if kind == "platform":
        return draft.platforms[index]
    if kind == "obstacle":
        return draft.obstacles[index]
    if kind == "goal":
        return draft.goal
    if kind == "spring":
        return draft.springs[index]
    if kind == "spike":
        return draft.spikes[index]
    return None


def hit_test(draft: LevelDraft, pos: Tuple[int, int]) -> Optional[Selection]:
    x, y = pos
    bx, by = draft.ball_start
    if (x - bx) ** 2 + (y - by) ** 2 <= (BALL_RADIUS + 6) ** 2:
        return ("ball", -1)

    for index in range(len(draft.spikes) - 1, -1, -1):
        if block_rect(draft.spikes[index]).collidepoint(pos):
            return ("spike", index)

    for index in range(len(draft.springs) - 1, -1, -1):
        if block_rect(draft.springs[index]).collidepoint(pos):
            return ("spring", index)

    for index in range(len(draft.obstacles) - 1, -1, -1):
        if block_rect(draft.obstacles[index]).collidepoint(pos):
            return ("obstacle", index)

    if block_rect(draft.goal).collidepoint(pos):
        return ("goal", -1)

    for index in range(len(draft.platforms) - 1, -1, -1):
        if block_rect(draft.platforms[index]).collidepoint(pos):
            return ("platform", index)

    return None


class LevelEditor:
    def __init__(self) -> None:
        self.level_ids = list(load_manifest(MANIFEST_PATH))
        self.index = 0
        self.path = self._path_for_index(self.index)
        self.draft = load_level_draft(self.path)

        self.mode = "select"
        self.selection: Optional[Selection] = None
        self.dragging = False
        self.dirty = False
        self.message = "Готово"

        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 30)

    def _path_for_index(self, index: int) -> Path:
        return LEVELS_DIR / f"{self.level_ids[index]}.json"

    def load_current(self) -> None:
        self.path = self._path_for_index(self.index)
        self.draft = load_level_draft(self.path)
        self.selection = None
        self.dragging = False
        self.dirty = False
        self.message = f"Загружен {self.path.name}"

    def save_current(self) -> None:
        save_level_draft(self.path, self.draft)
        self.dirty = False
        self.message = f"Сохранено: {self.path.name}"

    def switch_level(self, delta: int) -> None:
        if self.dirty:
            self.message = "Есть несохраненные изменения: Ctrl+S сохранить, Ctrl+R отменить"
            return
        self.index = (self.index + delta) % len(self.level_ids)
        self.load_current()

    def create_level(self) -> None:
        if self.dirty:
            self.message = "Есть несохраненные изменения: Ctrl+S сохранить, Ctrl+R отменить"
            return

        level_id = next_level_id(self.level_ids, LEVELS_DIR)
        draft = create_default_draft(len(self.level_ids) + 1)
        path = LEVELS_DIR / f"{level_id}.json"
        save_level_draft(path, draft)

        self.level_ids.append(level_id)
        save_manifest(self.level_ids, MANIFEST_PATH)
        self.index = len(self.level_ids) - 1
        self.load_current()
        self.message = f"Создан {path.name}"

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        self.message = f"Режим: {mode}"

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            return self._handle_key(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._mouse_down(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._drag_to(event.pos)

        return True

    def _handle_key(self, event: pygame.event.Event) -> bool:
        mods = pygame.key.get_mods()
        if event.key == pygame.K_ESCAPE:
            if self.dirty:
                self.message = "Есть несохраненные изменения: Ctrl+S сохранить, Ctrl+R отменить"
                return True
            return False
        if event.key == pygame.K_n and mods & pygame.KMOD_CTRL:
            self.create_level()
        elif event.key == pygame.K_s and mods & pygame.KMOD_CTRL:
            self.save_current()
        elif event.key == pygame.K_r and mods & pygame.KMOD_CTRL:
            self.load_current()
        elif event.key in (pygame.K_RIGHTBRACKET, pygame.K_PAGEUP):
            self.switch_level(1)
        elif event.key in (pygame.K_LEFTBRACKET, pygame.K_PAGEDOWN):
            self.switch_level(-1)
        elif event.key == pygame.K_1:
            self.set_mode("select")
        elif event.key == pygame.K_2:
            self.set_mode("platform")
        elif event.key == pygame.K_3:
            self.set_mode("obstacle")
        elif event.key == pygame.K_4:
            self.set_mode("goal")
        elif event.key == pygame.K_5:
            self.set_mode("ball")
        elif event.key == pygame.K_6:
            self.set_mode("spring")
        elif event.key == pygame.K_7:
            self.set_mode("spike")
        elif event.key == pygame.K_TAB:
            self._cycle_selection()
        elif event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
            self._delete_selected()
        elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
            self._nudge_selected(event.key, 20 if mods & pygame.KMOD_SHIFT else GRID)
        elif event.key in (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s):
            self._resize_selected(event.key, 20 if mods & pygame.KMOD_SHIFT else GRID)
        return True

    def _mouse_down(self, pos: Tuple[int, int]) -> None:
        if pos[0] >= WIDTH:
            return
        snapped = (snap(pos[0]), snap(pos[1]))

        if self.mode == "platform":
            self.draft.platforms.append([snapped[0], snapped[1], 180, 20])
            self.selection = ("platform", len(self.draft.platforms) - 1)
            self.dirty = True
            self.dragging = True
            return

        if self.mode == "obstacle":
            self.draft.obstacles.append([snapped[0], snapped[1], 50, 80])
            self.selection = ("obstacle", len(self.draft.obstacles) - 1)
            self.dirty = True
            self.dragging = True
            return

        if self.mode == "spring":
            self.draft.springs.append([snapped[0], snapped[1], 90, 24])
            self.selection = ("spring", len(self.draft.springs) - 1)
            self.dirty = True
            self.dragging = True
            return

        if self.mode == "spike":
            self.draft.spikes.append([snapped[0], snapped[1], 90, 34])
            self.selection = ("spike", len(self.draft.spikes) - 1)
            self.dirty = True
            self.dragging = True
            return

        if self.mode == "goal":
            self.draft.goal[0] = snapped[0]
            self.draft.goal[1] = snapped[1]
            clamp_block(self.draft.goal)
            self.selection = ("goal", -1)
            self.dirty = True
            self.dragging = True
            return

        if self.mode == "ball":
            self.draft.ball_start[:] = [snapped[0], snapped[1]]
            clamp_point(self.draft.ball_start)
            self.selection = ("ball", -1)
            self.dirty = True
            self.dragging = True
            return

        self.selection = hit_test(self.draft, snapped)
        self.dragging = self.selection is not None

    def _drag_to(self, pos: Tuple[int, int]) -> None:
        if self.selection is None or pos[0] >= WIDTH:
            return
        x, y = snap(pos[0]), snap(pos[1])
        kind, _ = self.selection
        if kind == "ball":
            self.draft.ball_start[:] = [x, y]
            clamp_point(self.draft.ball_start)
        else:
            block = selected_block(self.draft, self.selection)
            if block is None:
                return
            block[0], block[1] = x, y
            clamp_block(block)
        self.dirty = True

    def _cycle_selection(self) -> None:
        items: List[Selection] = [("ball", -1), ("goal", -1)]
        items.extend(("platform", i) for i in range(len(self.draft.platforms)))
        items.extend(("obstacle", i) for i in range(len(self.draft.obstacles)))
        items.extend(("spring", i) for i in range(len(self.draft.springs)))
        items.extend(("spike", i) for i in range(len(self.draft.spikes)))
        if not items:
            self.selection = None
            return
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
            clamp_point(self.draft.ball_start)
        else:
            block = selected_block(self.draft, self.selection)
            if block is None:
                return
            block[0] += dx
            block[1] += dy
            clamp_block(block)
        self.dirty = True

    def _resize_selected(self, key: int, amount: int) -> None:
        block = selected_block(self.draft, self.selection)
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
        clamp_block(block)
        self.dirty = True

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((18, 21, 26))
        self._draw_world(screen)
        self._draw_panel(screen)

    def _draw_world(self, screen: pygame.Surface) -> None:
        field = pygame.Rect(0, 0, WIDTH, HEIGHT)
        pygame.draw.rect(screen, COLOR_BG, field)
        draw_editor_grid(screen, field)

        for i, block in enumerate(self.draft.platforms):
            self._draw_block(
                screen,
                block,
                COLOR_PLATFORM,
                self.selection == ("platform", i),
            )
        for i, block in enumerate(self.draft.springs):
            self._draw_spring_block(
                screen,
                block,
                self.selection == ("spring", i),
            )
        for i, block in enumerate(self.draft.obstacles):
            self._draw_block(
                screen,
                block,
                COLOR_OBSTACLE,
                self.selection == ("obstacle", i),
            )
        for i, block in enumerate(self.draft.spikes):
            self._draw_spike_block(
                screen,
                block,
                self.selection == ("spike", i),
            )
        self._draw_block(
            screen,
            self.draft.goal,
            COLOR_GOAL,
            self.selection == ("goal", -1),
        )

        bx, by = self.draft.ball_start
        pygame.draw.circle(screen, COLOR_BALL, (bx, by), BALL_RADIUS)
        pygame.draw.circle(
            screen,
            COLOR_SELECTED if self.selection == ("ball", -1) else (45, 20, 20),
            (bx, by),
            BALL_RADIUS,
            3,
        )
        pygame.draw.rect(screen, (45, 50, 60), field, 2)

    def _draw_block(
        self,
        screen: pygame.Surface,
        block: Block,
        color: Tuple[int, int, int],
        selected: bool,
    ) -> None:
        rect = block_rect(block)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(
            screen,
            COLOR_SELECTED if selected else (30, 34, 42),
            rect,
            3 if selected else 2,
        )
        if selected:
            for point in (rect.topleft, rect.topright, rect.bottomleft, rect.bottomright):
                handle = pygame.Rect(0, 0, 8, 8)
                handle.center = point
                pygame.draw.rect(screen, COLOR_SELECTED, handle)

    def _draw_spring_block(
        self,
        screen: pygame.Surface,
        block: Block,
        selected: bool,
    ) -> None:
        self._draw_block(screen, block, COLOR_SPRING, selected)
        rect = block_rect(block)
        left = rect.left + 8
        right = rect.right - 8
        mid_y = rect.centery
        amp = max(4, min(rect.height // 3, 10))
        points = []
        for i in range(7):
            x = left + int((right - left) * i / 6)
            y = mid_y + (amp if i % 2 else -amp)
            points.append((x, y))
        pygame.draw.lines(screen, (20, 60, 70), False, points, 3)

    def _draw_spike_block(
        self,
        screen: pygame.Surface,
        block: Block,
        selected: bool,
    ) -> None:
        rect = block_rect(block)
        pygame.draw.rect(screen, (120, 30, 36), rect)
        count = max(1, rect.width // max(16, rect.height))
        step = rect.width / count
        for i in range(count):
            left = rect.left + int(i * step)
            right = rect.left + int((i + 1) * step)
            points = [
                (left, rect.bottom),
                ((left + right) // 2, rect.top),
                (right, rect.bottom),
            ]
            pygame.draw.polygon(screen, COLOR_SPIKE, points)
            pygame.draw.polygon(screen, (45, 20, 20), points, 2)
        pygame.draw.rect(
            screen,
            COLOR_SELECTED if selected else (30, 34, 42),
            rect,
            3 if selected else 2,
        )
        if selected:
            for point in (rect.topleft, rect.topright, rect.bottomleft, rect.bottomright):
                handle = pygame.Rect(0, 0, 8, 8)
                handle.center = point
                pygame.draw.rect(screen, COLOR_SELECTED, handle)

    def _draw_panel(self, screen: pygame.Surface) -> None:
        panel = pygame.Rect(WIDTH, 0, PANEL_WIDTH, HEIGHT)
        pygame.draw.rect(screen, COLOR_PANEL, panel)
        x = WIDTH + 18
        y = 18
        dirty = "*" if self.dirty else ""
        y = self._draw_line(
            screen,
            f"{self.index + 1}/{len(self.level_ids)} {self.draft.name}{dirty}",
            x,
            y,
            self.title_font,
        )
        y = self._draw_line(screen, self.path.name, x, y + 2, self.small_font, COLOR_MUTED)
        y += 12
        y = self._draw_line(screen, f"Режим: {self.mode}", x, y, self.font)
        y = self._draw_line(screen, f"Выбор: {self._selection_label()}", x, y, self.font)
        y += 10

        help_lines = [
            "[ / ]  предыдущий / следующий",
            "1 выбор   2 платформа",
            "3 препятствие   4 цель",
            "5 старт   6 пружина",
            "7 шип",
            "ЛКМ / drag  выбрать и двигать",
            "Стрелки  двигать выбранное",
            "Shift+стрелки  быстрее",
            "A/D  ширина",
            "W/S  высота",
            "Tab  следующий объект",
            "Del  удалить блок",
            "Ctrl+N  новый уровень",
            "Ctrl+S  сохранить",
            "Ctrl+R  перезагрузить",
            "Esc  выход",
        ]
        for line in help_lines:
            y = self._draw_line(screen, line, x, y, self.small_font, COLOR_PANEL_TEXT)

        y += 12
        for line in self._object_summary():
            y = self._draw_line(screen, line, x, y, self.small_font, COLOR_MUTED)

        y = HEIGHT - 56
        self._draw_wrapped(screen, self.message, x, y, PANEL_WIDTH - 36)

    def _draw_line(
        self,
        screen: pygame.Surface,
        text: str,
        x: int,
        y: int,
        font: pygame.font.Font,
        color: Tuple[int, int, int] = COLOR_PANEL_TEXT,
    ) -> int:
        surface = font.render(text, True, color)
        screen.blit(surface, (x, y))
        return y + surface.get_height() + 5

    def _draw_wrapped(
        self,
        screen: pygame.Surface,
        text: str,
        x: int,
        y: int,
        max_width: int,
    ) -> None:
        words = text.split()
        line = ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if self.small_font.size(candidate)[0] <= max_width:
                line = candidate
                continue
            self._draw_line(screen, line, x, y, self.small_font, COLOR_MUTED)
            y += self.small_font.get_height() + 5
            line = word
        if line:
            self._draw_line(screen, line, x, y, self.small_font, COLOR_MUTED)

    def _selection_label(self) -> str:
        if self.selection is None:
            return "-"
        kind, index = self.selection
        if index >= 0:
            return f"{kind} #{index + 1}"
        return kind

    def _object_summary(self) -> List[str]:
        bx, by = self.draft.ball_start
        gx, gy, gw, gh = self.draft.goal
        return [
            f"Старт: {bx}, {by}",
            f"Цель: {gx}, {gy}, {gw}x{gh}",
            f"Платформы: {len(self.draft.platforms)}",
            f"Препятствия: {len(self.draft.obstacles)}",
            f"Пружины: {len(self.draft.springs)}",
            f"Шипы: {len(self.draft.spikes)}",
        ]


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Gravity Ball Level Editor")
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()
    editor = LevelEditor()

    running = True
    while running:
        for event in pygame.event.get():
            running = editor.handle_event(event)
            if not running:
                break
        editor.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
