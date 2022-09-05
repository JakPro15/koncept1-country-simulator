from __future__ import annotations

from numbers import Real
from typing import Mapping

from .arithmetic_dict import Arithmetic_Dict
from .constants import KNIGHT_FIGHTING_STRENGTH, KNIGHT_FOOD_CONSUMPTION
from .enums import Soldier


class Soldiers(Arithmetic_Dict[Soldier]):
    """
    Represents a number of soldiers.
    Access to resources is as follows:
    by attribute - res.knights
    by enumerator - res[Soldier.knights]
    """
    def __init__(
        self, soldiers: Mapping[Soldier, float] | float | None = None
    ) -> None:
        """
        If a dict is given as argument, the object is constructed from it.
        Number argument makes a dict with all soldier types of the given value.
        None as argument makes an empty Soldiers object
        (all soldiers set to zero).
        """
        super().__init__()
        if isinstance(soldiers, Mapping):
            for sol in Soldier:
                self[sol] = soldiers.get(sol, 0)
        elif isinstance(soldiers, Real):
            for sol in Soldier:
                self[sol] = soldiers
        elif soldiers is not None:
            raise TypeError("soldiers argument must be a dict or a number")

    @property
    def footmen(self) -> float:
        return self.get(Soldier.footmen, 0.0)

    @footmen.setter
    def footmen(self, new: float) -> None:
        self[Soldier.footmen] = float(new)

    @property
    def knights(self) -> float:
        return self.get(Soldier.knights, 0.0)

    @knights.setter
    def knights(self, new: float) -> None:
        self[Soldier.knights] = float(new)

    @property
    def strength(self) -> float:
        return self.knights * KNIGHT_FIGHTING_STRENGTH + self.footmen

    @property
    def number(self) -> float:
        return self.knights + self.footmen

    @property
    def food_consumption(self) -> float:
        return self.knights * KNIGHT_FOOD_CONSUMPTION + self.footmen

    def to_raw_dict(self) -> dict[str, float]:
        """
        Converts the Soldiers object into a raw dict, with resource names,
        not enumerators, as keys.
        """
        return {
            key.name: value for key, value in self.items()
        }

    def __getitem__(self, __k: Soldier) -> float:
        return self.get(__k, 0)

    def __delitem__(self, __k: Soldier) -> None:
        self[__k] = 0
