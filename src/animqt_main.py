import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from TimeRuler import TimeRuler
from AudioPlayer import AudioPlayer
from TimelineManager import TimelineManager
from InfoDisplays import CueInspector, AspectRatioWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Aminate - Canvas Commons Frontend Animation Editor")
        self.resize(1400, 900)

        self.setStyleSheet("background-color: #222;")

        root = QWidget()
        self.setCentralWidget(root)
        self._create_menubar()

        # Main Layout
        layout = QVBoxLayout(root)
        layout.setContentsMargins(5, 5, 5, 5)

        vertical = QSplitter(Qt.Orientation.Vertical)

        # Top workspace
        top_workspace = QSplitter(Qt.Orientation.Horizontal)

        inspector = CueInspector()
        preview = AspectRatioWidget()

        top_workspace.addWidget(inspector)
        top_workspace.addWidget(preview)

        # Bottom workspace
        timeline = TimelineManager()

        bottom_workspace = QHBoxLayout()
        bottom_workspace.setContentsMargins(75,0,0,0)

        bottom_widgets = QVBoxLayout()

        time_ruler = TimeRuler()
        audio_player = AudioPlayer()

        bottom_widgets.addWidget(time_ruler)
        bottom_widgets.addWidget(audio_player)

        bottom_workspace.addLayout(bottom_widgets)

        time_ruler.timeRangeUpdated.connect(audio_player.update_time_range)
        time_ruler.timeRangeUpdated.connect(timeline.update_time_range)
        audio_player.positionChanged.connect(timeline.update_playhead)

        timeline.cueUpdated.connect(inspector.display_cue_info)

        # Temporary Shortcuts bindings
        audio_player.load_audio("/home/skiddie/YouTube/0003/0003.wav")
        self.play_action = QAction("Play/Pause", self)
        self.play_action.setShortcut(QKeySequence("Space"))
        self.play_action.triggered.connect(audio_player.toggle_play_pause)
        self.addAction(self.play_action)

        self.clip_action = QAction("Create clip", self)
        self.clip_action.setShortcut(QKeySequence("R"))
        self.clip_action.triggered.connect(timeline.create_clip)
        self.addAction(self.clip_action)

        self.clip_start_action = QAction("Set clip start to playhead", self)
        self.clip_start_action.setShortcut(QKeySequence("S"))
        self.clip_start_action.triggered.connect(timeline.set_clip_start_to_playhead)
        self.addAction(self.clip_start_action)

        self.clip_end_action = QAction("Set clip end to playhead", self)
        self.clip_end_action.setShortcut(QKeySequence("F"))
        self.clip_end_action.triggered.connect(timeline.set_clip_end_to_playhead)
        self.addAction(self.clip_end_action)

        self.del_clip_action = QAction("Delete Clip", self)
        self.del_clip_action.setShortcut(QKeySequence("D"))
        self.del_clip_action.triggered.connect(timeline.delete_clip)
        self.addAction(self.del_clip_action)

        # Vertical packing
        vertical.addWidget(top_workspace)
        vertical.addWidget(timeline)

        vertical.setStretchFactor(0, 5)
        vertical.setStretchFactor(1, 1)

        layout.addWidget(vertical)
        layout.addLayout(bottom_workspace)


    def _create_menubar(self):
        menu = self.menuBar()
        menu.setStyleSheet("""
            QMenuBar {
                background-color: transparent;
                color: #ffffff;
            }
            QMenu::item {
                background-color: transparent;
                color: #ffffff;            /* White text for individual items */
                padding: 4px 20px;         /* Spacing around text */
            }
            QMenu::item:selected {
                background-color: #0078d4; /* Background color when hovering over an item */
            }
        """)

        file_menu = menu.addMenu("&File")

        new_action = QAction("New Project", self)
        open_action = QAction("Open Project...", self)
        audio_action = QAction("Open Audio...", self)
        save_action = QAction("Save Project", self)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(audio_action)
        file_menu.addSeparator()
        file_menu.addAction(save_action)

        edit_menu = menu.addMenu("&Edit")

        undo_action = QAction("Undo", self)
        redo_action = QAction("Redo", self)
        copy_action = QAction("Copy", self)
        paste_action = QAction("Paste", self)
        shortcut_action = QAction("Shorcuts", self)

        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)
        edit_menu.addSeparator()
        edit_menu.addAction(shortcut_action)

        clip_menu = menu.addMenu("&Clips")

        create_action = QAction("New Clip at Playhead", self)
        delete_action = QAction("Delete Selected Clip", self)

        clip_menu.addAction(create_action)
        clip_menu.addAction(delete_action)

        project_menu = menu.addMenu("&Project")

        generate_action = QAction("Generate Canvas Commons code", self)

        project_menu.addAction(generate_action)

        about_menu = menu.addMenu("&About")

        documentation_action = QAction("Documentation", self)
        contribute_action = QAction("Contribute", self)
        license_action = QAction("License", self)

        about_menu.addAction(documentation_action)
        about_menu.addAction(contribute_action)
        about_menu.addAction(license_action)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())