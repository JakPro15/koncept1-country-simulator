from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton

from ...auxiliaries.constants import GOVT_LEFT_LABELS
from ...auxiliaries.enums import RESOURCE_STR
from ...gui.resources_display import Resources_Display
from .abstract_scene import Abstract_Scene

if TYPE_CHECKING:
    from ..command_window import Command_Window


class Scene_Govt(Abstract_Scene):
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

        self.secure_button = QPushButton("Set secure resources", self)
        self.secure_button.clicked[None].connect(  # type: ignore
            self._parent.secure
        )
        self.layout_.addWidget(self.secure_button, 4, 5)

        self.optimal_button = QPushButton("Set optimal resources", self)
        self.optimal_button.clicked[None].connect(  # type: ignore
            self._parent.optimal
        )
        self.layout_.addWidget(self.optimal_button, 4, 6)

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
