"""
Chibi Dance Party – random chibi sprites dancing on your Linux desktop
=====================================================================

This script provides a lightweight desktop companion that spawns cute
chibi characters at random positions on your screen. Each character
appears in its own transparent, borderless window, stays for a few
seconds, and then disappears. The scheduler continues to spawn
characters at random intervals.

**Requirements**
----------------

* Python 3.8 or newer
* PySide6 (Qt for Python)
* Pillow (for image loading)

Install dependencies with:

```
pip install -r requirements.txt
```

Run the application with:

```
python3 main.py
```

You can add your own sprites by placing PNG files into the
`characters/` directory. Files with a transparent background work best.

**Note:** On Wayland sessions, some desktop environments may not allow
borderless windows to be truly topmost or transparent. The app has
been tested on X11 and modern Wayland compositors that support
transparent windows.
"""

import os
import random
import sys
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets


class CharacterWindow(QtWidgets.QWidget):
    """A borderless, transparent window that displays a chibi image."""

    def __init__(
        self,
        pixmap: QtGui.QPixmap | None = None,
        movie_path: str | None = None,
        duration_ms: int = 5000,
    ) -> None:
        super().__init__(None, QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Tool)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_AlwaysStackOnTop)
        self.pixmap = pixmap
        self.movie: QtGui.QMovie | None = None
        self.duration_ms = duration_ms

        if movie_path is not None:
            self.movie = QtGui.QMovie(movie_path)
            if self.movie.isValid():
                self.movie.frameChanged.connect(self._on_movie_frame_changed)
                self.movie.start()
                current = self.movie.currentPixmap()
                if not current.isNull():
                    self.resize(current.size())
            else:
                self.movie = None

        if self.movie is None:
            if self.pixmap is None or self.pixmap.isNull():
                raise ValueError("CharacterWindow requires a valid pixmap or movie_path")
            # Set window size to image size
            self.resize(self.pixmap.size())

        # Schedule closing after duration
        QtCore.QTimer.singleShot(self.duration_ms, self.fade_and_close)

        # For fade effect
        self._opacity_anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self._opacity_anim.setDuration(1000)
        self._opacity_anim.setStartValue(1.0)
        self._opacity_anim.setEndValue(0.0)
        self._opacity_anim.finished.connect(self.close)

    def fade_and_close(self) -> None:
        """Fade the window out and close it."""
        self._opacity_anim.start()

    def _on_movie_frame_changed(self) -> None:
        if self.movie is None:
            return
        frame = self.movie.currentPixmap()
        if not frame.isNull() and frame.size() != self.size():
            self.resize(frame.size())
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
        if self.movie is not None:
            frame = self.movie.currentPixmap()
            if not frame.isNull():
                painter.drawPixmap(0, 0, frame)
                return
        if self.pixmap is not None:
            painter.drawPixmap(0, 0, self.pixmap)


class Scheduler(QtCore.QObject):
    """Schedules chibi character windows at random intervals and positions."""

    def __init__(self, app: QtWidgets.QApplication, characters: list[Path]) -> None:
        super().__init__()
        self.app = app
        self.characters = characters
        # Determine available screen geometry
        screen = self.app.primaryScreen()
        if screen is None:
            raise RuntimeError("No primary screen detected")
        self.available_rect = screen.availableGeometry()
        # Start scheduling
        self.schedule_next()

    def schedule_next(self) -> None:
        """Plan the next character spawn after a random delay."""
        delay_ms = random.randint(2000, 8000)  # 2–8 seconds
        QtCore.QTimer.singleShot(delay_ms, self.spawn_character)

    def spawn_character(self) -> None:
        """Spawn a character window at a random location."""
        # Choose random character asset
        asset = random.choice(self.characters)
        ext = asset.suffix.lower()
        pixmap: QtGui.QPixmap | None = None
        movie_path: str | None = None

        if ext == ".gif":
            movie = QtGui.QMovie(str(asset))
            if movie.isValid():
                movie_path = str(asset)
                first_frame = movie.currentPixmap()
                if first_frame.isNull():
                    movie.start()
                    first_frame = movie.currentPixmap()
                    movie.stop()
                if first_frame.isNull():
                    return self.schedule_next()
                w = first_frame.width()
                h = first_frame.height()
            else:
                return self.schedule_next()
        else:
            pixmap = QtGui.QPixmap(str(asset))
            if pixmap.isNull():
                return self.schedule_next()
            w = pixmap.width()
            h = pixmap.height()

        # Determine position near bottom corners (dock/sidebar friendly)
        x, y = self._bottom_corner_position(w, h)
        # Create window
        window = CharacterWindow(pixmap=pixmap, movie_path=movie_path)
        window.move(x, y)
        window.show()
        # Keep reference to prevent garbage collection
        # We'll store active windows on the scheduler instance
        if not hasattr(self, "_windows"):
            self._windows = []
        self._windows.append(window)
        # Remove closed windows from list
        window.destroyed.connect(lambda: self._windows.remove(window))
        # Schedule next spawn
        self.schedule_next()

    def _bottom_corner_position(self, w: int, h: int) -> tuple[int, int]:
        """Return a position near the bottom-left or bottom-right corner."""
        rect = self.available_rect
        min_x = rect.left()
        max_x = rect.right() - w
        max_y = rect.bottom() - h
        min_y = rect.top()

        if max_x < min_x or max_y < min_y:
            return min_x, min_y

        side_margin = 24
        bottom_margin = 12
        corner_band = max(int(rect.width() * 0.18), w + side_margin)

        left_band_end = min(max_x, min_x + corner_band)
        right_band_start = max(min_x, max_x - corner_band)

        if random.random() < 0.5:
            x = random.randint(min_x, max(left_band_end, min_x))
        else:
            x = random.randint(min(right_band_start, max_x), max_x)

        y_min = max(min_y, max_y - max(int(rect.height() * 0.08), h // 3) - bottom_margin)
        y = random.randint(y_min, max_y)
        return x, y


def load_character_assets(characters_dir: Path) -> list[Path]:
    """Load all supported character assets from the characters directory."""
    assets: list[Path] = []
    for file in characters_dir.iterdir():
        if file.suffix.lower() in {".png", ".gif"} and file.is_file():
            assets.append(file)
    return assets


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    # Load images
    characters_dir = Path(__file__).resolve().parent / "characters"
    if not characters_dir.exists():
        raise RuntimeError(f"Characters directory not found: {characters_dir}")
    assets = load_character_assets(characters_dir)
    if not assets:
        raise RuntimeError(f"No PNG/GIF assets found in {characters_dir}")
    # Initialize scheduler
    scheduler = Scheduler(app, assets)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
