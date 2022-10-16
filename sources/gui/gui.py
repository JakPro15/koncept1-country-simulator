import traceback

from PySide6.QtWidgets import QApplication

from ..auxiliaries import globals
from .command_window import Command_Window


def graphical_user_interface(dirname: str):
    app = QApplication([])

    try:
        window = Command_Window(dirname)
        globals.warning_out = globals.WarningOutput(window)
    except BaseException:
        if globals.debug:
            traceback.print_exc()
        return

    window.show()
    app.exec()
