from ...auxiliaries.constants import LAND_TYPES
from ...auxiliaries.arithmetic_dict import Arithmetic_Dict
from .class_file import Class


class Others(Class):
    """
    Represents Other people of the country.
    They can work as peasants or in mines, on noble or government land.
    They do not own land and they can work as employees.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_name = "others"

    @staticmethod
    def create_from_dict(parent, data):
        population = data["population"]
        resources = data["resources"]
        land = data["land"]
        return Others(parent, population, resources, land)

    @property
    def employable(self):
        return True

    @property
    def land(self):
        return self._land.copy()

    @land.setter
    def land(self, new_land: dict):
        for land_type in LAND_TYPES:
            assert land_type in new_land
            assert new_land[land_type] == 0
        self._land = Arithmetic_Dict(new_land)

    @property
    def class_overpopulation(self):
        return 0

    def _add_population(self, number: int):
        """
        Adds new others to the class. Does not modify _population, only
        handles the initiation resources.
        """
        pass

    def produce(self):
        """
        Adds resources the class produced in the current month.
        """
        produced = Arithmetic_Dict({})
        used = Arithmetic_Dict({})

        return produced, used
