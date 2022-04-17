from ...auxiliaries.constants import (
    FOOD_CONSUMPTION,
    INBUILT_RESOURCES,
    MINER_TOOL_USAGE,
    OPTIMAL_RESOURCES,
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
                 resources: dict = None):
        self.parent = parent
        self._population = population
        if resources is None:
            self.resources = {
                resource: 0 for resource in RESOURCES
            }
        else:
            self.resources = resources

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        assert new_parent.month in WOOD_CONSUMPTION
        self._parent = new_parent

    @property
    def class_name(self):
        return "base class"

    @property
    def employable(self):
        return False

    @property
    def population(self):
        return self._population

    @population.setter
    def population(self, number):
        assert number >= 0
        difference = number - self._population
        self._resources -= INBUILT_RESOURCES[self.class_name] * difference
        self._population = number

    @property
    def resources(self):
        return self._resources

    @resources.setter
    def resources(self, new_resources: dict | Arithmetic_Dict):
        for resource in RESOURCES:
            assert resource in new_resources
        self._resources = Arithmetic_Dict(new_resources)

    @property
    def optimal_resources(self):
        opt_res = OPTIMAL_RESOURCES[self.class_name] * self.population

        # Special case for nobles (optimal resources per capita not constant):
        if self.class_name == "nobles":
            opt_res["tools"] += \
                4 * self.parent.get_available_employees() * MINER_TOOL_USAGE

        return Arithmetic_Dict(opt_res)

    @property
    def missing_resources(self):
        return Arithmetic_Dict({
            resource: -amount if amount < 0 else 0
            for resource, amount
            in self.resources.items()
        })

    def grow_population(self, modifier: float):
        """
        Modifier specifies by how much to modify the population,
        negative means decrease in numbers.
        Modifier 0 means no change in population.
        Also consumes the class' resources, if they are needed for growth.
        """
        self.population *= (1 + modifier)

    def consume(self):
        """
        Removes resources the class consumed in the month.
        """
        self._resources -= Arithmetic_Dict({
            "food": FOOD_CONSUMPTION * self._population,
            "wood": WOOD_CONSUMPTION[self._parent.month] * self._population
        })

    def to_dict(self):
        data = {
            "population": self.population,
            "resources": dict(self.resources)
        }
        return data
