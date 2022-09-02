import sys
from io import StringIO
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QVBoxLayout)

from ..cli import cli
from .auxiliaries import crashing_slot

if TYPE_CHECKING:
    from .command_window import Command_Window


class Execute_Dialog(QDialog):
    def __init__(self, parent: Command_Window):
        super().__init__(parent)
        self._parent = parent

        self.command_line = QLineEdit()
        self.command_line.setPlaceholderText("Enter a command...")

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked[None].connect(  # type: ignore
            self.confirmed
        )

        self.input_layout = QHBoxLayout()
        self.input_layout.addWidget(self.command_line)
        self.input_layout.addWidget(self.confirm_button)

        self.output_label = QLabel("Command line output will be shown here")

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.input_layout)
        self.main_layout.addWidget(self.output_label)
        self.main_layout.addStretch()

        self.setLayout(self.main_layout)
        self.setWindowTitle("Command Line Interface Emulator")
        self.setMinimumSize(600, 400)

    @crashing_slot
    def confirmed(self) -> None:
        output_stream = StringIO()
        input_stream = StringIO("1")
        sys.stdout = output_stream
        sys.stdin = input_stream
        command = self.command_line.text().strip()
        cli.execute(command, self._parent.interface)
        self.output_label.setText(output_stream.getvalue())
