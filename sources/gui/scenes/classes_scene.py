from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton

from ...auxiliaries.enums import CLASS_NAME_STR, RESOURCE_STR, Class_Name
from ...gui.resources_display import Resources_Display
from .abstract_scene import Abstract_Scene
from ..auxiliaries import crashing_slot

if TYPE_CHECKING:
    from ..command_window import Command_Window


class Scene_Classes(Abstract_Scene):
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

            @crashing_slot
            def this_transfer(_: bool = False, cn: Class_Name = class_name
                              ) -> None:
                self._parent.transfer(cn)

            self.transfer_buttons[i].clicked[None].connect(  # type: ignore
                this_transfer
            )
            self.main_layout.addWidget(self.transfer_buttons[i], i + 1, 7)

        self.promote_buttons: list[QPushButton] = []
        for i, class_name in enumerate(list(Class_Name)[:3]):
            self.promote_buttons.append(QPushButton("Promote"))

            @crashing_slot
            def this_promote(_: bool = False, cn: Class_Name = class_name
                             ) -> None:
                self._parent.promote(cn)

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
