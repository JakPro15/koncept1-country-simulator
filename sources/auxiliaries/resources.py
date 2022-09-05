from __future__ import annotations

from numbers import Real
from typing import Mapping

from .arithmetic_dict import Arithmetic_Dict
from .enums import Resource


class Resources(Arithmetic_Dict[Resource]):
    """
    Represents a portion of resources.
    Access to resources is as follows:
    by attribute - res.land
    by enumerator - res[Resource.land]
    """
    def __init__(
        self, resources: Mapping[Resource, float] | float | None = None
    ) -> None:
        """
        If a dict is given as argument, the object is constructed from it.
        Number argument makes a dict with all resources of the given value.
        None as argument makes an empty Resources object
        (all resources set to zero).
        """
        super().__init__()
        if isinstance(resources, Mapping):
            for res in Resource:
                self[res] = resources.get(res, 0)
        elif isinstance(resources, Real):
            for res in Resource:
                self[res] = resources
        elif resources is not None:
            raise TypeError("Resources construction argument must be a mapping"
                            " object or a real number")

    @property
    def food(self) -> float:
        return self.get(Resource.food, 0.0)

    @food.setter
    def food(self, new: float) -> None:
        self[Resource.food] = new

    @property
    def wood(self) -> float:
        return self.get(Resource.wood, 0.0)

    @wood.setter
    def wood(self, new: float) -> None:
        self[Resource.wood] = float(new)

    @property
    def stone(self) -> float:
        return self.get(Resource.stone, 0.0)

    @stone.setter
    def stone(self, new: float) -> None:
        self[Resource.stone] = float(new)

    @property
    def iron(self) -> float:
        return self.get(Resource.iron, 0.0)

    @iron.setter
    def iron(self, new: float) -> None:
        self[Resource.iron] = float(new)

    @property
    def tools(self) -> float:
        return self.get(Resource.tools, 0.0)

    @tools.setter
    def tools(self, new: float) -> None:
        self[Resource.tools] = float(new)

    @property
    def land(self) -> float:
        return self.get(Resource.land, 0.0)

    @land.setter
    def land(self, new: float) -> None:
        self[Resource.land] = float(new)

    def worth(self, prices: Mapping[Resource, float]) -> float:
        """
        Returns the value of these Resources under the given prices.
        """
        result = 0
        for res in Resource:
            result += self[res] * prices[res]
        return result

    def to_raw_dict(self) -> dict[str, float]:
        """
        Converts the Resources object into a raw dict, with resource names,
        not enumerators, as keys.
        """
        return {
            key.name: self.get(key, 0) for key in Resource
        }

    def __getitem__(self, __k: Resource) -> float:
        return self.get(__k, 0)

    def __delitem__(self, __k: Resource) -> None:
        self[__k] = 0
