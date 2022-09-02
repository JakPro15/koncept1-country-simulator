from __future__ import annotations

from math import floor
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit,
                               QMessageBox, QPushButton, QSlider, QVBoxLayout,
                               QWidget)

from ..abstract_interface.interface import Interface
from ..auxiliaries.enums import Class_Name, Resource
from ..auxiliaries.resources import Resources
from ..state.social_classes.class_file import Class
from .auxiliaries import Value_Label, crashing_slot

if TYPE_CHECKING:
    from .command_window import Command_Window


class Transfer_Row(QWidget):
    value_changed = Signal()

    def __init__(self, class_name: Class_Name, res: Resource,
                 parent: Transfer_Dialog) -> None:
        super().__init__(parent)
        self._parent = parent
        self.resource = res
        self.old_govt = floor(
            self._parent.interface.state.government.real_resources[res])
        self.old_class = floor(self._parent.interface.state.classes[
            class_name].real_resources[res])

        self.label = QLabel(res.name.title())
        self.label.setFixedWidth(35)
        right_center_align: Qt.Alignment = Qt.AlignRight | Qt.AlignVCenter
        self.label.setAlignment(right_center_align)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimumWidth(300)
        self.slider.setMinimum(-self.old_govt)
        self.slider.setMaximum(self.old_class)
        self.slider.valueChanged[int].connect(  # type: ignore
            self.slider_changed
        )

        self.left_edit = QLineEdit()
        self.left_edit.setValidator(QRegularExpressionValidator(r"^\d*$"))
        self.left_edit.setFixedWidth(50)
        self.left_edit.setText(str(self.old_class))
        self.left_edit.textEdited[str].connect(  # type: ignore
            self.left_edit_changed
        )

        self.right_edit = QLineEdit()
        self.right_edit.setValidator(QRegularExpressionValidator(r"^\d*$"))
        self.right_edit.setFixedWidth(50)
        self.right_edit.setText(str(self.old_govt))
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
        self.left_edit.setText(str(self.old_class - slider_value))
        self.right_edit.setText(str(self.old_govt + slider_value))
        self.value_changed.emit()

    @crashing_slot
    def left_edit_changed(self, text: str) -> None:
        if text:
            max = self.slider.maximum() - self.slider.minimum()
            if int(text) > max:
                QMessageBox.warning(self, "Warning", "Invalid value")
                self.left_edit.setText(str(max))
            self.slider.setValue(self.old_class - int(self.left_edit.text()))

    @crashing_slot
    def right_edit_changed(self, text: str) -> None:
        if text:
            max = self.slider.maximum() - self.slider.minimum()
            if int(text) > max:
                QMessageBox.warning(self, "Warning", "Invalid value")
                self.right_edit.setText(str(max))
            self.slider.setValue(int(self.right_edit.text()) - self.old_govt)

    @property
    def transferred(self):
        return -self.slider.value()


class Transfer_Dialog(QDialog):
    def __init__(self, class_name: Class_Name, parent: Command_Window):
        super().__init__(parent)
        self._parent = parent
        self.class_name = class_name
        self.interface: Interface = self._parent.interface

        self.header = QLabel(f"Transferring resources to/from {class_name}")

        self.rows = [Transfer_Row(class_name, res, self) for res in Resource]
        for row in self.rows:
            row.value_changed[None].connect(self.changed)  # type: ignore

        self.estimated_happiness = Value_Label(
            "Estimated happiness after transfer"
        )

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked[None].connect(  # type: ignore
            self.confirmed
        )

        self.layout_ = QVBoxLayout()
        self.layout_.addWidget(self.header)
        for row in self.rows:
            self.layout_.addWidget(row)
        self.layout_.addWidget(self.confirm_button)
        self.layout_.addWidget(self.estimated_happiness)

        self.setLayout(self.layout_)
        self.setMinimumWidth(300)
        self.setWindowTitle("Transfer")

    @crashing_slot
    def changed(self) -> None:
        social_class = self.interface.state.classes[self.class_name]
        seized = Resources({
            res: -row.transferred for res, row, in zip(Resource, self.rows)
        })
        seized_money = seized.worth(self.interface.state.prices)
        happiness_change = Class.resources_seized_happiness(
            seized_money / social_class.population
        )
        self.estimated_happiness.value = \
            social_class.happiness + happiness_change

    @crashing_slot
    def confirmed(self) -> None:
        for row in self.rows:
            self.interface.transfer_resources(
                self.class_name, row.resource, row.transferred,
                demote=(row.resource == Resource.land)
            )
        self._parent.update()
        self.accept()
