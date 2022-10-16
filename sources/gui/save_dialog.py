from __future__ import annotations

import re
from os import mkdir
from os.path import isdir
from shutil import rmtree
from typing import TYPE_CHECKING

from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (QDialog, QLineEdit, QMessageBox, QPushButton,
                               QVBoxLayout)

from ..abstract_interface.interface import SaveAccessError
from .auxiliaries import crashing_slot
from .confirm_dialog import Confirm_Dialog

if TYPE_CHECKING:
    from .command_window import Command_Window


class Save_Dialog(QDialog):
    def __init__(self, parent: Command_Window, delete: bool = False
                 ) -> None:
        super().__init__(parent)
        self._parent = parent
        self.delete = delete

        self.dirname_input = QLineEdit()
        self.dirname_input.setPlaceholderText("Enter the name of the save")
        if not self.delete and self._parent.interface.save_name:
            self.dirname_input.setText(self._parent.interface.save_name)
        self.dirname_input.setValidator(QRegularExpressionValidator(r"^\w+$"))

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked[None].connect(  # type: ignore
            self.confirmed
        )

        self.layout_ = QVBoxLayout()
        self.layout_.addWidget(self.dirname_input)
        self.layout_.addWidget(self.confirm_button)

        self.setLayout(self.layout_)
        if self.delete:
            self.setWindowTitle("Delete")
        else:
            self.setWindowTitle("Save")

    @crashing_slot
    def confirmed(self) -> None:
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
                self._parent.interface.save_data(
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
