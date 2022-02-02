from .constants import FOOD_CONSUMPTION, WOOD_CONSUMPTION
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
    _optimal_resources - how much the class needs in total
    _missing_resources - how much the class is starving/freezing
    """
    def __init__(self, parent: "State_Data", population: int,
                 resources: dict = None, land: dict = None):
        self._parent = parent
        self._population = population
        if resources is None:
            self._resources = {
                "food": 0,
                "wood": 0,
                "iron": 0,
                "stone": 0,
                "tools": 0
            }
        else:
            self._resources = resources.copy()

        if land is None:
            self.land = {
                "fields": 0,
                "woods": 0,
                "stone_mines": 0,
                "iron_mines": 0
            }
        else:
            self.land = land.copy()

        self._missing_resources = {
            "food": 0,
            "wood": 0
        }
        self._class_overpopulation = 0

    @property
    def parent(self):
        return self._parent

    @property
    def population(self):
        return self._population

    @property
    def resources(self):
        return self._resources.copy()

    @property
    def optimal_resources(self):
        self._calculate_optimal_resources()
        return self._optimal_resources.copy()

    @property
    def missing_resources(self):
        return self._missing_resources.copy()

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

    def _calculate_optimal_resources(self):
        """
        Updates the class' optimal resources.
        """
        self._optimal_resources = {
            resource: resource_per_capita * self._population
            for resource, resource_per_capita
            in self.optimal_resources_per_capita(
                self._parent.month
            ).items()
        }

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

        resources = {"food", "wood"}
        for resource in resources:
            if self._resources[resource] < 0:
                self._missing_resources[resource] = -self._resources[resource]
                self._resources[resource] = 0

    def move_population(self, number: int, demotion: bool = False):
        """
        Moves the given number of people into or out of the class.
        Negative number signifies movement out.
        Demotion flag signifies that people are moved out because of
        no resources.
        """
        self._population += number
