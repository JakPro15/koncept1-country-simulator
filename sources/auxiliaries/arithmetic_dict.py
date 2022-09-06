from __future__ import annotations

from math import exp, inf, isinf, isnan
from numbers import Real
from typing import Generic, Hashable, Mapping, TypeVar, overload

from pytest import approx  # type: ignore
from typing_extensions import Self

T = TypeVar("T", bound=Hashable)


class Arithmetic_Dict(Generic[T], dict[T, float]):
    def __add__(self, other: Mapping[T, float]) -> Self:
        result = self.copy()
        for key in self | other:
            result[key] = self.get(key, 0) + other.get(key, 0)
        return result

    def __IADD__(self, other: Mapping[T, float]) -> None:
        for key in self | other:
            self[key] = self.get(key, 0) + other.get(key, 0)

    def __sub__(self, other: Mapping[T, float]) -> Self:
        result = self.copy()
        for key in self | other:
            result[key] = self.get(key, 0) - other.get(key, 0)
        return result

    def __ISUB__(self, other: Mapping[T, float]) -> None:
        for key in self | other:
            self[key] = self.get(key, 0) - other.get(key, 0)

    def __mul__(self, factor: Mapping[T, float] | float) -> Self:
        result = self.copy()
        if isinstance(factor, Mapping):
            for key in self | factor:
                result[key] = self.get(key, 0) * factor.get(key, 0)
                if isnan(result[key]):
                    result[key] = 0
        elif isinstance(factor, Real):
            for key in result:
                result[key] = self.get(key, 0) * factor
                if isnan(result[key]):
                    result[key] = 0
        else:
            raise TypeError("multiplication factor must be a mapping object or"
                            " a real number")
        return result

    def __IMUL__(self, factor: Mapping[T, float] | float) -> None:
        if isinstance(factor, Mapping):
            for key in self | factor:
                self[key] = self.get(key, 0) * factor.get(key, 0)
                if isnan(self.get(key, 0)):
                    self[key] = 0
        elif isinstance(factor, Real):
            for key in self:
                self[key] = self.get(key, 0) * factor
                if isnan(self.get(key, 0)):
                    self[key] = 0
        else:
            raise TypeError("multiplication factor must be a mapping object or"
                            " a real number")

    def __truediv__(self, factor: Mapping[T, float] | float) -> Self:
        result = self.copy()
        if isinstance(factor, Mapping):
            for key in self | factor:
                try:
                    result[key] = self.get(key, 0) / factor.get(key, 0)
                except ZeroDivisionError:
                    if self.get(key, 0) == 0:
                        result[key] = 0
                    else:
                        result[key] = inf * self.get(key, 0)
        elif isinstance(factor, Real):
            for key in result:
                try:
                    result[key] = self.get(key, 0) / factor
                except ZeroDivisionError:
                    if self.get(key, 0) == 0:
                        result[key] = 0
                    else:
                        result[key] = inf * self.get(key, 0)
        else:
            raise TypeError("division factor must be a mapping object or"
                            " a real number")
        return result

    def __IDIV__(self, factor: Mapping[T, float] | float) -> None:
        if isinstance(factor, Mapping):
            for key in self | factor:
                try:
                    self[key] = self.get(key, 0) / factor.get(key, 0)
                except ZeroDivisionError:
                    if self.get(key, 0) != 0:
                        self[key] = inf * self.get(key, 0)
        elif isinstance(factor, Real):
            for key in self:
                try:
                    self[key] = self.get(key, 0) / factor
                except ZeroDivisionError:
                    if self.get(key, 0) != 0:
                        self[key] = inf * self.get(key, 0)
        else:
            raise TypeError("division factor must be a mapping object or"
                            " a real number")

    def __floordiv__(self, factor: Mapping[T, float] | float) -> Self:
        result = self.copy()
        if isinstance(factor, Mapping):
            for key in self | factor:
                try:
                    result[key] = self.get(key, 0) // factor.get(key, 0)
                except ZeroDivisionError:
                    if self.get(key, 0) == 0:
                        result[key] = 0
                    else:
                        result[key] = inf * self.get(key, 0)
        elif isinstance(factor, Real):
            for key in result:
                try:
                    result[key] = self.get(key, 0) // factor
                except ZeroDivisionError:
                    if self.get(key, 0) == 0:
                        result[key] = 0
                    else:
                        result[key] = inf * self.get(key, 0)
        else:
            raise TypeError("division factor must be a mapping object or"
                            " a real number")
        return result

    def __IFLOORDIV__(self, factor: Mapping[T, float] | float) -> None:
        if isinstance(factor, Mapping):
            for key in self | factor:
                try:
                    self[key] = self.get(key, 0) // factor.get(key, 0)
                except ZeroDivisionError:
                    if self.get(key, 0) != 0:
                        self[key] = inf * self.get(key, 0)
        elif isinstance(factor, Real):
            for key in self:
                try:
                    self[key] = self.get(key, 0) // factor
                except ZeroDivisionError:
                    if self.get(key, 0) != 0:
                        self[key] = inf * self.get(key, 0)
        else:
            raise TypeError("division factor must be a mapping object or"
                            " a real number")

    def __lt__(self, other: Mapping[T, float] | float) -> bool:
        """
        Returns True if and only if one of the elements is smaller than its
        counterpart in the other mapping object. If other is a number, returns
        True if and only if one of the elements is smaller than this number.
        """
        if isinstance(other, Mapping):
            for key in self | other:
                if self.get(key, 0) < other.get(key, 0):
                    return True
        elif isinstance(other, Real):
            for key in self:
                if self.get(key, 0) < other:
                    return True
        else:
            raise TypeError("comparison argument must be a mapping object or"
                            " a real number")
        return False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Mapping):
            return NotImplemented
        for key in self | other:
            if self.get(key, 0) != approx(other.get(key, 0)):  # type: ignore
                return False
        return True

    def copy(self) -> Self:
        """
        Returns a shallow copy of the object.
        """
        return type(self)(super().copy())

    def exp(self) -> Self:
        """
        Returns a copy of the object with each value changed by the exp
        function (e to the power of value).
        """
        return type(self)(
            {element: exp(value) for element, value in self.items()}
        )

    def int(self) -> Self:
        """
        Returns a copy of the object with each value converted to an integer.
        """
        return type(self)({
            element: int(value)
            for element, value in self.items()
        })

    def float(self) -> Self:
        """
        Returns a copy of the object with each value converted to a float.
        """
        return type(self)({
            element: float(value)
            for element, value in self.items()
        })

    @staticmethod
    def _round(number: float, ndigits: int = 0) -> float | int:
        """
        Rounds the number, converting it to a correct type (int or float).
        Ignores infinities and NaN.
        """
        if isinf(number) or isnan(number):
            return number
        elif ndigits <= 0:
            return int(round(number, ndigits))
        else:
            return float(round(number, ndigits))

    @overload
    def __round__(self, ndigits: None = None) -> int:
        ...

    @overload
    def __round__(self, ndigits: int) -> Self:
        ...

    def __round__(self, ndigits: int | None = None
                  ) -> Self | int:
        if ndigits is None:
            raise TypeError(
                "round of an arithmetic dict must provide a second argument"
            )
        result = self.copy()
        for key in result:
            result[key] = Arithmetic_Dict._round(result[key], ndigits)
        return result

    def calculate_ratios(self) -> Arithmetic_Dict[T]:
        """
        Returns a dict of ratios:
            key: value / sum of values.
        If sum of values is 0 then returns a dict of zeros.
        """
        total = sum(self.values())
        if abs(total) > 1e-10:
            ratios = self / total
        else:
            ratios = Arithmetic_Dict({
                key: 0 for key in self
            })
        return ratios
