from ...auxiliaries.constants import (
    EMPTY_RESOURCES,
    FOOD_CONSUMPTION,
    INBUILT_RESOURCES,
    MONTHS,
    RESOURCES,
    WOOD_CONSUMPTION
)
from ...auxiliaries.arithmetic_dict import Arithmetic_Dict


class NegativeResourcesError(Exception):
    pass


class NegativePopulationError(Exception):
    pass


class InvalidParentError(Exception):
    pass


class InvalidResourcesDictError(Exception):
    pass


class Class:
    """
    Represents one social class of the country.
    Properties:
    parent - state this class is part of
    employable - whether the class can be hired as employees
    population - population of the class
    resources - dictionary containing info on the resources the class owns
    new_resources - dictionary containing current (temporary) info on the
                    resources the class owns
    real_resources - dictionary containing info on the resources the class
                     owns, including inbuilt resources
    optimal_resources - how much resources the class wants to own
    missing_resources - how much resources the class needs to own to not die
                        or get demoted
    class_overpopulation - how many of the class need to be demoted because of
                           no resources
    net_worth - monetary worth of the class' resources, based on the current
                prices in parent
    max_employees - how many employees can the class employ
    """
    def __init__(self, parent, population: int,
                 resources: dict = None):
        """
        Creates an object of type Class or a derived class.
        Parent is the State_Data object this belongs to.
        """
        self.parent = parent
        if population < 0:
            self._population = 0
        else:
            self._population = population
        if resources is None:
            self._resources = Arithmetic_Dict({
                resource: 0 for resource in RESOURCES
            })
        else:
            if set(resources.keys()) != set(RESOURCES):
                raise InvalidResourcesDictError
            for value in resources.values():
                if value < 0:
                    raise NegativeResourcesError
            self._resources = Arithmetic_Dict(resources)

        self._new_population = self.population
        self._new_resources = self.resources.copy()

        self.is_temp = False
        self.temp = {"population": 0, "resources": EMPTY_RESOURCES.copy()}

        self.starving = False
        self.freezing = False
        self.demoted_from = False
        self.demoted_to = False
        self.promoted_from = False
        self.promoted_to = False

        self.happiness = 0
        self.happiness_plateau = 0

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        if not hasattr(new_parent, "month"):
            raise InvalidParentError
        if new_parent.month not in MONTHS:
            raise InvalidParentError
        self._parent = new_parent

    @property
    def class_name(self):
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

    @property
    def new_population(self):
        return self._new_population

    @new_population.setter
    def new_population(self, number):
        """
        Does not modify the actual population, saves the changes in temporary
        _new_population. Use flush() to confirm the changes.
        """
        if number < 0:
            raise NegativePopulationError
        difference = number - self._new_population
        self.new_resources -= INBUILT_RESOURCES[self.class_name] * difference
        self._new_population = number

    @property
    def resources(self):
        return self._resources.copy()

    @property
    def new_resources(self):
        return self._new_resources.copy()

    @new_resources.setter
    def new_resources(self, new_new_resources: dict | Arithmetic_Dict):
        """
        Does not modify the actual resources, saves the changes in temporary
        _new_resources. Use flush() to confirm the changes.
        """
        if set(new_new_resources.keys()) != set(RESOURCES):
            raise InvalidResourcesDictError
        self._new_resources = Arithmetic_Dict(new_new_resources.copy())

    @property
    def real_resources(self):
        return self.resources + (
            INBUILT_RESOURCES[self.class_name] * self.population
        )

    @property
    def optimal_resources(self):
        """
        Returns optimal resources dict for the given social class object, for
        trade purposes.
        """
        opt_res = \
            self.parent.sm.optimal_resources[self.class_name] * self.population

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
        Returns how many of the class need to be demoted to remove
        negative resources.
        """
        overpops = []
        for res_name, value in self.missing_resources.items():
            res = INBUILT_RESOURCES[self.class_name][res_name] - \
                INBUILT_RESOURCES[self.lower_class.class_name][res_name]
            if res > 0:
                overpops.append(value / res)

        if overpops:
            return max(overpops)
        else:
            return 0

    @property
    def net_worth(self):
        """
        Returns the monetary value of the class' resources, based on current
        prices in parent.
        """
        prices = self.parent.prices
        return sum([
            prices[res] * amount
            for res, amount
            in self.real_resources.items()
        ])

    @property
    def max_employees(self):
        land_owned = self.resources["land"] + \
            INBUILT_RESOURCES[self.class_name]["land"] * self.population
        return min(
            self.resources["tools"] / 3,
            land_owned / self.parent.sm.worker_land_usage,
        )

    def grow_population(self, modifier: float):
        """
        Modifier specifies by how much to modify the population,
        negative means decrease in numbers.
        Modifier 0 means no change in population.
        Also consumes the class' resources, if they are needed for growth.
        """
        self.new_population *= (1 + modifier)

    def consume(self):
        """
        Removes resources the class consumed in the month.
        """
        self.new_resources -= Arithmetic_Dict({
            "food": FOOD_CONSUMPTION * self.population,
            "wood": WOOD_CONSUMPTION[self.parent.month] * self.population
        })

    def to_dict(self):
        """
        Converts the social class object to a dict. Does not save temporary
        attributes (new_population and new_resources).
        """
        data = {
            "population": self.population,
            "resources": dict(self.resources),
            "happiness": self.happiness
        }
        return data

    @classmethod
    def from_dict(cls, parent, data):
        """
        Creates a social class object from the given dict.
        """
        new_class = cls(parent, data["population"], data["resources"])
        new_class.happiness = data.get("happiness", 0)
        return new_class

    def handle_empty_class(self):
        """
        Makes classes with pop < 0.5 effectively empty.
        Flushes the class.
        """
        self.flush()
        if self.is_temp:
            if self.population + self.temp["population"] < 0.5:
                # Put all pop and res into temp
                self.temp["population"] += self.population
                self.temp["resources"] += self.resources
                self.new_population = 0
                self.new_resources = EMPTY_RESOURCES.copy()
            else:
                # Untemporarify the class
                self.temp["resources"] += self.resources
                self.new_population += self.temp["population"]
                self.new_resources = self.temp["resources"]
                self.is_temp = False
                self.temp = \
                    {"population": 0, "resources": EMPTY_RESOURCES.copy()}
        elif self.population < 0.5:
            # Make the class empty, save pop and res into temp
            self.is_temp = True
            self.temp["population"] = self.population
            self.temp["resources"] = self.resources
            self.new_population = 0
            self.new_resources = EMPTY_RESOURCES.copy()
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
        if self._new_population < 0:
            raise NegativePopulationError
        if set(self._new_resources.keys()) != set(RESOURCES):
            raise InvalidResourcesDictError

        self.handle_negative_resources()
        for value in self._new_resources.values():
            if value < 0:
                raise NegativeResourcesError

        self._population = self._new_population
        self._resources = self._new_resources.copy()

    def decay_happiness(self):
        """
        Changes the happiness a bit towards zero. Changes are bigger the
        further happiness is from zero.
        """
        self.happiness -= self.happiness_plateau
        decay = min(0.2 * abs(self.happiness), abs(self.happiness))
        sign = -1 if self.happiness > 0 else 1
        self.happiness += sign * decay
        self.happiness += self.happiness_plateau

    def update_happiness_plateau(self):
        """
        Sets happiness plateau based on growth modifiers flags.
        """
        self.happiness_plateau = 0
        if self.starving:
            self.happiness_plateau -= 20
        if self.freezing:
            self.happiness_plateau -= 20
        if self.demoted_from:
            self.happiness_plateau -= 10
        if self.demoted_to:
            self.happiness_plateau -= 10
        if self.promoted_from:
            self.happiness_plateau += 10
        if self.promoted_to:
            self.happiness_plateau += 10

    @staticmethod
    def starvation_happiness(part_dead):
        """
        Returns the change in happiness of a social class whose given part
        died of starvation or freezing.
        """
        percent_dead = part_dead * 100
        return (percent_dead ** 2.5) / (percent_dead - 100.01) - percent_dead

    @staticmethod
    def resources_seized_happiness(net_worth_seized_per_capita):
        """
        Returns the change in happiness of a social class whose given part
        of resources was seized by the government.
        """
        return net_worth_seized_per_capita * 15
