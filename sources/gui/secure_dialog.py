from __future__ import annotations

from math import floor
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit,
                               QMessageBox, QPushButton, QSlider, QVBoxLayout,
                               QWidget)

from ..abstract_interface.interface import Interface
from ..auxiliaries.enums import Resource
from .auxiliaries import crashing_slot

if TYPE_CHECKING:
    from .command_window import Command_Window


class Secure_Row(QWidget):
    value_changed = Signal()

    def __init__(self, res: Resource, parent: Secure_Dialog) -> None:
        super().__init__(parent)
        self._parent = parent
        self.resource = res
        self.old_free = floor(
            self._parent.interface.state.government.resources[res])
        self.old_secure = floor(
            self._parent.interface.state.government.secure_resources[res])

        self.label = QLabel(res.name.title())
        self.label.setFixedWidth(35)
        right_center_align: Qt.Alignment = Qt.AlignRight | Qt.AlignVCenter
        self.label.setAlignment(right_center_align)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimumWidth(300)
        self.slider.setMinimum(-self.old_free)
        self.slider.setMaximum(self.old_secure)
        self.slider.valueChanged[int].connect(  # type: ignore
            self.slider_changed
        )

        self.left_edit = QLineEdit()
        self.left_edit.setValidator(QRegularExpressionValidator(r"^\d*$"))
        self.left_edit.setFixedWidth(50)
        self.left_edit.setText(str(self.old_secure))
        self.left_edit.textEdited[str].connect(  # type: ignore
            self.left_edit_changed
        )

        self.right_edit = QLineEdit()
        self.right_edit.setValidator(QRegularExpressionValidator(r"^\d*$"))
        self.right_edit.setFixedWidth(50)
        self.right_edit.setText(str(self.old_free))
        self.right_edit.textEdited[str].connect(  # type: ignore
            self.right_edit_changed
        )

        self.layout_ = QHBoxLayout()
        self.layout_.addWidget(self.label)
        self.layout_.addWidget(self.left_edit)
        self.layout_.addWidget(self.slider)
        self.layout_.addWidget(self.right_edit)

        self.setLayout(self.layout_)

    @crashing_slot
    def slider_changed(self, slider_value: int) -> None:
        self.left_edit.setText(str(self.old_secure - slider_value))
        self.right_edit.setText(str(self.old_free + slider_value))
        self.value_changed.emit()

    @crashing_slot
    def left_edit_changed(self, text: str) -> None:
        if text:
            max = self.slider.maximum() - self.slider.minimum()
            if int(text) > max:
                QMessageBox.warning(self, "Warning", "Invalid value")
                self.left_edit.setText(str(max))
            self.slider.setValue(self.old_secure - int(self.left_edit.text()))

    @crashing_slot
    def right_edit_changed(self, text: str) -> None:
        if text:
            max = self.slider.maximum() - self.slider.minimum()
            if int(text) > max:
                QMessageBox.warning(self, "Warning", "Invalid value")
                self.right_edit.setText(str(max))
            self.slider.setValue(int(self.right_edit.text()) - self.old_free)

    @property
    def transferred(self):
        return -self.slider.value()


class Secure_Dialog(QDialog):
    def __init__(self, parent: Command_Window):
        super().__init__(parent)
        self._parent = parent
        self.interface: Interface = self._parent.interface

        self.header = QLabel(
            "Set amount of the government's secure resources"
        )

        self.below_header_layout = QHBoxLayout()
        self.free_label = QLabel("Tradeable resources")
        self.secure_label = QLabel("Secure resources")

        self.below_header_layout.addWidget(self.secure_label)
        self.below_header_layout.addStretch()
        self.below_header_layout.addWidget(self.free_label)

        self.rows = [Secure_Row(res, self) for res in Resource]

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked[None].connect(  # type: ignore
            self.confirmed
        )

        self.layout_ = QVBoxLayout()
        self.layout_.addWidget(self.header)
        self.layout_.addLayout(self.below_header_layout)
        for row in self.rows:
            self.layout_.addWidget(row)
        self.layout_.addWidget(self.confirm_button)

        self.setLayout(self.layout_)
        self.setMinimumWidth(300)
        self.setWindowTitle("Secure")

    @crashing_slot
    def confirmed(self) -> None:
        for row in self.rows:
            self.interface.secure_resources(
                row.resource, row.transferred
            )
        self._parent.update()
        self.accept()
