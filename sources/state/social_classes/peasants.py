from ...auxiliaries.constants import (
    DEFAULT_PRICES,
    PEASANT_TOOL_USAGE,
    FOOD_PRODUCTION,
    WOOD_PRODUCTION,
    LAND_TYPES
)
from ...auxiliaries.arithmetic_dict import Arithmetic_Dict
from .class_file import Class


class Peasants(Class):
    """
    Represents the Peasants of the country.
    Peasants make food and wood.
    They own land (but not mines) and they cannot work as employees.
    """
    @staticmethod
    def create_from_dict(parent, data):
        population = data["population"]
        resources = data["resources"]
        land = data["land"]
        return Peasants(parent, population, resources, land)

    @property
    def land(self):
        return self._land.copy()

    @land.setter
    def land(self, new_land: dict):
        for land_type in LAND_TYPES:
            assert land_type in new_land
            if land_type in {"stone_mines", "iron_mines"}:
                assert new_land[land_type] == 0
            else:
                assert new_land[land_type] >= 0
        self._land = Arithmetic_Dict(new_land)

    @property
    def class_overpopulation(self):
        resources = {"tools", "wood"}
        overpop = 0
        for resource in resources:
            if self._resources[resource] < 0:
                overpop = max(overpop, -self._resources[resource] / 3)
        total_land = self._land["fields"] + self._land["woods"]
        minimum_land = 15 * self._population
        if total_land < minimum_land:
            overpop = max(overpop, (minimum_land - total_land) / 15)
        return overpop

    def _add_population(self, number: int):
        """
        Adds new peasants to the class. Does not modify _population, only
        handles the initiation resources.
        """
        self._resources["wood"] -= 3 * number
        self._resources["tools"] -= 3 * number

    def optimal_resources_per_capita(self):
        """
        Food needed: four months' consumption
        Wood needed: yearly consumption + 1 (3 needed for new peasant)
        Iron needed: none
        Stone needed: none
        Tools needed: enough to work half a year + 1 (3 needed for new peasant)
        """
        optimal_resources = super().optimal_resources_per_capita()
        optimal_resources["wood"] += 1
        optimal_resources["tools"] += sum(PEASANT_TOOL_USAGE.values()) / 2 + 1
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
        peasants = self._get_working_peasants()
        month = self._parent.month

        food_per_capita = FOOD_PRODUCTION[month]
        wood_per_capita = WOOD_PRODUCTION

        wood_need_ratio = self._parent.prices["wood"] / DEFAULT_PRICES["wood"]
        food_need_ratio = self._parent.prices["food"] / DEFAULT_PRICES["food"]
        needed_wood_peasants_rel = wood_need_ratio / WOOD_PRODUCTION
        needed_food_peasants_rel = \
            food_need_ratio / (sum(FOOD_PRODUCTION.values()) / 12)
        ideal_wood_ratio = needed_wood_peasants_rel / \
            (needed_food_peasants_rel + needed_wood_peasants_rel)

        if ideal_wood_ratio * peasants * 20 > self._land["woods"]:
            wood_peasants = self._land["woods"] / 20
        else:
            wood_peasants = ideal_wood_ratio * peasants

        food_peasants = peasants - wood_peasants
        if food_peasants * 20 > self._land["fields"]:
            wood_peasants += food_peasants - self._land["fields"] / 20
            food_peasants = self._land["fields"] / 20

        produced = Arithmetic_Dict({
            "food": food_per_capita * food_peasants,
            "wood": wood_per_capita * wood_peasants
        })
        used = Arithmetic_Dict({
            "tools": PEASANT_TOOL_USAGE[month] * peasants
        })

        self._resources -= used
        self._resources += produced

        return produced, used

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
            self._resources["wood"] += -3 * number
            self._resources["tools"] += -3 * number
