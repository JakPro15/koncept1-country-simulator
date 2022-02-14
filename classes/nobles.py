from .class_file import Class
from .constants import (
    PEASANT_TOOL_USAGE,
    FOOD_PRODUCTION,
    WOOD_PRODUCTION,
    STONE_PRODUCTION,
    IRON_PRODUCTION,
    MINER_TOOL_USAGE
)
from math import ceil


class Nobles(Class):
    """
    Represents the Nobles of the country.
    Nobles do not make anything.
    They own land and they cannot work as employees.
    """
    @staticmethod
    def create_from_dict(parent, data):
        population = data["population"]
        resources = data["resources"]
        land = data["land"]
        return Nobles(parent, population, resources, land)

    @property
    def class_overpopulation(self):
        overpop = 0
        if self._resources["wood"] < 0:
            overpop = max(overpop, ceil(-self._resources["wood"] / 10))
        if self._resources["stone"] < 0:
            overpop = max(overpop, ceil(-self._resources["stone"] / 4))
        if self._resources["tools"] < 0:
            overpop = max(overpop, ceil(-self._resources["tools"] / 4))
        total_land = self._land["fields"] + self._land["woods"] + \
            self._land["stone_mines"] * 30 + self._land["iron_mines"] * 30
        minimum_land = 30 * self._population
        if total_land < minimum_land:
            overpop = max(overpop, ceil((minimum_land - total_land) / 30))
        return overpop

    def _add_population(self, number: int):
        """
        Adds new nobles to the class. Does not modify _population, only
        handles the initiation resources.
        """
        self._resources["wood"] -= 10 * number
        self._resources["stone"] -= 4 * number
        self._resources["tools"] -= 4 * number

    def optimal_resources_per_capita(self):
        """
        Food needed: enough to survive till harvest, plus three months
        Wood needed: yearly consumption + 1 (3 needed for new peasant)
        Iron needed: none
        Stone needed: none
        Tools needed: enough to work half a year + 1 (3 needed for new peasant)
        """
        optimal_resources = super().optimal_resources_per_capita()
        optimal_resources["food"] += 8
        optimal_resources["wood"] += 4.6
        optimal_resources["stone"] += 8
        optimal_resources["tools"] += \
            4 + (self._get_employees(assesment=True) * 3) / self.population
        return optimal_resources

    def _get_total_land_for_produce(self):
        """
        Returns the total amount of land the nobles own, with mines translated.
        to 2000 ha
        """
        return self._land["fields"] + self._land["woods"] + \
            self._land["stone_mines"] * 2000 + self._land["iron_mines"] * 2000

    def _get_employees(self, assesment=False):
        """
        Returns the number of people the nobles will employ this month.
        """
        total_land = self._get_total_land_for_produce()
        available_employees = self._parent.get_available_employees()
        if not assesment:
            wanted_employees = min(total_land // 20,
                                   self.resources["tools"] / 3)
        else:
            # For assesing the amount of tools nobles want
            wanted_employees = total_land // 20
        return min(wanted_employees, available_employees)

    def _get_ratios(self):
        """
        Returns a dict of ratios: resource producers to total employees.
        """
        total_land = self._get_total_land_for_produce()
        ratios = {
            "food": self._land["fields"] / total_land,
            "wood": self._land["woods"] / total_land,
            "stone": 2000 * self._land["stone_mines"] / total_land,
            "iron": 2000 * self._land["iron_mines"] / total_land
        }
        return ratios

    def _get_ratioed_employees(self):
        """
        Returns a dict of particular resource producing employees.
        """
        employees = self._get_employees()
        ratios = self._get_ratios()
        ratioed = {
            resource: value * employees
            for resource, value
            in ratios.items()
        }
        return ratioed

    def _get_produced_resources(self):
        """
        Returns a dict of resources produced this month.
        """
        month = self._parent.month
        per_capita = {
            "food": FOOD_PRODUCTION[month],
            "wood": WOOD_PRODUCTION,
            "stone": STONE_PRODUCTION,
            "iron": IRON_PRODUCTION
        }
        employees = self._get_ratioed_employees()
        produced = {
            resource: per_capita[resource] * employees[resource]
            for resource
            in per_capita
        }
        return produced

    def _get_tools_used(self):
        """
        Returns the amount of tools that will be used in production this month.
        """
        month = self._parent.month
        employees = self._get_ratioed_employees()
        peasant_tools_used = PEASANT_TOOL_USAGE[month] * \
            (employees["food"] + employees["wood"])
        miner_tools_used = MINER_TOOL_USAGE * \
            (employees["stone"] + employees["iron"])

        return peasant_tools_used + miner_tools_used

    def produce(self):
        """
        Adds resources the class' employees produced in the current month.
        """
        produced = self._get_produced_resources()
        used = {
            "tools": self._get_tools_used()
        }

        self._resources["tools"] -= used["tools"]
        for resource in produced:
            self._resources[resource] += 0.5 * produced[resource]
            self._parent.payments[resource] += 0.5 * produced[resource]

        return produced, used

    def move_population(self, number: int, demotion: bool = False):
        """
        Moves the given number of people into or out of the class.
        Negative number signifies movement out.
        Demotion flag signifies that people are moved out because of
        a shortage of resources.
        """
        super().move_population(number, demotion)
        if number > 0:
            self._add_population(number)
        elif demotion:
            self._resources["wood"] += -10 * number
            self._resources["stone"] += -4 * number
            self._resources["tools"] += -4 * number
