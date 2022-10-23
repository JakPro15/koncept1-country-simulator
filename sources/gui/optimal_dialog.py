from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QSizePolicy, QVBoxLayout, QWidget)

from ..abstract_interface.interface import Interface
from ..auxiliaries.enums import Resource
from .auxiliaries import crashing_slot

if TYPE_CHECKING:
    from .command_window import Command_Window


class LabeledLineEdit(QWidget):
    def __init__(self, res: Resource, value: int | None = None,
                 parent: QWidget | None = None):
        super().__init__(parent)
        self.resource = res

        self.label = QLabel(res.name.title(), self)
        self.line_edit = QLineEdit(str(value), self)
        self.line_edit.setValidator(QRegularExpressionValidator(r"^\d*$"))
        self.line_edit.setSizePolicy(QSizePolicy.Ignored,
                                     QSizePolicy.Preferred)
        self.line_edit.setMinimumWidth(40)

        self.layout_ = QHBoxLayout()
        self.layout_.addWidget(self.label)
        self.layout_.addWidget(self.line_edit)
        self.setLayout(self.layout_)

    @property
    def value(self) -> int:
        return int(self.line_edit.text())


class Optimal_Dialog(QDialog):
    def __init__(self, parent: Command_Window):
        super().__init__(parent)
        self._parent = parent
        self.interface: Interface = self._parent.interface

        self.header = QLabel(
            "Set the government's optimal resources"
        )

        self.resource_edits = [
            LabeledLineEdit(
                res,
                int(self.interface.state.government.optimal_resources[res]),
                self
            )
            for res in Resource
        ]
        self.resources_layout = QHBoxLayout()
        for edit in self.resource_edits:
            self.resources_layout.addWidget(edit)

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked[None].connect(  # type: ignore
            self.confirmed
        )

        self.layout_ = QVBoxLayout()
        self.layout_.addWidget(self.header)
        self.layout_.addLayout(self.resources_layout)
        self.layout_.addWidget(self.confirm_button)

        self.setLayout(self.layout_)
        self.setMinimumWidth(300)
        self.setWindowTitle("Optimal")

    @crashing_slot
    def confirmed(self) -> None:
        for edit in self.resource_edits:
            self.interface.set_govt_optimal(
                edit.resource, edit.value
            )
        self._parent.update()
        self.accept()
