from enum import Enum

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QLineEdit
)
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush

from CueInfo import CueInfo


class TimelineManager(QWidget):
    cueUpdated = pyqtSignal(object)


    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_display_duration = 0.0
        self.current_display_start = 0.0
        self.current_playhead_time = 0.0

        self.timelines = []
        self.selected_track = None

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        self.add_button = QPushButton("+")
        self.remove_button = QPushButton("-")

        self.add_button.clicked.connect(self.add_track)
        self.remove_button.clicked.connect(self.remove_track)

        controls_layout.addWidget(self.add_button)
        controls_layout.addWidget(self.remove_button)
        controls_layout.addStretch()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        # Container holding timelines
        self.timeline_container = QWidget()

        self.timeline_layout = QVBoxLayout(self.timeline_container)
        self.timeline_layout.setContentsMargins(0, 0, 0, 0)
        self.timeline_layout.setSpacing(2)

        # Important: allow horizontal expansion
        self.timeline_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )

        self.scroll_area.setWidget(self.timeline_container)

        self.main_layout.addWidget(controls)
        self.main_layout.addWidget(self.scroll_area)


    def add_track(self):
        timeline = TimelineTrack(
            f"Track {len(self.timelines)}",
            self.current_display_start,
            self.current_display_duration,
            self.current_playhead_time
        )
        timeline.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        timeline.trackSelected.connect(self.set_selected_track)
        timeline.clipUpdated.connect(lambda clip: self.cueUpdated.emit(clip.cue))
        self.timeline_layout.addWidget(timeline)
        self.timelines.append(timeline)
        self.set_selected_track(timeline)


    def remove_track(self):
        if self.selected_track is not None:
            delete_idx = self.timelines.index(self.selected_track)

            self.timelines.pop(delete_idx)
            self.timeline_layout.removeWidget(self.selected_track)
            self.selected_track.deleteLater()

            self.selected_track = None
            if delete_idx < len(self.timelines):
                self.set_selected_track(self.timelines[delete_idx])
            elif len(self.timelines) > 0:
                self.set_selected_track(self.timelines[delete_idx-1])


    def update_time_range(self, start, dur):
        self.current_display_start = start
        self.current_display_duration = dur
        for timeline in self.timelines:
            timeline.update_time_range(start, dur)


    def set_selected_track(self, track):
        if self.selected_track is not None:
            self.selected_track.set_selected(False)
        self.selected_track = track
        self.selected_track.set_selected(True)


    def update_playhead(self, new_time):
        self.current_playhead_time = new_time
        for timeline in self.timelines:
            timeline.update_playhead(new_time)


    def create_clip(self):
        if self.selected_track is not None:
            self.selected_track.create_clip()


    def delete_clip(self):
        if self.selected_track is not None:
            self.selected_track.delete_clip()


    def set_clip_start_to_playhead(self):
        if self.selected_track is not None:
            self.selected_track.set_start_to_playhead()


    def set_clip_end_to_playhead(self):
        if self.selected_track is not None:
            self.selected_track.set_end_to_playhead()


class TimelineTrack(QWidget):
    HEIGHT = 75
    NAME_WIDTH = 75
    trackSelected = pyqtSignal(object)
    clipUpdated = pyqtSignal(object)

    def __init__(self, name, display_start, display_dur, playhead_time, parent=None):
        super().__init__(parent)

        self.setFixedHeight(self.HEIGHT)

        self.selected = False

        # Visible time range
        self.start_time = display_start
        self.duration = display_dur

        # Current playhead
        self.playhead_time = playhead_time

        # Timeline clips
        self.clips = []
        self.selected_clip = None

        # Name entry
        self.name_edit = QLineEdit(name, self)
        self.name_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_edit.setGeometry(
            5,
            5,
            self.NAME_WIDTH - 10,
            self.NAME_WIDTH - 10
        )

        self.name_edit.setStyleSheet("""
            QLineEdit {
                background-color: #444;
                color: white;
                border: 1px solid #666;
            }
        """)

        self.setMouseTracking(True)


    def set_selected(self, selected):
        for clip in self.clips:
            clip.selected = False
        self.selected = selected

        self.update()


    def update_time_range(self, start_time, duration):
        self.start_time = start_time
        self.duration = max(duration, 0.001)
        self.update()


    def update_playhead(self, time):
        self.playhead_time = time
        self.update()


    def create_clip(self):
        clip = TimelineClip(
            start=self.playhead_time,
            end=self.playhead_time + 3.0
        )

        self.clips.append(clip)
        self.selected_clip = clip

        self.update()


    def delete_clip(self):
        if self.selected_clip is None:
            return

        # Remove from timeline
        if self.selected_clip in self.clips:
            self.clips.remove(self.selected_clip)

        # Clear selection
        self.selected_clip.selected = False
        self.selected_clip = None

        self.update()


    def set_start_to_playhead(self):
        if self.selected_clip is None:
            return

        self.selected_clip.start = min(
            self.playhead_time,
            self.selected_clip.end
        )

        self.update()


    def set_end_to_playhead(self):
        if self.selected_clip is None:
            return

        self.selected_clip.end = max(
            self.playhead_time,
            self.selected_clip.start
        )

        self.update()


    def time_to_pixel(self, time):
        timeline_width = self.width() - self.NAME_WIDTH

        return (
            self.NAME_WIDTH +
            ((time - self.start_time) / self.duration) *
            timeline_width
        )


    def pixel_to_time(self, x):
        timeline_width = self.width() - self.NAME_WIDTH

        return (
            self.start_time +
            ((x - self.NAME_WIDTH) / timeline_width) *
            self.duration
        )


    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        if event.position().x() < self.NAME_WIDTH:
            return

        self.trackSelected.emit(self)
        self.selected_clip = None

        # Check clips from front to back
        for clip in reversed(self.clips):
            if clip.is_hit(event.position().x(), self):
                self.selected_clip = clip
                clip.selected = True
                self.clipUpdated.emit(clip)
            else:
                clip.selected = False

        self.update()


    def mouseMoveEvent(self, event):
        if self.selected_clip is None:
            return

        self.selected_clip.drag(
            event.position().x(),
            self
        )

        self.update()


    def mouseReleaseEvent(self, event):
        if self.selected_clip is not None:
            self.selected_clip.end_drag()
            self.clipUpdated.emit(self.selected_clip)


    def paintEvent(self, event):
        painter = QPainter(self)

        # Background
        painter.fillRect(
            self.rect(),
            QColor(45, 45, 45)
        )

        # Name panel
        painter.fillRect(
            0,
            0,
            self.NAME_WIDTH,
            self.HEIGHT,
            QColor(60, 60, 60)
        )

        # Separator
        painter.setPen(
            QPen(QColor(120, 120, 120), 2)
        )

        painter.drawLine(
            self.NAME_WIDTH,
            0,
            self.NAME_WIDTH,
            self.height()
        )

        # Timeline background
        painter.fillRect(
            self.NAME_WIDTH,
            0,
            self.width() - self.NAME_WIDTH,
            self.height(),
            QColor(35, 35, 35)
        )

        # Draw clips at least partially inside the display area
        painter.save()

        painter.setClipRect(
            self.NAME_WIDTH,
            0,
            self.width() - self.NAME_WIDTH,
            self.height()
        )

        for clip in self.clips:
            clip.draw(painter, self)

        # Playhead
        if (
            self.start_time
            <= self.playhead_time
            <= self.start_time + self.duration
            and self.selected
        ):
            x = self.time_to_pixel(self.playhead_time)

            painter.setPen(
                QPen(QColor(255, 50, 50), 2)
            )

            painter.drawLine(
                int(x),
                0,
                int(x),
                self.height()
            )

        painter.restore()


class DragMode(Enum):
    NONE = 0
    MOVE = 1
    START = 2
    END = 3
    FADE_IN = 4
    FADE_OUT = 5


class TimelineClip:
    HANDLE_WIDTH = 6
    HANDLE_RADIUS = 5
    CLIP_HEIGHT = 36
    CONNECTOR_Y = 18


    def __init__(self, start=0.0, end=3.0):
        self.selected = False
        self.cue = CueInfo(start, end - start)

        self.drag_mode = DragMode.NONE
        self.drag_offset = 0.0


    def is_visible(self, timeline):
        visible_start = timeline.start_time
        visible_end = visible_start + timeline.duration

        return not (
            self.cue.end < visible_start or
            self.cue.start > visible_end
        )


    def draw(self, painter: QPainter, timeline):
        if not self.is_visible(timeline):
            return
        x1 = int(timeline.time_to_pixel(self.cue.start))
        x2 = int(timeline.time_to_pixel(self.cue.end))
        y = int((timeline.height() - self.CLIP_HEIGHT) / 2)

        # Cue body
        cue_rect = QRectF(x1, y, x2 - x1, self.CLIP_HEIGHT)
        cue_color = (50, 180, 255) if self.selected else (255, 180, 50)

        painter.setPen(QPen(QColor(240, 220, 80), 2))
        painter.setBrush(QBrush(QColor(*cue_color)))
        painter.drawRect(cue_rect)

        # Resizing handles
        handle_rect = lambda x : QRectF(
            x - self.HANDLE_WIDTH / 2, y,
            self.HANDLE_WIDTH, self.CLIP_HEIGHT
        )
        painter.fillRect(handle_rect(x1), QColor(255, 255, 255))
        painter.fillRect(handle_rect(x2), QColor(255, 255, 255))

        # Transition handles
        in_time_x = int(timeline.time_to_pixel(
            self.cue.start - self.cue.transition_in
        ))
        out_time_x = int(timeline.time_to_pixel(
            self.cue.end + self.cue.transition_out
        ))
        cy = int(timeline.height() / 2)

        painter.setPen(QPen(QColor(180, 180, 180), 1))
        painter.drawLine(in_time_x, cy, x1, cy)
        painter.drawLine(x2, cy, out_time_x, cy)

        transition_handle = lambda x : QRectF(
            x - self.HANDLE_RADIUS,
            cy - self.HANDLE_RADIUS,
            self.HANDLE_RADIUS * 2,
            self.HANDLE_RADIUS * 2
        )
        painter.setBrush(QColor(240, 240, 240))
        painter.drawEllipse(transition_handle(in_time_x))
        painter.drawEllipse(transition_handle(out_time_x))


    def is_hit(self, x, timeline):
        start = timeline.time_to_pixel(self.cue.start)
        end = timeline.time_to_pixel(self.cue.end)
        trans_left = timeline.time_to_pixel(self.cue.start - self.cue.transition_in)
        trans_right = timeline.time_to_pixel(self.cue.end + self.cue.transition_out)

        hit_near = lambda target: abs(x - target) < 7

        if hit_near(trans_right):
            self.drag_mode = DragMode.FADE_OUT
        elif hit_near(trans_left):
            self.drag_mode = DragMode.FADE_IN
        elif hit_near(start):
            self.drag_mode = DragMode.START
        elif hit_near(end):
            self.drag_mode = DragMode.END
        elif start < x < end:
            self.drag_mode = DragMode.MOVE
        else:
            self.drag_mode = DragMode.NONE

        if self.drag_mode == DragMode.MOVE:
            self.drag_offset = (timeline.pixel_to_time(x) - self.cue.start)

        return self.drag_mode != DragMode.NONE


    def drag(self, x, timeline):
        t = timeline.pixel_to_time(x)
        match self.drag_mode:
            case DragMode.START:
                new_start = min(t, self.cue.end - 0.01)
                self.cue.duration -= (new_start - self.cue.start)
                self.cue.start = new_start

            case DragMode.END:
                self.cue.duration = max(t - self.cue.start, 0.01)

            case DragMode.MOVE:
                self.cue.start = t - self.drag_offset

            case DragMode.FADE_IN:
                self.cue.transition_in = max(0, self.cue.start - t)

            case DragMode.FADE_OUT:
                self.cue.transition_out = max(0, t - self.cue.end)


    def end_drag(self):
        self.drag_mode = DragMode.NONE