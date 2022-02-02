from .constants import (
    FOOD_CONSUMPTION,
    LAND_TYPES,
    RESOURCES,
    WOOD_CONSUMPTION
)
from .state_data import State_Data
from math import floor


class Class:
    """
    Represents one social class of the country.
    Attributes:
    _parent - state this class is part of
    _population - population of the class
    _resources - dictionary containing all the resources the class owns
    _land - dictionary containing info on the land the class owns
    """
    def __init__(self, parent: "State_Data", population: int,
                 resources: dict = None, land: dict = None):
        self.parent = parent
        self.population = population
        if resources is None:
            self.resources = {
                "food": 0,
                "wood": 0,
                "iron": 0,
                "stone": 0,
                "tools": 0
            }
        else:
            self.resources = resources

        if land is None:
            self.land = {
                "fields": 0,
                "woods": 0,
                "stone_mines": 0,
                "iron_mines": 0
            }
        else:
            self.land = land

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        assert new_parent.month in WOOD_CONSUMPTION
        self._parent = new_parent

    @property
    def population(self):
        return self._population

    @population.setter
    def population(self, number):
        assert number >= 0
        self._population = number

    @property
    def resources(self):
        return self._resources.copy()

    @resources.setter
    def resources(self, new_resources: dict):
        for resource in RESOURCES:
            assert resource in new_resources
        self._resources = new_resources.copy()

    @property
    def land(self):
        return self._land.copy()

    @land.setter
    def land(self, new_land: dict):
        for land_type in LAND_TYPES:
            assert land_type in new_land
        self._land = new_land.copy()

    @property
    def optimal_resources(self):
        opt_res = {
            resource: resource_per_capita * self._population
            for resource, resource_per_capita
            in self.optimal_resources_per_capita(
                self._parent.month
            ).items()
        }
        return opt_res

    @property
    def missing_resources(self):
        miss_res = {
            resource: -amount if amount < 0 else 0
            for resource, amount
            in self.resources.items()
        }
        return miss_res

    @property
    def class_overpopulation(self):
        pass

    def grow_population(self, modifier: float):
        """
        Modifier specifies by how much to modify the population,
        negative means decrease in numbers.
        Modifier 0 means no change in population.
        Also consumes the class' resources, if they are needed for growth.
        """
        grown = floor(self._population * modifier)
        self._population += grown
        return grown

    @staticmethod
    def optimal_resources_per_capita(month: str):
        """
        Food needed: four months' consumption, producers
                     may need more as stockpile
        Wood needed: yearly consumption + depending on class
        Iron needed: depends on particular class
        Stone needed: depends on particular class
        Tools needed: depends on particular class
        """
        optimal_resources = {
            "food": 4,
            "wood": sum(WOOD_CONSUMPTION.values()),
            "iron": 0,
            "stone": 0,
            "tools": 0
        }
        return optimal_resources

    def produce(self):
        """
        Adds resources the class produced in the current month.
        """
        pass

    def consume(self):
        """
        Removes resources the class consumed in the month.
        Sets missing resources to signal shortages.
        """
        month = self._parent.month
        food_consumed = FOOD_CONSUMPTION * self._population
        wood_consumed = WOOD_CONSUMPTION[month] * self._population

        self._resources["food"] -= food_consumed
        self._resources["wood"] -= wood_consumed

    def move_population(self, number: int, demotion: bool = False):
        """
        Moves the given number of people into or out of the class.
        Negative number signifies movement out.
        Demotion flag signifies that people are moved out because of
        no resources.
        """
        self._population += number
