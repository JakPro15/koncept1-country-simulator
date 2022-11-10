from typing import Callable, ParamSpec, TypeVar

from PySide6.QtWidgets import QApplication, QLabel, QWidget

P = ParamSpec("P")
V = TypeVar("V")


def crashing_slot(inner: Callable[P, V]) -> Callable[P, V]:
    def crashing_inner(*args: P.args, **kwargs: P.kwargs) -> V:
        try:
            return inner(*args, **kwargs)
        except BaseException:
            QApplication.exit()
            raise
    return crashing_inner


class Value_Label(QLabel):
    def __init__(self, desc: str, value: float | None = None,
                 parent: QWidget | None = None, rounding: int | None = None
                 ) -> None:
        super().__init__(parent)
        self._desc: str = desc
        self._value: float | None = value
        self.rounding: int | None = rounding
        self._update()

    @property
    def desc(self) -> str:
        return self._desc

    @desc.setter
    def desc(self, new_desc: str) -> None:
        self._desc = new_desc
        self._update()

    @property
    def value(self) -> float | None:
        return self._value

    @value.setter
    def value(self, new_value: float | None) -> None:
        self._value = new_value
        self._update()

    def _update(self) -> None:
        if self.value is None:
            self.setText(f"{self.desc}:")
        elif self.rounding is not None:
            value = round(self.value, self.rounding)
            if self.rounding <= 0:
                value = int(value)
            self.setText(f"{self.desc}: {value}")
        else:
            self.setText(f"{self.desc}: {self.value}")
