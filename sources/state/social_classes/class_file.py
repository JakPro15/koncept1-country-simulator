from ...auxiliaries.constants import (
    FOOD_CONSUMPTION,
    LAND_TYPES,
    RESOURCES,
    WOOD_CONSUMPTION
)
from ...auxiliaries.arithmetic_dict import Arithmetic_Dict


class Class:
    """
    Represents one social class of the country.
    Properties:
    parent - state this class is part of
    employable - whether the class can be hired as employees
    population - population of the class
    resources - dictionary containing info on the resources the class owns
    land - dictionary containing info on the land the class owns
    optimal_resources - how much resources the class wants to own
    missing_resources - how much resources the class needs to own to not die
    class_overpopulation - how many of the class need to be demoted because of
                           no resources
    """
    def __init__(self, parent, population: int,
                 resources: dict = None, land: dict = None):
        self.parent = parent
        self.population = population
        if resources is None:
            self.resources = {
                resource: 0 for resource in RESOURCES
            }
        else:
            self.resources = resources

        if land is None:
            self.land = {
                land_type: 0 for land_type in LAND_TYPES
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
    def employable(self):
        return False

    @property
    def population(self):
        return self._population

    @population.setter
    def population(self, number):
        assert number >= 0
        self._population = number

    @property
    def resources(self):
        return self._resources

    @resources.setter
    def resources(self, new_resources: dict):
        for resource in RESOURCES:
            assert resource in new_resources
        self._resources = Arithmetic_Dict(new_resources)

    @property
    def land(self):
        return self._land

    @land.setter
    def land(self, new_land: dict):
        for land_type in LAND_TYPES:
            assert land_type in new_land
            assert new_land[land_type] >= 0
        self._land = Arithmetic_Dict(new_land)

    @property
    def optimal_resources(self):
        opt_res = {
            resource: resource_per_capita * self._population
            for resource, resource_per_capita
            in self.optimal_resources_per_capita().items()
        }
        return Arithmetic_Dict(opt_res)

    @property
    def missing_resources(self):
        miss_res = {
            resource: -amount if amount < 0 else 0
            for resource, amount
            in self.resources.items()
        }
        return Arithmetic_Dict(miss_res)

    def grow_population(self, modifier: float):
        """
        Modifier specifies by how much to modify the population,
        negative means decrease in numbers.
        Modifier 0 means no change in population.
        Also consumes the class' resources, if they are needed for growth.
        """
        grown = self._population * modifier
        self._population += grown
        self._add_population(grown)
        return grown

    def optimal_resources_per_capita(self):
        """
        Food needed: four months' consumption
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
        return Arithmetic_Dict(optimal_resources)

    def consume(self):
        """
        Removes resources the class consumed in the month.
        Sets missing resources to signal shortages.
        """
        month = self._parent.month

        consumed = {
            "food": FOOD_CONSUMPTION * self._population,
            "wood": WOOD_CONSUMPTION[month] * self._population
        }

        self._resources -= consumed
        if self._resources["food"] < 0:
            consumed["food"] += self._resources["food"]
        if self._resources["wood"] < 0:
            consumed["wood"] += self._resources["wood"]

        return consumed

    def move_population(self, number: int, demotion: bool = False):
        """
        Moves the given number of people into or out of the class.
        Negative number signifies movement out.
        Demotion flag signifies that people are moved out because of
        no resources.
        """
        self._population += number

    def to_dict(self):
        data = {
            "population": self.population,
            "resources": dict(self.resources),
            "land": dict(self.land)
        }
        return data
