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


def _read() -> dict:
    if not DEFAULT_PATH.exists():
        return {"total": None, "per_level": {}}
    try:
        with open(DEFAULT_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {"total": None, "per_level": {}}
    if not isinstance(data, dict):
        return {"total": None, "per_level": {}}
    data.setdefault("total", None)
    data.setdefault("per_level", {})
    return data


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
