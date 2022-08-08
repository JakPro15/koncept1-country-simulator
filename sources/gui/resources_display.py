from PySide6.QtWidgets import QLabel
from ..auxiliaries.constants import RESOURCES
from ..auxiliaries.arithmetic_dict import Arithmetic_Dict


class Resources_Display:
    def __init__(self, resources: Arithmetic_Dict = None):
        self.labels = [QLabel(f"{res}:") for res in RESOURCES]

        if resources:
            self.set_resources(resources)

    def set_resources(self, resources: Arithmetic_Dict):
        for label, res, amount in zip(self.labels, resources.keys(),
                                      resources.values()):
            label.setText(f"{res.title()}: {amount}")

    def add_to_layout(self, layout):
        for label in self.labels:
            layout.addWidget(label)

    def add_to_grid_layout(self, layout, row, first_column):
        for i, label in enumerate(self.labels):
            layout.addWidget(label, row, first_column + i)

    def setAlignment(self, alignment):
        for label in self.labels:
            label.setAlignment(alignment)
