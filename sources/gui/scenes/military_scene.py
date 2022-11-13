from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton

from ...auxiliaries.enums import CLASS_NAME_STR, Class_Name
from .abstract_scene import Abstract_Scene
from ..auxiliaries import crashing_slot, ValueLabel
from ...auxiliaries.constants import Soldier

if TYPE_CHECKING:
    from ..command_window import Command_Window


class Scene_Military(Abstract_Scene):
    def __init__(self, parent: Command_Window) -> None:
        super().__init__(parent)
        self._parent = parent
        self.top_labels = [
            QLabel(column_title, self)
            for column_title in ["Population", "Happiness"]
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

        self.population_labels: list[QLabel] = []
        for i in range(len(self.left_labels)):
            self.population_labels.append(QLabel())
            self.population_labels[i].setAlignment(Qt.AlignCenter)
            self.main_layout.addWidget(self.population_labels[i], i + 1, 1)

        self.happiness_labels: list[QLabel] = []
        for i in range(len(self.left_labels)):
            self.happiness_labels.append(QLabel())
            self.happiness_labels[i].setAlignment(Qt.AlignCenter)
            self.main_layout.addWidget(self.happiness_labels[i], i + 1, 2)

        self.recruit_buttons: list[QPushButton] = []

        for i, class_name in enumerate(Class_Name):
            self.recruit_buttons.append(QPushButton("Recruit"))

            @crashing_slot
            def this_recruit(_: bool = False, cn: Class_Name = class_name
                             ) -> None:
                self._parent.recruit(cn)

            self.recruit_buttons[i].clicked[None].connect(  # type: ignore
                this_recruit
            )
            self.main_layout.addWidget(self.recruit_buttons[i], i + 1, 3)

        for i in range(8):
            self.main_layout.setColumnStretch(i, 1)

        self.soldiers_label = QLabel("Government soldiers:")
        self.main_layout.addWidget(self.soldiers_label, 0, 5)

        self.soldier_labels: list[ValueLabel] = []
        for i, soldier in enumerate(Soldier):
            self.soldier_labels.append(ValueLabel(f"{soldier.name.title()}",
                                                  rounding=0))
            self.main_layout.addWidget(self.soldier_labels[i], i + 1, 5)

        self.revolt_label = QLabel()
        self.main_layout.addWidget(self.revolt_label, 3, 5, 1, 2)

        self.crime_label = QLabel("Crime:")
        self.brigands_label = QLabel()
        self.brigands_strength_label = QLabel()

        self.main_layout.addWidget(self.crime_label, 0, 6)
        self.main_layout.addWidget(self.brigands_label, 1, 6)
        self.main_layout.addWidget(self.brigands_strength_label, 2, 6)

        self.fight_label = QLabel("Combat options:")
        self.main_layout.addWidget(self.fight_label, 6, 1)

        self.fight_buttons: list[QPushButton] = []
        self.fight_buttons.append(QPushButton("Attack brigands"))
        self.fight_buttons.append(QPushButton("Attack to plunder resources"))
        self.fight_buttons.append(QPushButton("Attack to conquer land"))

        for i, target in enumerate(["crime", "plunder", "conquest"]):
            @crashing_slot
            def this_fight(_: bool = False, tgt: str = target) -> None:
                self._parent.fight(tgt)

            self.fight_buttons[i].clicked[None].connect(  # type: ignore
                this_fight
            )

        for i, button in enumerate(self.fight_buttons):
            self.main_layout.addWidget(button, 7, 2 * i + 1, 1, 2)

        self.fight_desc_label = QLabel(
            "You can fight only once a round, and you need at least one"
            " soldier."
        )
        self.main_layout.addWidget(self.fight_desc_label, 8, 1, 1, 4)

        self.setLayout(self.main_layout)
        self.update()

    def update(self) -> None:
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

        for i in range(len(Class_Name)):
            class_name = CLASS_NAME_STR[i]
            self.population_labels[i].setText(f"{pops[class_name]}")
            self.happiness_labels[i].setText(f"{haps[class_name]}")

        for i, button in enumerate(self.recruit_buttons):
            button.setEnabled(
                self._parent.interface.state.classes[
                    Class_Name(i)].population > 0
            )

        for label, soldier in zip(self.soldier_labels, Soldier):
            label.value = \
                self._parent.interface.state.government.soldiers[soldier]

        if self._parent.interface.state.government.soldier_revolt:
            self.revolt_label.setText("The soldiers are revolting!")
        else:
            self.revolt_label.setText("The soldiers are not revolting.")

        brigands, strength = self._parent.interface.get_brigands()
        if isinstance(brigands, tuple) and isinstance(strength, tuple):
            self.brigands_label.setText(
                f"Brigands: {brigands[0]}-{brigands[1]}"
            )
            self.brigands_strength_label.setText(
                f"Brigand strength: {strength[0]}-{strength[1]}"
            )
        else:
            self.brigands_label.setText(f"Brigands: {brigands}")
            self.brigands_strength_label.setText(
                f"Brigand strength: {strength}"
            )

        for button in self.fight_buttons:
            if self._parent.interface.state.government.soldiers.number < 1 or \
                 self._parent.interface.fought:
                button.setEnabled(False)
            else:
                button.setEnabled(True)
