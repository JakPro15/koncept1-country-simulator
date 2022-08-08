from io import StringIO
import sys
from PySide6.QtWidgets import (
    QDialog, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit
)
from .auxiliaries import crashing_slot
from ..cli import cli


class Execute_Dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.command_line = QLineEdit()
        self.command_line.setPlaceholderText("Enter a command...")

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked[None].connect(self.confirmed)

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
    def confirmed(self):
        output_stream = StringIO()
        input_stream = StringIO("1")
        sys.stdout = output_stream
        sys.stdin = input_stream
        command = self.command_line.text().strip()
        cli.execute(command, self.parent().interface)
        self.output_label.setText(output_stream.getvalue())
