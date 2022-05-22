from ...auxiliaries.constants import (
    DEFAULT_PRICES,
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
    @property
    def class_name(self):
        return CLASSES[0]

    def _get_employees(self):
        """
        Returns the number of people the nobles will employ this month.
        """
        return min(
            self.resources["tools"] / 3,
            self.parent.get_available_employees()
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
        return self._get_ratios(self.parent.prices) * self._get_employees()

    def _get_tools_used(self, employees):
        """
        Returns the amount of tools that will be used in production this month.
        """
        peasant_tools_used = self.parent.sm.peasant_tool_usage * \
            (employees["food"] + employees["wood"])
        miner_tools_used = self.parent.sm.miner_tool_usage * \
            (employees["stone"] + employees["iron"])

        return peasant_tools_used + miner_tools_used

    def produce(self):
        """
        Adds resources the class' employees produced in the current month.
        """
        per_capita = Arithmetic_Dict({
            "food": self.parent.sm.food_production[self._parent.month],
            "wood": self.parent.sm.wood_production,
            "stone": self.parent.sm.stone_production,
            "iron": self.parent.sm.iron_production
        })
        ratioed_emps = self._get_ratioed_employees()
        produced = per_capita * ratioed_emps

        self._new_resources["tools"] -= self._get_tools_used(ratioed_emps)
        self.new_resources += produced * (1 - self.parent.sm.others_wage)
        self.parent.payments += produced * self.parent.sm.others_wage
