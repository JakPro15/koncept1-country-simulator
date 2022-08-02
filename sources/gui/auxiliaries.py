from PySide6.QtWidgets import QApplication
import traceback


def crashing_slot(inner):
    def crashing_inner(*args, **kwargs):
        try:
            inner(*args, **kwargs)
        except BaseException:
            if __debug__:
                traceback.print_exc()
            QApplication.exit()
    return crashing_inner
