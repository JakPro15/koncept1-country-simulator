from .constants import FOOD_CONSUMPTION, WOOD_CONSUMPTION
from .state_data import State_Data
from math import floor


class Class:
    """
    Represents one social class of the country.
    Attributes:
    _parent - state this class is part of
    _population - population of the class
    resources - dictionary containing all the resources the class owns
    _optimal_resources - how much the class needs in total
    missing_resources - how much the class is starving/freezing
    class_overpopulation - how many of the class need to be moved to lower
                           classes
    """
    def __init__(self, parent: "State_Data", population: int,
                 resources: dict = None, land: dict = None):
        self._parent = parent
        self._population = population
        if resources is None:
            self.resources = {
                "food": 0,
                "wood": 0,
                "iron": 0,
                "stone": 0,
                "tools": 0
            }
        else:
            self.resources = resources.copy()

        if land is None:
            self._land = {
                "fields": 0,
                "woods": 0,
                "stone_mines": 0,
                "iron_mines": 0
            }
        else:
            self._land = land.copy()

        self.missing_resources = {
            "food": 0,
            "wood": 0
        }
        self.class_overpopulation = 0

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

    def get_optimal_resources(self):
        self._calculate_optimal_resources()
        return self._optimal_resources.copy()

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

        self.resources["food"] -= food_consumed
        self.resources["wood"] -= wood_consumed

        resources = {"food", "wood"}
        for resource in resources:
            if self.resources[resource] < 0:
                self.missing_resources[resource] = -self.resources[resource]
                self.resources[resource] = 0

    def move_population(self, number: int, demotion: bool = False):
        """
        Moves the given number of people into or out of the class.
        Negative number signifies movement out.
        Demotion flag signifies that people are moved out because of
        no resources.
        """
        self._population += number
