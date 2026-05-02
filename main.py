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

    def __init__(self, pixmap: QtGui.QPixmap, duration_ms: int = 5000) -> None:
        super().__init__(flags=QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Tool)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_AlwaysStackOnTop)
        self.pixmap = pixmap
        self.duration_ms = duration_ms
        # Set window size to image size
        self.resize(pixmap.size())
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

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawPixmap(0, 0, self.pixmap)


class Scheduler(QtCore.QObject):
    """Schedules chibi character windows at random intervals and positions."""

    def __init__(self, app: QtWidgets.QApplication, images: list[QtGui.QPixmap]) -> None:
        super().__init__()
        self.app = app
        self.images = images
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
        # Choose random image
        pixmap = random.choice(self.images)
        # Determine random position within screen bounds
        w = pixmap.width()
        h = pixmap.height()
        x = random.randint(self.available_rect.left(), self.available_rect.right() - w)
        y = random.randint(self.available_rect.top(), self.available_rect.bottom() - h)
        # Create window
        window = CharacterWindow(pixmap)
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


def load_images(characters_dir: Path) -> list[QtGui.QPixmap]:
    """Load all PNG images from the characters directory."""
    images: list[QtGui.QPixmap] = []
    for file in characters_dir.iterdir():
        if file.suffix.lower() == ".png":
            pixmap = QtGui.QPixmap(str(file))
            if not pixmap.isNull():
                images.append(pixmap)
    return images


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    # Load images
    characters_dir = Path(__file__).resolve().parent / "characters"
    if not characters_dir.exists():
        raise RuntimeError(f"Characters directory not found: {characters_dir}")
    images = load_images(characters_dir)
    if not images:
        raise RuntimeError(f"No PNG images found in {characters_dir}")
    # Initialize scheduler
    scheduler = Scheduler(app, images)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
