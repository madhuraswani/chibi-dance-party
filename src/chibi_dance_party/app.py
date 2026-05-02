from __future__ import annotations

from pathlib import Path

from PySide6 import QtWidgets

from .asset_loader import load_character_assets
from .config import load_config
from .scheduler import Scheduler


def run_app(base_dir: Path) -> int:
    app = QtWidgets.QApplication([])
    config = load_config(base_dir / "config.json")

    characters_dir = Path(config.characters_dir)
    if not characters_dir.is_absolute():
        characters_dir = base_dir / characters_dir

    assets = load_character_assets(characters_dir)
    if not assets:
        print(
            "No character images found. Add PNG/GIF files to characters/ or run tools/generate_sample_chibi.py."
        )
        return 1

    _scheduler = Scheduler(app, assets, config)
    return app.exec()
