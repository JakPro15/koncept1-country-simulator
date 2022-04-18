from ...auxiliaries.constants import (
    EMPTY_RESOURCES,
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

    @staticmethod
    @property
    def class_name():
        """
        Returns the name of the class as a string.
        Should never be used on the base Class, only on derived classes.
        """
        return "base class"

    @property
    def employable(self):
        return False

    @property
    def population(self):
        return self._population

    @population.setter
    def population(self, number):
        """
        Does not modify the actual population, saves the changes in temporary
        _new_population. Use flush() to confirm the changes.
        """
        assert number >= 0
        difference = number - self._new_population
        self.resources -= INBUILT_RESOURCES[self.class_name] * difference
        self._new_population = number

    @property
    def resources(self):
        return self._resources

    @resources.setter
    def resources(self, new_resources: dict | Arithmetic_Dict):
        """
        Does not modify the actual resources, saves the changes in temporary
        _new_resources. Use flush() to confirm the changes.
        """
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
        """
        Returns the resources the class has negative.
        WARNING: Uses the temporary _new_resources, not resources itself.
        """
        return Arithmetic_Dict({
            resource: -amount if amount < 0 else 0
            for resource, amount
            in self._new_resources.items()
        })

    @property
    def class_overpopulation(self):
        """
        Returns how many of the class need to be demoted to remove negative
        resources.
        """
        overpops = []
        for res_name, value in self.missing_resources.items():
            res = INBUILT_RESOURCES[self.class_name][res_name]
            res -= \
                INBUILT_RESOURCES[self.lower_class_type.class_name][res_name]
            if res > 0:
                overpops.append(value / res)
        return max(overpops.values())

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
        """
        Creates a social class object from the given dict.
        """
        return cls(parent, data["population"], data["resources"])

    def handle_empty_class(self):
        """
        Makes classes with pop < 0.5 effectively empty.
        WARNING: Flushes the class.
        """
        self.flush()
        if self.is_temp:
            if self.population + self.temp["population"] < 0.5:
                # Put all pop and res into temp
                self.temp["population"] += self.population
                self.temp["resources"] += self.resources
                self.population = 0
                self.resources = EMPTY_RESOURCES
            else:
                # Untemporarify the class
                self.temp["resources"] += self.resources
                self.population += self.temp["population"]
                self.resources = self.temp["resources"]
                self.is_temp = False
                self.temp = \
                    {"population": 0, "resources": EMPTY_RESOURCES}
        elif self.population < 0.5:
            # Make the class empty, save pop and res into temp
            self.is_temp = True
            self.temp["population"] = self.population
            self.temp["resources"] = self.resources
            self.population = 0
            self.resources = EMPTY_RESOURCES
        self.flush()

    def handle_negative_resources(self):
        """
        Handles minimal negative resources resulting from floating-point
        rounding errors.
        """
        for resource in self._new_resources:
            if self._new_resources[resource] < 0 and \
                 abs(self._new_resources[resource]) < 0.001:
                self._new_resources[resource] = 0

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
