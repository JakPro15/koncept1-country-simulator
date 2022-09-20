from __future__ import annotations

from numbers import Real
from typing import Any, Mapping

from typing_extensions import Self

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
        self, soldiers: Mapping[Soldier, float] | float = {}
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
        else:
            raise TypeError("soldiers argument must be a dict or a number")

    @property
    def footmen(self) -> float:
        return self.get(Soldier.footmen, 0.0)

    @footmen.setter
    def footmen(self, new: float) -> None:
        self[Soldier.footmen] = new

    @footmen.deleter
    def footmen(self) -> None:
        del self[Soldier.footmen]

    @property
    def knights(self) -> float:
        return self.get(Soldier.knights, 0.0)

    @knights.setter
    def knights(self, new: float) -> None:
        self[Soldier.knights] = new

    @knights.deleter
    def knights(self) -> None:
        del self[Soldier.knights]

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
        Ignores all keys that are not of type Soldier.
        """
        return {key.name: self[key] for key in Soldier}

    @classmethod
    def from_raw_dict(cls, raw_dict: Mapping[Any, float]) -> Self:
        """
        Creates a Soldiers object from the given raw dict, with soldier names,
        not enumerators, as keys.
        Ignores all keys that do not correspond to Soldier enumerators.
        If the dict contains enumerators as keys, each enum key is taken
        instead of the corresponding string key.
        """
        new_dict: dict[Soldier, float] = {}
        for res in Soldier:
            try:
                new_dict[res] = raw_dict[res]
            except KeyError:
                new_dict[res] = raw_dict.get(res.name, 0)
        return cls(new_dict)

    def __delitem__(self, __k: Soldier) -> None:
        # so that all Soldier enumerators are always keys of the object
        self[__k] = 0
