from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from ..command_window import Command_Window


class Abstract_Scene(QWidget):
    @abstractmethod
    def __init__(self, parent: Command_Window) -> None:
        super().__init__(parent)

    @abstractmethod
    def update(self) -> None:
        ...
