from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from ...auxiliaries.constants import (FOOD_CONSUMPTION, HAPPINESS_DECAY,
                                      INBUILT_RESOURCES, OTHERS_MINIMUM_WAGE,
                                      WOOD_CONSUMPTION)
from ...auxiliaries.enums import Class_Name, Resource
from ...auxiliaries.resources import Resources

if TYPE_CHECKING:
    from ..state_data import State_Data


class ValidationError(Exception):
    """
    Raised when social class validation fails.
    """


class InvalidInputError(ValueError):
    """
    Raised when attempting to create a government or a social class from
    an invalid dict.
    """


class Class(ABC):
    """
    Represents one social class of the country.
    """
    def __init__(self, parent: State_Data, population: float = 0,
                 resources: Resources = Resources()) -> None:
        """
        Creates an Class object. Resources default to zero.
        """
        self.parent: State_Data = parent

        if population < 0:
            raise ValueError("population cannot be negative")
        self._population: float = population

        if resources < 0:
            raise ValueError("resources cannot be negative at the beginning")
        self.resources: Resources = resources.copy()

        self.starving: bool = False
        self.freezing: bool = False
        self.demoted_from: bool = False
        self.demoted_to: bool = False
        self.promoted_from: bool = False
        self.promoted_to: bool = False

        self.happiness: float = 0

        # Attributes used only during employment calculation and history
        self.employees: float = 0
        self.wage: float = 0
        self.wage_share: float
        self.increase_wage: bool
        self.profit_share: float
        self.old_wage: float = OTHERS_MINIMUM_WAGE

        # Attributes used only when trading
        self.market_res: Resources
        self.money: float

        # This is assigned by State_Data in classes setter. It should be
        # assigned before the object is used.
        self.lower_class: Class = None  # type: ignore

    @property
    @abstractmethod
    def class_name(self) -> Class_Name:
        """
        Returns the name of the class as an enumerator (Class_Name).
        """

    @property
    def population(self) -> float:
        return self._population

    @population.setter
    def population(self, new: float) -> None:
        if new < 0:
            raise ValueError("population cannot be negative")
        difference = new - self._population
        self.resources -= INBUILT_RESOURCES[self.class_name] * difference
        self._population = new

    @property
    def employable(self) -> bool:
        return False

    @property
    def real_resources(self) -> Resources:
        return self.resources + (
            INBUILT_RESOURCES[self.class_name] * self.population
        )

    @property
    def optimal_resources(self) -> Resources:
        """
        Returns optimal resources for the given social class object, for
        trade purposes.
        """
        return self.parent.sm.optimal_resources[self.class_name] \
            * self.population

    @property
    def missing_resources(self) -> Resources:
        """
        Returns the resources the class is missing to not have any negative
        resources.
        """
        return Resources({
            resource: -amount if amount < 0 else 0
            for resource, amount
            in self.resources.items()
        })

    @property
    def class_overpopulation(self) -> float:
        """
        Returns how many of the class need to be demoted to remove
        negative resources.
        """
        overpops: list[float] = []
        for res_name, value in self.missing_resources.items():
            res = INBUILT_RESOURCES[self.class_name][res_name] - \
                INBUILT_RESOURCES[self.lower_class.class_name][res_name]
            if res > 0:
                overpops.append(value / res)

        if overpops:
            return max(overpops)
        else:
            return 0

    @property
    def net_worth(self) -> float:
        return self.real_resources.worth(self.parent.prices)

    @property
    def max_employees(self) -> float:
        land_owned = self.resources.land + \
            INBUILT_RESOURCES[self.class_name].land * self.population
        return min(
            self.resources.tools / 3,
            land_owned / self.parent.sm.worker_land_usage,
        )

    def grow_population(self, modifier: float) -> None:
        """
        Modifier specifies by how much to modify the population,
        negative means decrease in numbers.
        Modifier 0 means no change in population.
        Also consumes the class' resources, if they are needed for growth.
        """
        self.population *= (1 + modifier)

    def consume(self) -> None:
        """
        Removes resources the class consumed in the month.
        """
        self.resources -= Resources({
            Resource.food: FOOD_CONSUMPTION * self.population,
            Resource.wood: WOOD_CONSUMPTION[
                self.parent.month] * self.population
        })

    @abstractmethod
    def produce(self) -> None:
        """
        Adds resources the class produced in the month.
        """

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the social class object to a dict.
        """
        return {
            "population": self.population,
            "resources": self.resources.to_raw_dict(),
            "starving": self.starving,
            "freezing": self.freezing,
            "demoted_from": self.demoted_from,
            "demoted_to": self.demoted_to,
            "promoted_from": self.promoted_from,
            "promoted_to": self.promoted_to,
            "happiness": self.happiness
        }

    @classmethod
    def from_dict(cls, parent: State_Data, data: dict[str, Any]) -> Self:
        """
        Creates a social class object from the given dict.
        lower_class still needs to be set!
        """
        try:
            new = cls(parent, float(data["population"]),
                      Resources.from_raw_dict(data["resources"]))

            new.parent = parent

            new.starving = bool(data["starving"])
            new.freezing = bool(data["freezing"])
            new.demoted_from = bool(data["demoted_from"])
            new.demoted_to = bool(data["demoted_to"])
            new.promoted_from = bool(data["promoted_from"])
            new.promoted_to = bool(data["promoted_to"])

            new.happiness = float(data["happiness"])
        except (KeyError, ValueError) as e:
            raise InvalidInputError from e

        return new

    def handle_empty_class(self) -> None:
        """
        Makes classes with pop < 0.5 effectively empty. Resources are handed
        over to the government.
        """
        if self.population < 0.5:
            self.population = 0
            self.parent.government.resources += self.resources
            self.resources = Resources()

    def validate(self) -> None:
        """
        Handles very small amounts of negative resources resulting from
        floating-point math. Raises an exception if resources is negative
        after that.
        """
        for resource in Resource:
            if self.resources[resource] < 0:
                if -0.0001 < self.resources[resource]:
                    self.resources[resource] = 0
                else:
                    raise ValidationError(
                        f"{resource.name} in {self.class_name} negative"
                    )

    def decay_happiness(self) -> None:
        """
        Changes the happiness towards zero. Changes are bigger the further
        happiness is from zero.
        """
        self.happiness *= (1 - HAPPINESS_DECAY)
        if abs(self.happiness) < 0.5:
            self.happiness = 0

    @staticmethod
    def starvation_happiness(part_dead: float) -> float:
        """
        Returns the change in happiness of a social class whose given part
        died of starvation or freezing.
        """
        percent_dead = part_dead * 100
        return (percent_dead ** 2.5) / (percent_dead - 100.01) - percent_dead

    @staticmethod
    def resources_seized_happiness(worth_seized_per_capita: float) -> float:
        """
        Returns the change in happiness of a social class whose given part
        of resources was seized by the government.
        """
        return worth_seized_per_capita * -5
