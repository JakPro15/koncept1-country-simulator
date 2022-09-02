from __future__ import annotations
from abc import ABC, abstractmethod

import sys
from math import floor

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QMessageBox,
                               QPushButton, QVBoxLayout, QWidget, QDialog)

from ..abstract_interface.interface import (Interface, MalformedSaveError,
                                            SaveAccessError)
from ..auxiliaries.constants import GOVT_LEFT_LABELS, INBUILT_RESOURCES
from ..auxiliaries.enums import CLASS_NAME_STR, RESOURCE_STR, Class_Name
from ..cli.cli_commands import ShutDownCommand
from ..gui.number_select_dialog import Number_Select_Dialog
from ..gui.resources_display import Resources_Display
from ..state.state_data_employ_and_commands import (EveryoneDeadError,
                                                    RebellionError)
from .auxiliaries import crashing_slot
from .execute_dialog import Execute_Dialog
from .save_dialog import Save_Dialog
from .transfer_dialog import Transfer_Dialog

# @TODO: Add estimated happiness to transfer dialog


class AbstractScene(QWidget, ABC):
    @abstractmethod
    def __init__(self, parent: Command_Window) -> None:
        ...

    @abstractmethod
    def update(self) -> None:
        ...


class Scene_Classes(AbstractScene):
    def __init__(self, parent: Command_Window) -> None:
        super().__init__(parent)
        self._parent = parent
        self.top_labels = [
            QLabel(res.title(), self)
            for res in RESOURCE_STR + ["population", "happiness"]
        ]
        self.left_labels = [
            QLabel(f"{class_name.title()}:", self)
            for class_name in CLASS_NAME_STR
        ]

        self.main_layout = QGridLayout(self)
        for i, label in enumerate(self.top_labels):
            label.setAlignment(Qt.AlignCenter)
            self.main_layout.addWidget(label, 0, i + 1 if i < 6 else i + 3)
        for i, label in enumerate(self.left_labels):
            right_center_align: Qt.Alignment = Qt.AlignRight | Qt.AlignVCenter
            label.setAlignment(right_center_align)
            self.main_layout.addWidget(label, i + 1, 0)

        self.resources_labels: list[Resources_Display] = []
        for i in range(len(self.left_labels)):
            self.resources_labels.append(Resources_Display())
            self.resources_labels[i].setAlignment(Qt.AlignCenter)
            self.resources_labels[i].add_to_grid_layout(
                self.main_layout, i + 1, 1
            )

        self.population_labels: list[QLabel] = []
        for i in range(len(self.left_labels)):
            self.population_labels.append(QLabel())
            self.population_labels[i].setAlignment(Qt.AlignCenter)
            self.main_layout.addWidget(self.population_labels[i], i + 1, 9)

        self.happiness_labels: list[QLabel] = []
        for i in range(len(self.left_labels)):
            self.happiness_labels.append(QLabel())
            self.happiness_labels[i].setAlignment(Qt.AlignCenter)
            self.main_layout.addWidget(self.happiness_labels[i], i + 1, 10)

        self.transfer_buttons: list[QPushButton] = []

        for i, class_name in enumerate(Class_Name):
            self.transfer_buttons.append(QPushButton("Transfer"))

            def this_transfer(state: None = None) -> None:
                nonlocal class_name
                self._parent.transfer(class_name)

            self.transfer_buttons[i].clicked[None].connect(  # type: ignore
                this_transfer
            )
            self.main_layout.addWidget(self.transfer_buttons[i], i + 1, 7)

        self.promote_buttons: list[QPushButton] = []
        for i, class_name in enumerate(list(Class_Name)[:3]):
            self.promote_buttons.append(QPushButton("Promote"))

            def this_promote(state: None = None) -> None:
                nonlocal class_name
                self._parent.promote(class_name)

            self.promote_buttons[i].clicked[None].connect(  # type: ignore
                this_promote
            )
            self.main_layout.addWidget(self.promote_buttons[i], i + 1, 8)

        self.setLayout(self.main_layout)
        self.update()

    def update(self) -> None:
        ress = {
            class_name.name: round(
                self._parent.interface.state.classes[class_name].resources, 2)
            for class_name in Class_Name
        }

        pops = {
            class_name.name: round(
                self._parent.interface.state.classes[class_name].population)
            for class_name in Class_Name
        }

        haps = {
            class_name.name: round(
                self._parent.interface.state.classes[class_name].happiness, 2)
            for class_name in Class_Name
        }

        for i in range(len(self.resources_labels)):
            class_name = CLASS_NAME_STR[i]
            self.resources_labels[i].set_resources(ress[class_name])
            self.population_labels[i].setText(f"{pops[class_name]}")
            self.happiness_labels[i].setText(f"{haps[class_name]}")

        for i, button in enumerate(self.transfer_buttons):
            button.setEnabled(
                self._parent.interface.state.classes[
                    Class_Name(i)].population > 0
            )


class Scene_Govt(AbstractScene):
    def __init__(self, parent: Command_Window):
        super().__init__(parent)
        self._parent = parent

        self.top_labels = [
            QLabel(res.title(), self)
            for res in RESOURCE_STR
        ]
        self.left_labels = [
            QLabel(text, self) for text in GOVT_LEFT_LABELS
        ]

        self.layout_ = QGridLayout(self)
        for i, label in enumerate(self.top_labels):
            label.setAlignment(Qt.AlignCenter)
            self.layout_.addWidget(label, 0, i + 1)
        for i, label in enumerate(self.left_labels):
            right_center_align: Qt.Alignment = Qt.AlignRight | Qt.AlignVCenter
            label.setAlignment(right_center_align)
            self.layout_.addWidget(label, i + 1, 0)

        self.data_labels: list[Resources_Display] = []
        for i in range(len(self.left_labels)):
            self.data_labels.append(Resources_Display())
            self.data_labels[i].setAlignment(Qt.AlignCenter)
            self.data_labels[i].add_to_grid_layout(self.layout_, i + 1, 1)
        self.setLayout(self.layout_)
        self.update()

    def update(self):
        ress = round(self._parent.interface.state.government.resources, 2)
        self.data_labels[0].set_resources(ress)
        ress = round(
            self._parent.interface.state.government.secure_resources, 2)
        self.data_labels[1].set_resources(ress)
        ress = round(
            self._parent.interface.state.government.optimal_resources, 2)
        self.data_labels[2].set_resources(ress)


class Command_Window(QDialog):
    def __init__(self, dirname: str, parent: QWidget | None = None):
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
        self.l0_exec_button.clicked[None].connect(  # type: ignore
            self.execute_command)
        self.l0_layout.addWidget(self.l0_exec_button)

        self.l0_next_button = QPushButton("End month")
        self.l0_next_button.clicked[None].connect(  # type: ignore
            self.next_month)
        self.l0_layout.addWidget(self.l0_next_button)

        self.l0_save_button = QPushButton("Save game")
        self.l0_save_button.clicked[None].connect(  # type: ignore
            self.save_game)
        self.l0_layout.addWidget(self.l0_save_button)

        self.l0_del_button = QPushButton("Delete save")
        self.l0_del_button.clicked[None].connect(  # type: ignore
            self.delete_save)
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
        self.l3_menus_buttons[0].clicked[None].connect(  # type: ignore
            lambda: self.set_scene(Scene_Classes(self))
        )
        self.l3_menus_buttons[1].clicked[None].connect(  # type: ignore
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

        self.scene_set: AbstractScene | None = None
        self.update()

        self.setMinimumSize(900, 600)

    def set_scene(self, new_scene: AbstractScene) -> None:
        if self.scene_set:
            self.layout_.removeWidget(self.scene_set)
            self.scene_set.deleteLater()
        self.scene_set = new_scene
        self.layout_.insertWidget(4, new_scene)

    def update(self) -> None:
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

    @crashing_slot
    def execute_command(self):
        real_stdout = sys.stdout
        real_stdin = sys.stdin
        try:
            dialog = Execute_Dialog(self)
            dialog.exec()
        finally:
            sys.stdout = real_stdout
            sys.stdin = real_stdin

    @crashing_slot
    def next_month(self):
        try:
            self.interface.next_month()
        except EveryoneDeadError as e:
            QMessageBox.information(self, "Game Over", "GAME OVER\n"
                                    "There is not a living person left in your"
                                    " country.")
            raise ShutDownCommand from e
        except RebellionError as e:
            QMessageBox.information(self, "Game Over", "GAME OVER\n"
                                    f"{str(e).title()} have rebelled.")
            raise ShutDownCommand from e
        self.update()

    @crashing_slot
    def save_game(self):
        save_dialog = Save_Dialog(self, False)
        save_dialog.exec()

    @crashing_slot
    def delete_save(self):
        save_dialog = Save_Dialog(self, True)
        save_dialog.exec()

    @crashing_slot
    def transfer(self, class_name: Class_Name):
        transfer_dialog = Transfer_Dialog(class_name, self)
        transfer_dialog.exec()

    @crashing_slot
    def promote(self, class_name: Class_Name):
        lower_class = self.interface.state.classes[class_name].lower_class

        cost = (INBUILT_RESOURCES[class_name] -
                INBUILT_RESOURCES[lower_class.class_name])
        res_maxes = self.interface.state.government.real_resources / cost
        res_max = floor(min(res_maxes.values()))

        if res_max <= 0:
            QMessageBox.warning(self, "Warning", "The government does not have"
                                " enough resources for this operation")
        elif floor(lower_class.population) <= 0:
            QMessageBox.warning(self, "Warning", "The class to promote from is"
                                " empty")
        else:
            promote_dialog = Number_Select_Dialog(
                0, min(floor(lower_class.population), res_max), "Promote",
                f"How many {lower_class.class_name} do you want to"
                f" promote to {class_name}?"
            )
            number = promote_dialog.exec()

            self.interface.force_promotion(class_name, number)
            self.update()
