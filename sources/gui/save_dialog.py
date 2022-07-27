from PySide6.QtWidgets import (
    QDialog, QLineEdit, QVBoxLayout, QPushButton, QMessageBox
)
from PySide6.QtGui import QRegularExpressionValidator
import re
from os import mkdir
from .confirm_dialog import Confirm_Dialog
from ..abstract_interface.interface import SaveAccessError


class Save_Dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dirname_input = QLineEdit()
        self.dirname_input.setPlaceholderText("Enter the name of the save")
        validator = QRegularExpressionValidator(r"^\w+$")
        self.dirname_input.setValidator(validator)

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.confirmed)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.dirname_input)
        self.layout.addWidget(self.confirm_button)

        self.setLayout(self.layout)

    def confirmed(self):
        if not re.search(r"^\w+$", self.dirname_input.text()):
            QMessageBox.warning(self, "Warning", "Invalid save name")
            return
        if self.dirname_input.text() == "starting":
            QMessageBox.warning(self, "Warning", 'Please choose a save name'
                                ' different from "starting"')
            return

        try:
            mkdir(f"saves/{self.dirname_input.text()}")
        except FileExistsError:
            confirm_dialog = Confirm_Dialog("This save already exists. Do you"
                                            " want to overwrite?")
            ans = confirm_dialog.exec()
            if not ans:
                return

        try:
            self.parent().interface.save_data(f"{self.dirname_input.text()}")
        except SaveAccessError:
            QMessageBox.warning(self, "Warning",
                                "Failed to open the save file.")
            return

        QMessageBox.information(self, "Success", "Game saved")
        self.close()
