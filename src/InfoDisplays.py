from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLineEdit,
    QFrame
)


class CueInspector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QLabel {
                color: white;
            }

            QLineEdit {
                color: white;
            }
        """)

        self.start_edit = QLineEdit()
        self.duration_edit = QLineEdit()
        self.transition_in_edit = QLineEdit()
        self.transition_out_edit = QLineEdit()

        self.start_edit.setReadOnly(True)
        self.duration_edit.setReadOnly(True)
        self.transition_in_edit.setReadOnly(True)
        self.transition_out_edit.setReadOnly(True)

        layout = QFormLayout()
        layout.addRow("Start:", self.start_edit)
        layout.addRow("Duration:", self.duration_edit)
        layout.addRow("Transition In:", self.transition_in_edit)
        layout.addRow("Transition Out:", self.transition_out_edit)

        self.setLayout(layout)


    def display_cue_info(self, cue_object):
        self.start_edit.setText(f"{cue_object.start:.2f}")
        self.duration_edit.setText(f"{cue_object.duration:.2f}")
        self.transition_in_edit.setText(f"{cue_object.transition_in:.2f}")
        self.transition_out_edit.setText(f"{cue_object.transition_out:.2f}")



class AspectRatioWidget(QWidget):
    """A container that keeps its child at a fixed aspect ratio."""

    def __init__(self, aspect_width=16, aspect_height=9):
        super().__init__()

        self.aspect = aspect_width / aspect_height

        self.preview = QFrame(self)
        self.preview.setStyleSheet("""
            background-color: #000;
            border: 2px solid #888;
        """)

    def resizeEvent(self, event):
        w = self.width()
        h = self.height()

        if w / h > self.aspect:
            # Limited by height
            preview_h = h
            preview_w = int(preview_h * self.aspect)
        else:
            # Limited by width
            preview_w = w
            preview_h = int(preview_w / self.aspect)

        x = (w - preview_w) // 2
        y = (h - preview_h) // 2

        self.preview.setGeometry(QRect(x, y, preview_w, preview_h))