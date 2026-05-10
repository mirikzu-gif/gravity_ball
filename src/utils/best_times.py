"""Лучшие времена прохождения — хранятся в best_times.json в корне проекта.

Простой модуль с set-функциями. Чтение/запись инкапсулированы; ошибки I/O
проглатываются, чтобы недоступная файловая система не валила игру.

Структура файла:
    {"total": float|None, "per_level": {"<name>": float}}
"""
import json
from pathlib import Path
from typing import Optional


DEFAULT_PATH: Path = (
    Path(__file__).resolve().parent.parent.parent / "best_times.json"
)


def _default_data() -> dict:
    return {"total": None, "per_level": {}}


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _normalize(data: dict) -> dict:
    total = data.get("total")
    if total is not None and not _is_number(total):
        total = None

    per_level = data.get("per_level")
    if not isinstance(per_level, dict):
        per_level = {}

    safe_per_level = {
        str(name): float(time)
        for name, time in per_level.items()
        if isinstance(name, str) and _is_number(time)
    }
    return {
        "total": float(total) if total is not None else None,
        "per_level": safe_per_level,
    }


def _read() -> dict:
    if not DEFAULT_PATH.exists():
        return _default_data()
    try:
        with open(DEFAULT_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return _default_data()
    if not isinstance(data, dict):
        return _default_data()
    return _normalize(data)


def _write(data: dict) -> None:
    try:
        DEFAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DEFAULT_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except OSError:
        pass


def record_level(name: str, time: float) -> bool:
    """Запоминает время уровня, если оно лучше прежнего. Возвращает True при новом рекорде."""
    data = _read()
    prev = data["per_level"].get(name)
    if prev is None or time < prev:
        data["per_level"][name] = time
        _write(data)
        return True
    return False


def record_total(time: float) -> bool:
    data = _read()
    prev = data["total"]
    if prev is None or time < prev:
        data["total"] = time
        _write(data)
        return True
    return False


def best_total() -> Optional[float]:
    return _read().get("total")


def best_for_level(name: str) -> Optional[float]:
    return _read()["per_level"].get(name)
