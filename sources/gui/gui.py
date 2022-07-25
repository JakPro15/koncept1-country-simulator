from PySide6.QtWidgets import (
    QLineEdit, QPushButton, QApplication,
    QVBoxLayout, QDialog, QLabel
)
from ..abstract_interface.interface import Interface
from ..cli.cli import execute
from io import StringIO
import sys


class CommandWindow(QDialog):
    def __init__(self, parent=None):
        super(CommandWindow, self).__init__(parent)

        self.interface = Interface()
        self.interface.load_data("starting")

        # Create widgets
        self.edit = QLineEdit("Enter a command here")
        self.button = QPushButton("Execute")
        self.output = QLabel("Command output will be displayed here")
        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        layout.addWidget(self.output)
        # Set dialog layout
        self.setLayout(layout)
        # Add button signal to greetings slot
        self.button.clicked.connect(self.execute_command)

    # Greets the user
    def execute_command(self):
        results = StringIO()
        old_stdout = sys.stdout
        sys.stdout = results

        execute(self.edit.text(), self.interface)
        self.output.setText(results.getvalue())
        self.adjustSize()

        sys.stdout = old_stdout


def gui():
    # Create the Qt Application
    app = QApplication([])
    # Create and show the dialog
    window = CommandWindow()
    window.show()
    # Run the main Qt loop
    app.exec()
