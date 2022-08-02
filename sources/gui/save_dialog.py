from PySide6.QtWidgets import (
    QDialog, QLineEdit, QVBoxLayout, QPushButton, QMessageBox
)
from PySide6.QtGui import QRegularExpressionValidator
import re
from os import mkdir
from os.path import isdir
from shutil import rmtree
from .confirm_dialog import Confirm_Dialog
from ..abstract_interface.interface import SaveAccessError


class Save_Dialog(QDialog):
    def __init__(self, delete=False, parent=None):
        super().__init__(parent)
        self.delete = delete

        self.dirname_input = QLineEdit()
        self.dirname_input.setPlaceholderText("Enter the name of the save")
        if not self.delete:
            self.dirname_input.setText(self.parent().interface.save_name)
        self.dirname_input.setValidator(QRegularExpressionValidator(r"^\w+$"))

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked[None].connect(self.confirmed)

        self.layout_ = QVBoxLayout()
        self.layout_.addWidget(self.dirname_input)
        self.layout_.addWidget(self.confirm_button)

        self.setLayout(self.layout_)
        if self.delete:
            self.setWindowTitle("Delete")
        else:
            self.setWindowTitle("Save")

    def confirmed(self):
        if not re.search(r"^\w+$", self.dirname_input.text()):
            QMessageBox.warning(self, "Warning", "Invalid save name")
            return
        if self.dirname_input.text() == "starting":
            if not self.delete:
                QMessageBox.warning(self, "Warning", 'Please choose a save'
                                    ' name different from "starting"')
            else:
                QMessageBox.warning(self, "Warning", "Deleting this save is"
                                    " prohibited.")
            return

        if not self.delete:
            try:
                mkdir(f"saves/{self.dirname_input.text()}")
            except FileExistsError:
                confirm_dialog = Confirm_Dialog("This save already exists. Do"
                                                " you want to overwrite?")
                ans = confirm_dialog.exec()
                if not ans:
                    return

            try:
                self.parent().interface.save_data(
                    f"{self.dirname_input.text()}"
                )
            except SaveAccessError:
                QMessageBox.warning(self, "Warning",
                                    "Failed to open the save file.")
                return

            QMessageBox.information(self, "Success", "Game saved in"
                                    f" saves/{self.dirname_input.text()}")
        else:
            if not isdir(f"saves/{self.dirname_input.text()}"):
                QMessageBox.warning(self, "Warning",
                                    "This save does not exist.")
                return

            confirm_dialog = Confirm_Dialog("Are you sure you want to delete"
                                            " this save?")
            ans = confirm_dialog.exec()
            if not ans:
                return

            rmtree(f"saves/{self.dirname_input.text()}")
            QMessageBox.information(self, "Success", "Removed the save"
                                    f" saves/{self.dirname_input.text()}")
        self.close()
