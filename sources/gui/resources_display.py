from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QLayout

from ..auxiliaries.enums import RESOURCE_STR
from ..auxiliaries.resources import Resources


class Resources_Display:
    def __init__(self, resources: Resources | None = None) -> None:
        self.labels = [QLabel(f"{res}:") for res in RESOURCE_STR]

        if resources:
            self.set_resources(resources)

    def set_resources(self, resources: Resources) -> None:
        for label, res, amount in zip(self.labels, resources.keys(),
                                      resources.values()):
            label.setText(f"{res.name.title()}: {amount}")

    def add_to_layout(self, layout: QLayout) -> None:
        for label in self.labels:
            layout.addWidget(label)

    def add_to_grid_layout(self, layout: QGridLayout, row: int,
                           first_column: int) -> None:
        for i, label in enumerate(self.labels):
            layout.addWidget(label, row, first_column + i)

    def setAlignment(self, alignment: Qt.Alignment) -> None:
        for label in self.labels:
            label.setAlignment(alignment)
