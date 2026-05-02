from __future__ import annotations

from pathlib import Path


def load_character_assets(characters_dir: Path) -> list[Path]:
    assets: list[Path] = []
    if not characters_dir.exists():
        return assets

    for file in characters_dir.iterdir():
        if file.suffix.lower() in {".png", ".gif"} and file.is_file():
            assets.append(file)
    return assets
