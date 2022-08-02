from PySide6.QtWidgets import (
    QWidget, QPushButton, QHBoxLayout, QGridLayout,
    QVBoxLayout, QLabel, QMessageBox
)
from PySide6.QtCore import Qt
from ..abstract_interface.interface import (
    Interface,
    MalformedSaveError,
    SaveAccessError
)
from .gui_commands import GUI_Commands
from ..auxiliaries.constants import CLASSES, GOVT_LEFT_LABELS, RESOURCES


class Scene_Classes(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.top_labels = [
            QLabel(res.title(), self)
            for res in RESOURCES + ["population", "happiness"]
        ]
        self.left_labels = [
            QLabel(f"{social_class.title()}:", self)
            for social_class in CLASSES
        ]

        self.layout_ = QGridLayout(self)
        for i, label in enumerate(self.top_labels):
            label.setAlignment(Qt.AlignCenter)
            self.layout_.addWidget(label, 0, i + 1 if i < 6 else i + 2)
        for i, label in enumerate(self.left_labels):
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.layout_.addWidget(label, i + 1, 0)

        self.data_labels = []
        for i in range(len(self.left_labels)):
            self.data_labels.append([])
            for j in range(len(self.top_labels)):
                label = QLabel(self)
                label.setAlignment(Qt.AlignCenter)
                self.data_labels[i].append(label)
                self.layout_.addWidget(label, i + 1, j + 1 if j < 6 else j + 2)

        self.transfer_buttons = []
        for i, class_name in enumerate(CLASSES):
            self.transfer_buttons.append(QPushButton("Transfer"))
            self.transfer_buttons[i].clicked[None].connect(
                lambda state=None, cn=class_name: self.parent().transfer(cn)
            )
            self.layout_.addWidget(self.transfer_buttons[i], i + 1, 7)

        self.setLayout(self.layout_)
        self.update()

    def update(self):
        ress = round(
            self.parent().interface.state.get_state_data("resources", True), 2
        )
        pops = round(
            self.parent().interface.state.get_state_data("population")
        )
        haps = round(
            self.parent().interface.state.get_state_data("happiness"), 2
        )

        for i, row in enumerate(self.data_labels):
            class_name = CLASSES[i]
            for j, label in enumerate(row):
                if j == 6:
                    label.setText(f"{pops[class_name]}")
                elif j == 7:
                    label.setText(f"{haps[class_name]}")
                else:
                    label.setText(f"{ress[class_name][RESOURCES[j]]}")


class Scene_Govt(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.top_labels = [
            QLabel(res.title(), self)
            for res in RESOURCES
        ]
        self.left_labels = [
            QLabel(text, self) for text in GOVT_LEFT_LABELS
        ]

        self.layout_ = QGridLayout(self)
        for i, label in enumerate(self.top_labels):
            label.setAlignment(Qt.AlignCenter)
            self.layout_.addWidget(label, 0, i + 1)
        for i, label in enumerate(self.left_labels):
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.layout_.addWidget(label, i + 1, 0)

        self.data_labels = []
        for i in range(len(self.left_labels)):
            self.data_labels.append([])
            for j in range(len(self.top_labels)):
                label = QLabel(self)
                label.setAlignment(Qt.AlignCenter)
                self.data_labels[i].append(label)
                self.layout_.addWidget(label, i + 1, j + 1)
        self.setLayout(self.layout_)
        self.update()

    def update(self):
        ress = round(self.parent().interface.state.government.resources, 2)
        for res, label in zip(RESOURCES, self.data_labels[0]):
            label.setText(f"{ress[res]}")
        ress = self.parent().interface.state.government.secure_resources
        for res, label in zip(RESOURCES, self.data_labels[1]):
            label.setText(f"{ress[res]}")
        ress = self.parent().interface.state.government.optimal_resources
        for res, label in zip(RESOURCES, self.data_labels[2]):
            label.setText(f"{ress[res]}")


class Command_Window(GUI_Commands):
    def __init__(self, dirname: str, parent=None):
        super().__init__(parent)

        # Load the game
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

        # 0th layer - header label and some command buttons
        self.l0_layout = QHBoxLayout()

        save_string = self.interface.save_name
        month = f"{self.interface.state.month} {self.interface.state.year}"
        if save_string == "":
            save_string = f"New game: {month}"
        else:
            save_string = f'Loaded game "{save_string}": {month}'
        self.l0_header = QLabel(save_string)
        self.l0_layout.addWidget(self.l0_header)

        self.l0_layout.addStretch()

        self.l0_next_button = QPushButton("End month")
        self.l0_next_button.clicked[None].connect(self.next_month)
        self.l0_layout.addWidget(self.l0_next_button)

        self.l0_save_button = QPushButton("Save game")
        self.l0_save_button.clicked[None].connect(self.save_game)
        self.l0_layout.addWidget(self.l0_save_button)

        self.l0_del_button = QPushButton("Delete save")
        self.l0_del_button.clicked[None].connect(self.delete_save)
        self.l0_layout.addWidget(self.l0_del_button)

        self.l0_layout.addSpacing(10)

        # 1st layer: General state information
        self.l1_data_labels = [
            QLabel("Food:", self),
            QLabel("Wood:", self),
            QLabel("Stone:", self),
            QLabel("Iron:", self),
            QLabel("Tools:", self),
            QLabel("Land:", self),
            QLabel("Population:", self)
        ]

        self.l1_layout = QHBoxLayout()
        self.l1_layout.addSpacing(10)
        for label in self.l1_data_labels:
            self.l1_layout.addWidget(label)

        # 2nd layer: Various menus buttons
        self.l2_menus_buttons = [
            QPushButton("Classes", self),
            QPushButton("Government", self),
            QPushButton("Military", self),
            QPushButton("Laws", self),
            QPushButton("History", self)
        ]
        self.l2_menus_buttons[0].clicked[None].connect(
            lambda: self.set_scene(Scene_Classes(self))
        )
        self.l2_menus_buttons[1].clicked[None].connect(
            lambda: self.set_scene(Scene_Govt(self))
        )

        self.l2_layout = QHBoxLayout()
        for button in self.l2_menus_buttons:
            self.l2_layout.addWidget(button)

        self.layout_ = QVBoxLayout()
        self.layout_.addLayout(self.l0_layout)
        self.layout_.addLayout(self.l1_layout)
        self.layout_.addLayout(self.l2_layout)
        self.layout_.addSpacing(15)
        self.layout_.addStretch()
        self.setLayout(self.layout_)

        self.scene_set = None
        self.update()

        self.setMinimumSize(800, 500)

    def set_scene(self, new_scene):
        if self.scene_set:
            self.layout_.removeWidget(self.scene_set)
            self.scene_set.deleteLater()
        self.scene_set = new_scene
        self.layout_.insertWidget(4, new_scene)

    def update(self):
        # Main menu
        ress = round(self.interface.state.government.resources, 2)
        for label, res in zip(self.l1_data_labels,
                              ress.values()):
            label.setText(
                f"{label.text().split(' ')[0]} {res}"
            )
        self.l1_data_labels[6].setText(
            f"{self.l1_data_labels[6].text().split(' ')[0]} "
            f"{round(self.interface.state.total_population)}"
        )
        # Scene
        if self.scene_set:
            self.scene_set.update()
