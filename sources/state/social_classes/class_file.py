from ...auxiliaries.constants import (
    FOOD_CONSUMPTION,
    INBUILT_RESOURCES,
    MONTHS,
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
    optimal_resources - how much resources the class wants to own
    missing_resources - how much resources the class needs to own to not die
    class_overpopulation - how many of the class need to be demoted because of
                           no resources
    """
    def __init__(self, parent, population: int,
                 resources: dict = None):
        self.parent = parent
        self.population = population
        if resources is None:
            self.resources = {
                resource: 0 for resource in RESOURCES
            }
        else:
            self.resources = resources

        self._new_population = self.population
        self._new_resources = self.resources

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        assert new_parent.month in MONTHS
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
        difference = number - self._new_population
        self.resources -= INBUILT_RESOURCES[self.class_name] * difference
        self._new_population = number

    @property
    def resources(self):
        return self._resources

    @resources.setter
    def resources(self, new_resources: dict | Arithmetic_Dict):
        for resource in RESOURCES:
            assert resource in new_resources
        self._new_resources = Arithmetic_Dict(new_resources)

    @property
    def optimal_resources(self):
        opt_res = OPTIMAL_RESOURCES[self.class_name] * self.population

        # Special case for nobles (optimal resources per capita not constant):
        if self.class_name == "nobles":
            opt_res["tools"] += 4 * self.parent.get_available_employees()

        return Arithmetic_Dict(opt_res)

    @property
    def missing_resources(self):
        return Arithmetic_Dict({
            resource: -amount if amount < 0 else 0
            for resource, amount
            in self.resources.items()
        })

    @property
    def class_overpopulation(self):
        overpops = {}
        for res_name, value in self.missing_resources.items():
            res = INBUILT_RESOURCES[self.class_name][res_name]
            if res > 0:
                overpops[res_name] = value / res
        return max(INBUILT_RESOURCES[self.class_name].values())

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
        self.resources -= Arithmetic_Dict({
            "food": FOOD_CONSUMPTION * self.population,
            "wood": WOOD_CONSUMPTION[self.parent.month] * self.population
        })

    def to_dict(self):
        data = {
            "population": self.population,
            "resources": dict(self.resources)
        }
        return data

    @classmethod
    def from_dict(cls, parent, data):
        return cls(parent, data["population"], data["resources"])

    def flush(self):
        """
        To be run after multifunctional calculations - to save the temporary
        changes, after checking validity.
        """
        assert self._new_population >= 0
        assert set(self._new_resources.keys()) == set(RESOURCES)
        for value in self._new_resources.values():
            assert value >= 0

        self._population = self._new_population
        self._resources = self._new_resources
