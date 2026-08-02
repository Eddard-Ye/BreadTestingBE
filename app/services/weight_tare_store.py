"""Persist app-layer weight tare offset (grams) across restarts."""

from __future__ import annotations

import json
import threading
from pathlib import Path

from app.core.config import get_settings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

_lock = threading.Lock()
_cached_offset: float | None = None


def resolve_weight_tare_path(config_path: str | None = None) -> Path:
    raw_path = config_path if config_path is not None else get_settings().WEIGHT_TARE_PATH
    path = Path(raw_path)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


def get_tare_offset_g(config_path: str | None = None) -> float:
    global _cached_offset
    with _lock:
        if _cached_offset is not None:
            return _cached_offset

        path = resolve_weight_tare_path(config_path)
        if not path.exists():
            _cached_offset = 0.0
            return _cached_offset

        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            value = float(raw.get("tareOffsetG", 0) or 0)
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            value = 0.0

        _cached_offset = value
        return _cached_offset


def set_tare_offset_g(value: float, config_path: str | None = None) -> float:
    global _cached_offset
    offset = round(float(value), 1)
    path = resolve_weight_tare_path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"tareOffsetG": offset}
    temp_path = path.with_suffix(".json.tmp")
    with _lock:
        temp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temp_path.replace(path)
        _cached_offset = offset
    return offset


def clear_tare_offset_g(config_path: str | None = None) -> float:
    return set_tare_offset_g(0.0, config_path=config_path)


def reset_tare_offset_cache() -> None:
    """Test helper: drop in-memory cache so next read hits disk."""
    global _cached_offset
    with _lock:
        _cached_offset = None
