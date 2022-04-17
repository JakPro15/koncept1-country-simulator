from ...auxiliaries.constants import (
    CLASSES,
    DEFAULT_PRICES,
    PEASANT_TOOL_USAGE,
    FOOD_PRODUCTION,
    WOOD_PRODUCTION
)
from ...auxiliaries.arithmetic_dict import Arithmetic_Dict
from .class_file import Class


class Peasants(Class):
    """
    Represents the Peasants of the country.
    Peasants make food and wood.
    They own land (but not mines) and they cannot work as employees.
    """
    def class_name(self):
        return CLASSES[2]

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
            "food": FOOD_PRODUCTION[month] * food_peasants,
            "wood": WOOD_PRODUCTION * wood_peasants,
            "tools": -PEASANT_TOOL_USAGE[month] * self.population
        })

        self.resources += changes
