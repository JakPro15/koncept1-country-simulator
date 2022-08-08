from PySide6.QtWidgets import (
    QPushButton, QHBoxLayout, QLineEdit,
    QVBoxLayout, QLabel, QMessageBox, QDialog, QSlider
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QRegularExpressionValidator
from .auxiliaries import crashing_slot


class Number_Select_Dialog(QDialog):
    def __init__(self, min: int, max: int, window_title: str, header: str,
                 parent=None):
        super().__init__(parent)

        self.header = QLabel(header)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(min)
        self.slider.setMaximum(max)
        self.slider.setMinimumWidth(300)
        self.slider.valueChanged[int].connect(self.slider_changed)

        self.right_edit = QLineEdit()
        self.right_edit.setValidator(QRegularExpressionValidator(r"^\d*$"))
        self.right_edit.setFixedWidth(50)
        self.right_edit.setText(str(min))
        self.right_edit.textEdited[str].connect(self.edit_changed)

        self.input_layout = QHBoxLayout()
        self.input_layout.addWidget(self.slider)
        self.input_layout.addWidget(self.right_edit)

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked[None].connect(self.confirmed)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.header)
        self.main_layout.addLayout(self.input_layout)
        self.main_layout.addWidget(self.confirm_button)

        self.setLayout(self.main_layout)
        self.setWindowTitle(window_title)

    @crashing_slot
    def slider_changed(self, slider_value: int):
        self.right_edit.setText(str(slider_value))

    @crashing_slot
    def edit_changed(self, text):
        if text:
            if int(text) > self.slider.maximum():
                QMessageBox.warning(self, "Warning", "Invalid value")
                self.right_edit.setText(str(self.slider.maximum()))
            elif int(text) < self.slider.minimum():
                QMessageBox.warning(self, "Warning", "Invalid value")
                self.right_edit.setText(str(self.slider.minimum()))
            self.slider.setValue(int(self.right_edit.text()))

    @crashing_slot
    def confirmed(self):
        self.accept()

    def exec(self):
        super().exec()
        return self.slider.value()
