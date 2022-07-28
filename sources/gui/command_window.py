from PySide6.QtWidgets import (
    QPushButton, QHBoxLayout,
    QVBoxLayout, QLabel, QMessageBox
)
from ..abstract_interface.interface import (
    Interface,
    MalformedSaveError,
    SaveAccessError
)
from .gui_commands import GUI_Commands


class Command_Window(GUI_Commands):
    def __init__(self, dirname: str, parent=None):
        super().__init__(parent)

        self.interface = Interface()
        try:
            self.interface.load_data(dirname)
        except SaveAccessError:
            QMessageBox.critical(self, "Critical Error", "Failed to open the"
                                 " save file. Shutting down.")
            raise
        except MalformedSaveError:
            QMessageBox.critical(self, "Critical Error", "The program"
                                 " encountered an error while loading the save"
                                 " file. Probably the file format is invalid."
                                 " Shutting down.")
            raise

        self.menus_buttons = [
            QPushButton("Classes", self),
            QPushButton("Government", self),
            QPushButton("Military", self),
            QPushButton("Laws", self),
            QPushButton("History", self)
        ]

        self.menus_buttons_layout = QHBoxLayout()
        for button in self.menus_buttons:
            self.menus_buttons_layout.addWidget(button)

        self.top_labels = [
            QLabel("Food:", self),
            QLabel("Wood:", self),
            QLabel("Stone:", self),
            QLabel("Iron:", self),
            QLabel("Tools:", self),
            QLabel("Land:", self),
            QLabel("Population:", self)
        ]

        self.top_labels_layout = QHBoxLayout()
        self.top_labels_layout.addSpacing(10)
        for label in self.top_labels:
            self.top_labels_layout.addWidget(label)

        self.next_month_button = QPushButton("End month")
        self.next_month_button.clicked.connect(self.next_month)
        self.top_labels_layout.addWidget(self.next_month_button)

        self.save_button = QPushButton("Save game")
        self.save_button.clicked.connect(self.save_game)
        self.top_labels_layout.addWidget(self.save_button)

        self.del_button = QPushButton("Delete save")
        self.del_button.clicked.connect(self.delete_save)
        self.top_labels_layout.addWidget(self.del_button)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.top_labels_layout)
        self.main_layout.addLayout(self.menus_buttons_layout)
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)

        self.update_labels()
        self.setMinimumSize(800, 500)
