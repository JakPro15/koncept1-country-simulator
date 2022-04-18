from ...auxiliaries.constants import (
    DEFAULT_PRICES,
    OTHERS_WAGE,
    PEASANT_TOOL_USAGE,
    FOOD_PRODUCTION,
    WOOD_PRODUCTION,
    STONE_PRODUCTION,
    IRON_PRODUCTION,
    MINER_TOOL_USAGE,
    CLASSES
)
from ...auxiliaries.arithmetic_dict import Arithmetic_Dict
from .class_file import Class


class Nobles(Class):
    """
    Represents the Nobles of the country.
    Nobles do not make anything.
    They cannot work as employees.
    They employ Others.
    They do not promote.
    They demote to Peasants.
    """
    @staticmethod
    @property
    def class_name():
        return CLASSES[0]

    def _get_employees(self):
        """
        Returns the number of people the nobles will employ this month.
        """
        return min(
            self.resources["tools"] / 3, self._parent.get_available_employees()
        )

    def _get_ratios(self, prices):
        """
        Returns a dict of ratios: resource producers to total employees.
        """
        new_prices = Arithmetic_Dict(prices) / DEFAULT_PRICES
        total_prices = sum(new_prices.values()) - new_prices["tools"]
        if total_prices != 0:
            ratios = Arithmetic_Dict({
                "food": new_prices["food"] / total_prices,
                "wood": new_prices["wood"] / total_prices,
                "stone": new_prices["stone"] / total_prices,
                "iron": new_prices["iron"] / total_prices
            })
        else:
            ratios = Arithmetic_Dict({
                "food": 0,
                "wood": 0,
                "stone": 0,
                "iron": 0
            })
        return ratios

    def _get_ratioed_employees(self):
        """
        Returns a dict of particular resource producing employees.
        """
        return self._get_ratios(self._parent.prices) * self._get_employees()

    def _get_tools_used(self):
        """
        Returns the amount of tools that will be used in production this month.
        """
        employees = self._get_ratioed_employees()
        peasant_tools_used = PEASANT_TOOL_USAGE * \
            (employees["food"] + employees["wood"])
        miner_tools_used = MINER_TOOL_USAGE * \
            (employees["stone"] + employees["iron"])

        return peasant_tools_used + miner_tools_used

    def produce(self):
        """
        Adds resources the class' employees produced in the current month.
        """
        per_capita = Arithmetic_Dict({
            "food": FOOD_PRODUCTION[self._parent.month],
            "wood": WOOD_PRODUCTION,
            "stone": STONE_PRODUCTION,
            "iron": IRON_PRODUCTION
        })
        produced = per_capita * self._get_ratioed_employees()

        self.resources["tools"] -= self._get_tools_used()
        self.resources += produced * (1 - OTHERS_WAGE)
        self.parent.payments += produced * OTHERS_WAGE
