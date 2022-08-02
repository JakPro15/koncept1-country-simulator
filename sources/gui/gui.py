import traceback
from PySide6.QtWidgets import QApplication
from .command_window import Command_Window


def graphical_user_interface(dirname):
    app = QApplication([])

    try:
        window = Command_Window(dirname)
    except BaseException:
        if __debug__:
            traceback.print_exc()
        return

    window.show()
    app.exec()
