from PySide6.QtWidgets import (
    QWidget, QPushButton, QHBoxLayout, QGridLayout,
    QVBoxLayout, QLabel, QMessageBox
)
from PySide6.QtCore import Qt

from sources.gui.resources_display import Resources_Display
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
            self.layout_.addWidget(label, 0, i + 1 if i < 6 else i + 3)
        for i, label in enumerate(self.left_labels):
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.layout_.addWidget(label, i + 1, 0)

        self.resources_labels: list[Resources_Display] = []
        for i in range(len(self.left_labels)):
            self.resources_labels.append(Resources_Display())
            self.resources_labels[i].setAlignment(Qt.AlignCenter)
            self.resources_labels[i].add_to_grid_layout(self.layout_, i + 1, 1)

        self.population_labels: list[QLabel] = []
        for i in range(len(self.left_labels)):
            self.population_labels.append(QLabel())
            self.population_labels[i].setAlignment(Qt.AlignCenter)
            self.layout_.addWidget(self.population_labels[i], i + 1, 9)

        self.happiness_labels: list[QLabel] = []
        for i in range(len(self.left_labels)):
            self.happiness_labels.append(QLabel())
            self.happiness_labels[i].setAlignment(Qt.AlignCenter)
            self.layout_.addWidget(self.happiness_labels[i], i + 1, 10)

        self.transfer_buttons: list[QPushButton] = []
        for i, class_name in enumerate(CLASSES):
            self.transfer_buttons.append(QPushButton("Transfer"))
            self.transfer_buttons[i].clicked[None].connect(
                lambda state=None, cn=class_name: self.parent().transfer(cn)
            )
            self.layout_.addWidget(self.transfer_buttons[i], i + 1, 7)

        self.promote_buttons: list[QPushButton] = []
        for i, class_name in enumerate(CLASSES[:3]):
            self.promote_buttons.append(QPushButton("Promote"))
            self.promote_buttons[i].clicked[None].connect(
                lambda state=None, cn=class_name: self.parent().promote(cn)
            )
            self.layout_.addWidget(self.promote_buttons[i], i + 1, 8)

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

        for i in range(len(self.resources_labels)):
            class_name = CLASSES[i]
            self.resources_labels[i].set_resources(ress[class_name])
            self.population_labels[i].setText(f"{pops[class_name]}")
            self.happiness_labels[i].setText(f"{haps[class_name]}")

        for i, button in enumerate(self.transfer_buttons):
            button.setEnabled(
                self.parent().interface.state.classes[i].population > 0
            )


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

        self.data_labels: list[Resources_Display] = []
        for i in range(len(self.left_labels)):
            self.data_labels.append(Resources_Display())
            self.data_labels[i].setAlignment(Qt.AlignCenter)
            self.data_labels[i].add_to_grid_layout(self.layout_, i + 1, 1)
        self.setLayout(self.layout_)
        self.update()

    def update(self):
        ress = round(self.parent().interface.state.government.resources, 2)
        self.data_labels[0].set_resources(ress)
        ress = self.parent().interface.state.government.secure_resources
        self.data_labels[1].set_resources(ress)
        ress = self.parent().interface.state.government.optimal_resources
        self.data_labels[2].set_resources(ress)


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

        self.l0_header = QLabel()
        self.l0_layout.addWidget(self.l0_header)

        self.l0_layout.addStretch()

        self.l0_exec_button = QPushButton("Execute command")
        self.l0_exec_button.clicked[None].connect(self.execute_command)
        self.l0_layout.addWidget(self.l0_exec_button)

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
        self.l1_header = QLabel("Current prices:")
        self.l1_prices = Resources_Display()

        self.l1_layout = QHBoxLayout()
        self.l1_layout.addSpacing(10)
        self.l1_layout.addWidget(self.l1_header)
        self.l1_prices.add_to_layout(self.l1_layout)

        # 2nd layer: General state information
        self.l2_header = QLabel("Government resources:")
        self.l2_resources = Resources_Display()
        self.l2_population = QLabel("Population:", self)

        self.l2_layout = QHBoxLayout()
        self.l2_layout.addSpacing(10)
        self.l2_layout.addWidget(self.l2_header)
        self.l2_resources.add_to_layout(self.l2_layout)
        self.l2_layout.addWidget(self.l2_population)

        # 3rd layer: Various menus buttons
        self.l3_menus_buttons = [
            QPushButton("Classes", self),
            QPushButton("Government", self),
            QPushButton("Military", self),
            QPushButton("Laws", self),
            QPushButton("History", self)
        ]
        self.l3_menus_buttons[0].clicked[None].connect(
            lambda: self.set_scene(Scene_Classes(self))
        )
        self.l3_menus_buttons[1].clicked[None].connect(
            lambda: self.set_scene(Scene_Govt(self))
        )

        self.l3_layout = QHBoxLayout()
        for button in self.l3_menus_buttons:
            self.l3_layout.addWidget(button)

        self.layout_ = QVBoxLayout()
        self.layout_.addLayout(self.l0_layout)
        self.layout_.addLayout(self.l1_layout)
        self.layout_.addLayout(self.l2_layout)
        self.layout_.addLayout(self.l3_layout)
        self.layout_.addSpacing(15)
        self.layout_.addStretch()
        self.setLayout(self.layout_)

        self.scene_set = None
        self.update()

        self.setMinimumSize(900, 600)

    def set_scene(self, new_scene):
        if self.scene_set:
            self.layout_.removeWidget(self.scene_set)
            self.scene_set.deleteLater()
        self.scene_set = new_scene
        self.layout_.insertWidget(4, new_scene)

    def update(self):
        # Main menu
        save_string = self.interface.save_name
        month = f"{self.interface.state.month} {self.interface.state.year}"
        if save_string == "":
            save_string = f"New game: {month}"
        else:
            save_string = f'Loaded game "{save_string}": {month}'
        self.l0_header.setText(save_string)

        prices = round(self.interface.state.prices, 4)
        self.l1_prices.set_resources(prices)

        ress = round(self.interface.state.government.resources, 2)
        self.l2_resources.set_resources(ress)
        self.l2_population.setText(
            f"Population: {round(self.interface.state.total_population)}"
        )
        # Scene
        if self.scene_set:
            self.scene_set.update()
