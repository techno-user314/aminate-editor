from math import log2

from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QColor, QFontMetrics, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class TimeRuler(QWidget):
    timeRangeUpdated = pyqtSignal(float, float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(35)

        self.scroll_time = 0.0 # left edge of widget in seconds.
        self.pixels_per_second = 100.0 # pixels per second

        self.background = QColor(45, 45, 45)
        self.tick_color = QColor(190, 190, 190)


    def scroll_by(self, seconds: float):
        self.set_scroll(self.scroll_time + seconds)


    def set_scroll(self, seconds: float):
        self.scroll_time = max(0.0, seconds)
        self.update()


    def zoom_by(self, factor: float, anchor_x=None):
        if anchor_x is None:
            anchor_x = self.width() * 0.5
        anchor_time = self.pixel_to_time(anchor_x)

        new_zoom = self.pixels_per_second * factor
        self.set_zoom(new_zoom)

        # Keep anchor time fixed
        self.scroll_time = anchor_time - anchor_x / self.pixels_per_second
        self.scroll_time = max(0.0, self.scroll_time)

        self.update()


    def set_zoom(self, pixels_per_second: float):
        self.pixels_per_second = pixels_per_second
        self.update()


    def pixel_to_time(self, x):
        return x / self.pixels_per_second + self.scroll_time


    @staticmethod
    def format_time(seconds, seconds_per_tick):
        total_ms = round(seconds * 1000)

        total_seconds, ms = divmod(total_ms, 1000)
        minutes, sec = divmod(total_seconds, 60)
        hours, minute = divmod(minutes, 60)

        if hours > 0: time = f"{hours:02}:{minute:02}"
        else: time = f"{minute:02}:{sec:02}"

        if seconds_per_tick < 1:
            return time + f".{ms:03}"
        elif seconds_per_tick < 8:
            return time + f".{int(ms/100)}"
        else:
            return time


    def time_to_pixel(self, seconds):
        return (seconds - self.scroll_time) * self.pixels_per_second


    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        p.fillRect(self.rect(), self.background)
        p.setPen(QPen(self.tick_color))
        font_metrics = QFontMetrics(self.font())

        spacing_time = 2 ** -int(log2(self.pixels_per_second)-7.5) / 10
        minor_tick = int(spacing_time * self.pixels_per_second)
        medium_tick_every = 5
        major_tick_every = 10

        for step, x in enumerate(range(0, self.width(), minor_tick)):
            if step % major_tick_every == 0:
                p.drawLine(int(x), 0, int(x), 18)
                p.drawText(
                    QRectF(x + 4, 33 - font_metrics.ascent(), 120, 20),
                    self.format_time(self.pixel_to_time(x), spacing_time*10),
                )
            elif step % medium_tick_every == 0:
                p.drawLine(int(x), 6, int(x), 16)
            else:
                p.drawLine(int(x), 10, int(x), 16)


    def update_time_range(self):
        visible_seconds = self.width() / self.pixels_per_second
        self.timeRangeUpdated.emit(self.scroll_time, visible_seconds)


    def showEvent(self, event):
        super().showEvent(event)
        self.update_time_range()


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_time_range()


    def wheelEvent(self, event):
        visible_seconds = self.width() / self.pixels_per_second

        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            self.zoom_by(factor, event.position().x())
        else:
            # Scroll
            seconds = -event.angleDelta().y() / 120 * (visible_seconds * 0.05)
            self.scroll_by(seconds)
        self.timeRangeUpdated.emit(self.scroll_time, visible_seconds)
        event.accept()