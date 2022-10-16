import sys

from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtCore import QTimer, QObject
from ..gui.auxiliaries import crashing_slot

warning_out = sys.stdout
debug = False


class WarningOutput(QObject):
    def __init__(self, parent: QWidget, buffering_time_ms: int = 100) -> None:
        super().__init__(parent)
        self._parent = parent
        self.max_buffering_time = buffering_time_ms
        self.buffer = ""
        self.buffering: bool = False

    def write(self, __s: str, /) -> int:
        if not self.buffering:
            self.buffering = True
            QTimer.singleShot(  # type: ignore
                self.max_buffering_time, self.flush
            )
        self.buffer += f"\n{__s}"
        return len(__s)

    @crashing_slot
    def flush(self) -> None:
        QMessageBox.warning(self._parent, "Warning", self.buffer)
        self.buffer = ""
        self.buffering = False
