from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import QWidget
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput


class AudioPlayer(QWidget):
    positionChanged = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(55)

        # Audio playback
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        # Current playback time (seconds)
        self.current_time = 0.0
        self.start = 0.0 # Start time of the display
        self.duration = 0.0 # Duration of the display
        self.playhead_time = 0.0

        self.player.positionChanged.connect(self._position_changed)


    # Public Methods
    def load_audio(self, filename: str):
        self.player.setSource(QUrl.fromLocalFile(filename))


    def toggle_play_pause(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()


    def set_time(self, seconds: float):
        self.player.setPosition(int(seconds * 1000))


    def update_time_range(self, start, duration):
        self.start = start
        self.duration = duration
        self.update()


    def update_playhead(self, time):
        self.playhead_time = time
        self.update()


    # Internal Methods
    def _position_changed(self, ms):
        self.current_time = ms / 1000.0
        self.positionChanged.emit(self.current_time)
        self.update()


    def paintEvent(self, event):
        p = QPainter(self)

        w = self.width()
        h = self.height()

        # Background
        p.fillRect(self.rect(), QColor(55, 55, 55))

        # Border
        p.setPen(QPen(QColor(90, 90, 90)))
        p.drawRect(self.rect().adjusted(0, 0, -1, -1))

        start = self.start
        duration = self.duration

        if duration <= 0:
            return

        x = ((self.current_time - start) / duration) * w

        if 0 <= x <= w:
            if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                p.setPen(QPen(QColor(255, 80, 80), 2))
            else:
                p.setPen(QPen(QColor(80, 80, 255), 2))
            p.drawLine(int(x), 0, int(x), h)


    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        fraction = event.position().x() / max(1, self.width())
        fraction = max(0.0, min(1.0, fraction))

        start = self.start
        duration = self.duration

        new_time = start + fraction * duration

        self.set_time(new_time)
        self.positionChanged.emit(new_time)

        super().mousePressEvent(event)
