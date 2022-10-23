import sys
from typing import Protocol

from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtCore import QTimer, QObject
from ..gui.auxiliaries import crashing_slot


class WarningOutput(Protocol):
    def write(self, __s: str, /) -> int: ...


class CLIWarningOutput:
    def write(self, __s: str, /) -> int:
        return sys.stdout.write(__s + '\n')


class GUIWarningOutput(QObject):
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
        return len(__s) + 1

    @crashing_slot
    def flush(self) -> None:
        QMessageBox.warning(self._parent, "Warning", self.buffer)
        self.buffer = ""
        self.buffering = False


warning_out: WarningOutput = CLIWarningOutput()
debug = False
