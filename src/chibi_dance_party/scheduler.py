from __future__ import annotations

import random
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from .character_window import CharacterWindow
from .config import AppConfig


class Scheduler(QtCore.QObject):
    def __init__(self, app: QtWidgets.QApplication, assets: list[Path], config: AppConfig) -> None:
        super().__init__()
        self.app = app
        self.assets = assets
        self.config = config
        self._windows: list[CharacterWindow] = []

        screen = self.app.primaryScreen()
        if screen is None:
            raise RuntimeError("No primary screen detected")
        self.available_rect = screen.availableGeometry()
        self.schedule_next()

    def schedule_next(self) -> None:
        delay_ms = int(random.uniform(self.config.spawn_min_seconds, self.config.spawn_max_seconds) * 1000)
        QtCore.QTimer.singleShot(delay_ms, self.spawn_character)

    def spawn_character(self) -> None:
        self._windows = [w for w in self._windows if not w.isHidden()]
        if len(self._windows) >= self.config.max_active_characters:
            return self.schedule_next()

        asset = random.choice(self.assets)
        pixmap: QtGui.QPixmap | None = None
        movie_path: str | None = None

        if asset.suffix.lower() == ".gif":
            movie = QtGui.QMovie(str(asset))
            if not movie.isValid():
                return self.schedule_next()
            movie_path = str(asset)
            first = movie.currentPixmap()
            if first.isNull():
                movie.start(); first = movie.currentPixmap(); movie.stop()
            if first.isNull():
                return self.schedule_next()
            w, h = first.width(), first.height()
        else:
            pixmap = QtGui.QPixmap(str(asset))
            if pixmap.isNull():
                return self.schedule_next()
            w, h = pixmap.width(), pixmap.height()

        x, y = self._spawn_position(w, h)
        window = CharacterWindow(
            pixmap=pixmap,
            movie_path=movie_path,
            duration_ms=int(self.config.visible_duration_seconds * 1000),
            fade_out_ms=int(self.config.fade_out_seconds * 1000),
        )
        window.move(x, y)
        window.show()
        self._windows.append(window)
        window.destroyed.connect(lambda: self._safe_remove(window))
        self.schedule_next()

    def _safe_remove(self, window: CharacterWindow) -> None:
        if window in self._windows:
            self._windows.remove(window)

    def _spawn_position(self, w: int, h: int) -> tuple[int, int]:
        rect = self.available_rect.adjusted(
            self.config.screen_margin,
            self.config.screen_margin,
            -self.config.screen_margin,
            -self.config.screen_margin,
        )
        min_x = rect.left()
        max_x = rect.right() - w
        min_y = rect.top()
        max_y = rect.bottom() - h
        if max_x < min_x or max_y < min_y:
            return self.available_rect.left(), self.available_rect.top()

        mode = self.config.spawn_mode
        if mode == "random":
            return random.randint(min_x, max_x), random.randint(min_y, max_y)
        if mode == "edges":
            edge = random.choice(["top", "bottom", "left", "right"])
            if edge == "top":
                return random.randint(min_x, max_x), min_y
            if edge == "bottom":
                return random.randint(min_x, max_x), max_y
            if edge == "left":
                return min_x, random.randint(min_y, max_y)
            return max_x, random.randint(min_y, max_y)

        # corners and bottom_walk both prioritize bottom corners for now
        corner_x = min_x if random.random() < 0.5 else max_x
        y = random.randint(max(min_y, max_y - max(10, int(rect.height() * 0.1))), max_y)
        return corner_x, y
