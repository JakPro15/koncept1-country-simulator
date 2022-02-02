from .classfile import Class
from .constants import (
    PEASANT_FOOD_NEEDED,
    PEASANT_TOOL_USAGE,
    FOOD_PRODUCTION,
    WOOD_PRODUCTION
)
from math import ceil


class Peasants(Class):
    def _add_population(self, number: int):
        """
        Adds new peasants to the class. Does not modify _population, only
        handles the initiation resources.
        """
        self.resources["wood"] -= 3 * number
        self.resources["tools"] -= 3 * number
        resources = {"tools", "wood"}
        for resource in resources:
            if self.resources[resource] < 0:
                self.class_overpopulation = \
                    max(self.class_overpopulation,
                        ceil(-self.resources[resource] / 3))

    def grow_population(self, modifier: float):
        """
        Modifier specifies by how much to modify the population,
        negative means decrease in numbers.
        Modifier 0 means no change in population.
        Also consumes the class' resources, if th ey are needed for growth.
        """
        grown = super().grow_population(modifier)
        self._add_population(grown)

    @staticmethod
    def get_food_needed_till_harvest(month: str):
        return PEASANT_FOOD_NEEDED.get(month, 0)

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
        optimal_resources["food"] += \
            Peasants.get_food_needed_till_harvest(month) - 1
        optimal_resources["wood"] += 1
        optimal_resources["tools"] += sum(PEASANT_TOOL_USAGE.values()) / 2 + 1
        return optimal_resources

    def _get_working_peasants(self):
        """
        Returns the number of fully working peasants.
        """
        land_available = (self._land['fields'] + self._land['woods']) / 20
        working_peasants = min(land_available, self._population)
        return working_peasants

    def produce(self):
        """
        Adds resources the class produced in the current month.
        """
        peasants = self._get_working_peasants()
        month = self._parent.month

        food_per_capita = FOOD_PRODUCTION[month]
        wood_per_capita = WOOD_PRODUCTION

        total_land = self._land["fields"] + self._land["woods"]
        food_ratio = self._land["fields"] / total_land

        food_peasants = ceil(food_ratio * peasants)
        wood_peasants = peasants - food_peasants

        new_food = food_per_capita * food_peasants
        new_wood = wood_per_capita * wood_peasants

        tools_consumed = PEASANT_TOOL_USAGE[month] * peasants
        self.resources["tools"] -= tools_consumed
        if self.resources["tools"] < 0:
            self.class_overpopulation = ceil(-self.resources["tools"] / 3)

        self.resources["food"] += new_food
        self.resources["wood"] += new_wood

    def move_population(self, number: int, demotion: bool = False):
        """
        Moves the given number of people into or out of the class.
        Negative number signifies movement out.
        Demotion flag signifies that people are moved out because of
        no resources.
        """
        super().move_population(number, demotion)
        if number > 0:
            self._add_population(number)
        elif demotion:
            self.resources["wood"] += -3 * number
            self.resources["tools"] += -3 * number
