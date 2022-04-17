from ...auxiliaries.constants import (
    LAND_TYPES,
    ARTISAN_IRON_USAGE,
    ARTISAN_TOOL_USAGE,
    ARTISAN_WOOD_USAGE,
    TOOLS_PRODUCTION
)
from ...auxiliaries.arithmetic_dict import Arithmetic_Dict
from .class_file import Class


class Artisans(Class):
    """
    Represents the Artisans of the country.
    Artisans use wood and iron to make tools.
    They do not own land and they cannot work as employees.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_name = "artisans"

    @staticmethod
    def create_from_dict(parent, data):
        population = data["population"]
        resources = data["resources"]
        land = data["land"]
        return Artisans(parent, population, resources, land)

    @property
    def land(self):
        return self._land.copy()

    @land.setter
    def land(self, new_land: Arithmetic_Dict):
        for land_type in LAND_TYPES:
            assert land_type in new_land
            assert new_land[land_type] == 0
        self._land = Arithmetic_Dict(new_land)

    @property
    def class_overpopulation(self):
        overpop = 0
        if self._resources["wood"] < 0:
            overpop = max(overpop, -self._resources["wood"] / 2)
        if self._resources["iron"] < 0:
            overpop = max(overpop, -self._resources["iron"] / 2)
        if self._resources["tools"] < 0:
            overpop = max(overpop, -self._resources["tools"] / 3)
        return overpop

    def _add_population(self, number: int):
        """
        Adds new artisans to the class. Does not modify _population, only
        handles the initiation resources.
        """
        self._resources["wood"] -= 2 * number
        self._resources["iron"] -= 2 * number
        self._resources["tools"] -= 3 * number

    def produce(self):
        """
        Adds resources the class produced in the current month.
        """
        artisans = self._population

        produced = Arithmetic_Dict({
            "tools": TOOLS_PRODUCTION * artisans
        })
        used = Arithmetic_Dict({
            "wood": TOOLS_PRODUCTION * artisans * ARTISAN_WOOD_USAGE,
            "iron": TOOLS_PRODUCTION * artisans * ARTISAN_IRON_USAGE,
            "tools": ARTISAN_TOOL_USAGE * artisans
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
            self._resources["wood"] += -2 * number
            self._resources["iron"] += -1 * number
            self._resources["tools"] += -3 * number
