from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets


class CharacterWindow(QtWidgets.QWidget):
    def __init__(self, pixmap: QtGui.QPixmap | None = None, movie_path: str | None = None, duration_ms: int = 5000, fade_out_ms: int = 1000) -> None:
        super().__init__(None, QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Tool)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_AlwaysStackOnTop)
        self.pixmap = pixmap
        self.movie: QtGui.QMovie | None = None

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
            self.resize(self.pixmap.size())

        QtCore.QTimer.singleShot(duration_ms, self.fade_and_close)

        self._opacity_anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self._opacity_anim.setDuration(fade_out_ms)
        self._opacity_anim.setStartValue(1.0)
        self._opacity_anim.setEndValue(0.0)
        self._opacity_anim.finished.connect(self.close)

    def fade_and_close(self) -> None:
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
