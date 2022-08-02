from PySide6.QtWidgets import (
    QDialog, QSlider, QVBoxLayout, QPushButton, QLineEdit, QHBoxLayout, QLabel,
    QWidget, QMessageBox
)
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import Qt
from ..auxiliaries.constants import CLASS_NAME_TO_INDEX, RESOURCES
from math import floor
from .auxiliaries import crashing_slot


class Transfer_Row(QWidget):
    def __init__(self, class_name: str, res_name: str,
                 parent: "Transfer_Dialog"):
        super().__init__(parent)
        self.resource = res_name
        self.old_govt = floor(
            self.parent().parent().interface.state.government.real_resources[
                res_name
            ])
        self.old_class = floor(self.parent().parent().interface.state.classes[
                CLASS_NAME_TO_INDEX[class_name]
            ].real_resources[res_name])

        self.label = QLabel(res_name.title())
        self.label.setFixedWidth(35)
        self.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimumWidth(300)
        self.slider.setMinimum(-self.old_govt)
        self.slider.setMaximum(self.old_class)
        self.slider.valueChanged[int].connect(self.slider_changed)

        self.left_edit = QLineEdit()
        self.left_edit.setValidator(QRegularExpressionValidator(r"^\d*$"))
        self.left_edit.setFixedWidth(50)
        self.left_edit.setText(str(self.old_class))
        self.left_edit.textEdited[str].connect(self.left_edit_changed)

        self.right_edit = QLineEdit()
        self.right_edit.setValidator(QRegularExpressionValidator(r"^\d*$"))
        self.right_edit.setFixedWidth(50)
        self.right_edit.setText(str(self.old_govt))
        self.right_edit.textEdited[str].connect(self.right_edit_changed)

        self.layout_ = QHBoxLayout()
        self.layout_.addWidget(self.label)
        self.layout_.addWidget(self.left_edit)
        self.layout_.addWidget(self.slider)
        self.layout_.addWidget(self.right_edit)

        self.setLayout(self.layout_)

    @crashing_slot
    def slider_changed(self, sliderValue: int):
        print("sloider shanged")
        self.left_edit.setText(str(self.old_class - sliderValue))
        self.right_edit.setText(str(self.old_govt + sliderValue))

    @crashing_slot
    def left_edit_changed(self, text):
        print("left yedit shanged")
        if text:
            max = self.slider.maximum() - self.slider.minimum()
            if int(text) > max:
                QMessageBox.warning(self, "Warning", "Invalid value")
                self.left_edit.setText(str(max))
            self.slider.setValue(self.old_class - int(self.left_edit.text()))

    @crashing_slot
    def right_edit_changed(self, text):
        print("roight yedit shanged")
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
    def __init__(self, class_name: str, parent):
        super().__init__(parent)
        self.class_name = class_name

        self.header = QLabel(f"Transferring resources to/from {class_name}")

        self.rows = [Transfer_Row(class_name, res, self) for res in RESOURCES]

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked[None].connect(self.confirmed)

        self.layout_ = QVBoxLayout()
        self.layout_.addWidget(self.header)
        for row in self.rows:
            self.layout_.addWidget(row)
        self.layout_.addWidget(self.confirm_button)

        self.setLayout(self.layout_)
        self.setMinimumWidth(300)
        self.setWindowTitle("Transfer")

    @crashing_slot
    def confirmed(self):
        for row in self.rows:
            if row.transferred != 0:
                self.parent().interface.transfer_resources(
                    self.class_name, row.resource, row.transferred
                )
        self.parent().update()
        self.accept()
