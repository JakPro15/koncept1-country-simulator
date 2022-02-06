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

    @staticmethod
    def optimal_resources_per_capita(month: str):
        """
        Food needed: enough to survive till harvest, plus three months
        Wood needed: yearly consumption + 1 (3 needed for new peasant)
        Iron needed: none
        Stone needed: none
        Tools needed: enough to work half a year + 1 (3 needed for new peasant)
        """
        optimal_resources = Class.optimal_resources_per_capita(month)
        optimal_resources["food"] += 9
        optimal_resources["wood"] += 4.6
        optimal_resources["stone"] += 8
        optimal_resources["tools"] += 10
        return optimal_resources

    def _get_working_peasants(self):
        """
        Returns the number of fully working peasants.
        """
        land_available = (self.land['fields'] + self.land['woods']) / 20
        working_peasants = min(land_available, self._population)
        return working_peasants

    def produce(self):
        """
        Adds resources the class produced in the current month.
        """
        total_land = self._land["fields"] + self._land["woods"] + \
            self._land["stone_mines"] * 2000 + self._land["iron_mines"] * 2000
        wanted_employees = min(total_land // 20, self.resources["tools"] / 3)
        available_employees = self._parent.get_available_employees()
        employees = min(wanted_employees, available_employees)

        food_ratio = self._land["fields"] / total_land
        wood_ratio = self._land["wood"] / total_land
        stone_ratio = self._land["stone"] / total_land
        iron_ratio = self._land["iron"] / total_land

        farmers = food_ratio * employees
        lumberjacks = wood_ratio * employees
        stone_miners = stone_ratio * employees
        iron_miners = iron_ratio * employees

        month = self._parent.month

        food_per_capita = FOOD_PRODUCTION[month]
        wood_per_capita = WOOD_PRODUCTION
        stone_per_capita = STONE_PRODUCTION
        iron_per_capita = IRON_PRODUCTION

        new_food = food_per_capita * farmers
        new_wood = wood_per_capita * lumberjacks
        new_stone = stone_per_capita * stone_miners
        new_iron = iron_per_capita * iron_miners

        peasant_tools_used = PEASANT_TOOL_USAGE[month] * \
            (farmers + lumberjacks)
        miner_tools_used = MINER_TOOL_USAGE * \
            (stone_miners + iron_miners)

        tools_consumed = peasant_tools_used + miner_tools_used

        self._resources["tools"] -= tools_consumed

        self._resources["food"] += new_food
        self._resources["wood"] += new_wood
        self._resources["stone"] += new_stone
        self._resources["iron"] += new_iron

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
