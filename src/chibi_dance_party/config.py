from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    spawn_min_seconds: float = 2.0
    spawn_max_seconds: float = 8.0
    visible_duration_seconds: float = 5.0
    max_active_characters: int = 5
    screen_margin: int = 20
    spawn_mode: str = "corners"
    fade_out_seconds: float = 1.0
    characters_dir: str = "characters"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def load_config(path: Path) -> AppConfig:
    cfg = AppConfig()
    if not path.exists():
        return cfg

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return cfg

    if not isinstance(raw, dict):
        return cfg

    cfg.spawn_min_seconds = _clamp(float(raw.get("spawn_min_seconds", cfg.spawn_min_seconds)), 0.2, 60.0)
    cfg.spawn_max_seconds = _clamp(float(raw.get("spawn_max_seconds", cfg.spawn_max_seconds)), cfg.spawn_min_seconds, 120.0)
    cfg.visible_duration_seconds = _clamp(float(raw.get("visible_duration_seconds", cfg.visible_duration_seconds)), 0.5, 120.0)
    cfg.max_active_characters = int(_clamp(float(raw.get("max_active_characters", cfg.max_active_characters)), 1, 100))
    cfg.screen_margin = int(_clamp(float(raw.get("screen_margin", cfg.screen_margin)), 0, 500))
    cfg.fade_out_seconds = _clamp(float(raw.get("fade_out_seconds", cfg.fade_out_seconds)), 0.1, 10.0)

    spawn_mode = str(raw.get("spawn_mode", cfg.spawn_mode)).strip().lower()
    if spawn_mode in {"random", "edges", "bottom_walk", "corners"}:
        cfg.spawn_mode = spawn_mode

    characters_dir = raw.get("characters_dir", cfg.characters_dir)
    if isinstance(characters_dir, str) and characters_dir.strip():
        cfg.characters_dir = characters_dir.strip()

    return cfg
