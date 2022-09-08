from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..auxiliaries.resources import Resources
from ..auxiliaries.soldiers import Soldiers
from .social_classes.class_file import InvalidInputError, ValidationError

if TYPE_CHECKING:
    from .state_data import State_Data


class Government:
    """
    Represents the government of the country - the object that the player has
    the most direct control over.
    Properties:
    parent - state this government is part of
    resources - dictionary containing info on the resources the govt owns
    new_resources - temporary resources owned by the govt
    secure_resources - govt's resources declared to be untradeable
    real_resources - how much resources in total the govt owns
    optimal_resources - how much resources the govt wants to own
    max_employees - how many employees can the govt employ
    """
    def __init__(self, parent: State_Data, res: Resources = Resources(),
                 optimal_res: Resources = Resources(),
                 secure_res: Resources = Resources(),
                 soldiers: Soldiers = Soldiers()):
        """
        Creates an object of type Government.
        Parent is the State_Data object this belongs to.
        """
        self.parent: State_Data = parent

        if res < 0:
            raise ValueError("resources cannot be negative")
        else:
            self.resources: Resources = res.copy()

        if optimal_res < 0:
            raise ValueError("optimal resources cannot be negative")
        else:
            self.optimal_resources: Resources = optimal_res.copy()

        if secure_res < 0:
            raise ValueError("secure resources cannot be negative")
        else:
            self.secure_resources: Resources = secure_res.copy()

        self.wage: float = self.parent.sm.others_minimum_wage
        self.wage_autoregulation: bool = True

        if soldiers < 0:
            raise ValueError("soldiers cannot be negative")
        else:
            self.soldiers: Soldiers = soldiers.copy()

        self.missing_food: float = 0

        # Attributes used only during employment calculation and history
        self.employees: float = 0
        self.increase_wage: bool
        self.profit_share: float
        self.old_wage: float = self.parent.sm.others_minimum_wage

        # Attributes used only when trading
        self.market_res: Resources
        self.money: float

    @property
    def real_resources(self) -> Resources:
        return self.resources + self.secure_resources

    @property
    def max_employees(self) -> float:
        land_owned = self.resources.land
        return min(
            self.resources.tools / 3,
            land_owned / self.parent.sm.worker_land_usage,
        )

    @property
    def soldier_revolt(self) -> bool:
        return self.missing_food > 0

    def consume(self) -> None:
        """
        Removes resources the government's soldiers consumed this month.
        """
        self.resources.food -= self.soldiers.food_consumption
        if self.resources.food < 0:
            self.missing_food = -self.resources.food
            self.resources.food = 0
        else:
            self.missing_food = 0

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the government object to a dict.
        """
        return {
            "resources": self.resources.to_raw_dict(),
            "optimal_resources": self.optimal_resources.to_raw_dict(),
            "secure_resources": self.secure_resources.to_raw_dict(),
            "wage": self.wage,
            "wage_autoregulation": self.wage_autoregulation,
            "soldiers": self.soldiers.to_raw_dict(),
            "missing_food": self.missing_food,
            "employees": self.employees,
            "old_wage": self.old_wage
        }

    @classmethod
    def from_dict(cls, parent: State_Data, data: dict[str, Any]) -> Government:
        """
        Creates a government object from the given dict.
        """
        try:
            new = cls(
                parent, Resources.from_raw_dict(data["resources"]),
                Resources.from_raw_dict(data["optimal_resources"]),
                Resources.from_raw_dict(data["secure_resources"]),
                Soldiers.from_raw_dict(data["soldiers"])
            )
            new.wage = float(data["wage"])
            new.wage_autoregulation = bool(data["wage_autoregulation"])
            new.missing_food = float(data["missing_food"])
            new.employees = float(data["employees"])
            new.old_wage = float(data["old_wage"])
        except (KeyError, ValueError) as e:
            raise InvalidInputError from e
        return new

    def validate(self) -> None:
        """
        Handles very small amounts of negative resources or soldiers resulting
        from floating-point math. Raises ValidationError if resources or
        soldiers is negative after that.
        """
        for name in ("resources", "optimal_resources", "secure_resources"):
            resources = getattr(self, name)
            for res in resources:
                if resources[res] < 0:
                    if -0.0001 < resources[res]:
                        resources[res] = 0
                    else:
                        raise ValidationError(
                            f"{res} in government's {name} negative"
                        )

        for sol in self.soldiers:
            if self.soldiers[sol] < 0:
                if -0.0001 < self.soldiers[sol]:
                    self.soldiers[sol] = 0
                else:
                    raise ValidationError(
                        f"{sol} in government's soldiers negative"
                    )
