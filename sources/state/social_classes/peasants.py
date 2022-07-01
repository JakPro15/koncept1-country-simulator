from ...auxiliaries.constants import (
    CLASSES,
    INBUILT_RESOURCES,
    DEFAULT_PRICES
)
from ...auxiliaries.arithmetic_dict import Arithmetic_Dict
from .class_file import Class


class Peasants(Class):
    """
    Represents the Peasants of the country.
    Peasants make food and wood.
    They cannot work as employees.
    They promote to Nobles.
    They demote to Others.
    """
    @property
    def class_name(self):
        return CLASSES[2]

    @property
    def max_employees(self):
        land_owned = self.resources["land"] + \
            INBUILT_RESOURCES[self.class_name]["land"] * self.population
        return max(min(
            self.resources["tools"] / 3,
            land_owned / self.parent.sm.worker_land_usage,
        ) - self.population, 0)

    def produce(self):
        """
        Adds resources the class produced in the current month.
        """
        month = self.parent.month
        relative_prices = self.parent.prices / DEFAULT_PRICES

        total_price = relative_prices["food"] + relative_prices["wood"]
        food_peasants = self.population * relative_prices["food"] / total_price
        wood_peasants = self.population * relative_prices["wood"] / total_price

        changes = Arithmetic_Dict({
            "food": self.parent.sm.food_production[month] * food_peasants,
            "wood": self.parent.sm.wood_production * wood_peasants,
            "tools": -self.parent.sm.peasant_tool_usage * self.population
        })

        self.new_resources += changes
