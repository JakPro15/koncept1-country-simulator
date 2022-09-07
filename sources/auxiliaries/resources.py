from __future__ import annotations

from numbers import Real
from typing import Mapping

from typing_extensions import Self

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
        self, resources: Mapping[Resource, float] | float = {}
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
        else:
            raise TypeError("Resources construction argument must be a mapping"
                            " object or a real number")

    @property
    def food(self) -> float:
        return self[Resource.food]

    @food.setter
    def food(self, new: float) -> None:
        self[Resource.food] = new

    @property
    def wood(self) -> float:
        return self[Resource.wood]

    @wood.setter
    def wood(self, new: float) -> None:
        self[Resource.wood] = new

    @property
    def stone(self) -> float:
        return self[Resource.stone]

    @stone.setter
    def stone(self, new: float) -> None:
        self[Resource.stone] = new

    @property
    def iron(self) -> float:
        return self[Resource.iron]

    @iron.setter
    def iron(self, new: float) -> None:
        self[Resource.iron] = new

    @property
    def tools(self) -> float:
        return self[Resource.tools]

    @tools.setter
    def tools(self, new: float) -> None:
        self[Resource.tools] = new

    @property
    def land(self) -> float:
        return self[Resource.land]

    @land.setter
    def land(self, new: float) -> None:
        self[Resource.land] = new

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
        Ignores all keys that are not of type Resource.
        """
        return {key.name: self[key] for key in Resource}

    @classmethod
    def from_raw_dict(cls, raw_dict: Mapping[str, float]) -> Self:
        """
        Creates a Resources object from the given raw dict, with resource
        names, not enumerators, as keys.
        Ignores all keys that do not correspond to Resource enumerators.
        """
        new_dict = {
            res: raw_dict.get(res.name, 0) for res in Resource
        }
        return cls(new_dict)

    def __delitem__(self, __k: Resource) -> None:
        # so that all Resource enumerators are always keys in Resources
        self[__k] = 0
