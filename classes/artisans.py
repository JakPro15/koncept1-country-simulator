from .constants import LAND_TYPES
from .class_file import Class
from .constants import (
    ARTISAN_IRON_USAGE,
    ARTISAN_TOOL_USAGE,
    ARTISAN_WOOD_USAGE,
    TOOLS_PRODUCTION
)
from math import ceil


class Artisans(Class):
    """
    Represents the Artisans of the country.
    Artisans use wood and iron to make tools.
    They do not own land and they cannot work as employees.
    """
    @property
    def land(self):
        return self._land.copy()

    @land.setter
    def land(self, new_land: dict):
        for land_type in LAND_TYPES:
            assert land_type in new_land
            assert new_land[land_type] == 0
        self._land = new_land.copy()

    @property
    def class_overpopulation(self):
        overpop = 0
        if self._resources["wood"] < 0:
            overpop = max(overpop, ceil(-self._resources["wood"] / 2))
        if self._resources["tools"] < 0:
            overpop = max(overpop, ceil(-self._resources["tools"] / 3))
        return overpop

    def _add_population(self, number: int):
        """
        Adds new artisans to the class. Does not modify _population, only
        handles the initiation resources.
        """
        self._resources["wood"] -= 2 * number
        self._resources["tools"] -= 3 * number

    def optimal_resources_per_capita(self):
        """
        Food needed: four months' consumption
        Wood needed: yearly consumption + 1 (3 needed for new artisan)
        Iron needed: none
        Stone needed: none
        Tools needed: enough to work half a year + 1 (3 needed for new artisan)
        """
        optimal_resources = super().optimal_resources_per_capita()
        optimal_resources["wood"] += ARTISAN_WOOD_USAGE * 4 + 0.5
        optimal_resources["iron"] += ARTISAN_IRON_USAGE * 4
        optimal_resources["tools"] += ARTISAN_TOOL_USAGE * 4 + 1
        return optimal_resources

    def _get_working_artisans(self):
        """
        Returns the number of fully working artisans.
        """
        wood_available = self._resources["wood"] / ARTISAN_WOOD_USAGE
        iron_available = self._resources["iron"] / ARTISAN_IRON_USAGE
        working_artisans = min(
            wood_available,
            iron_available,
            self._population
        )
        return working_artisans

    def produce(self):
        """
        Adds resources the class produced in the current month.
        """
        artisans = self._get_working_artisans()
        self._resources["wood"] -= \
            TOOLS_PRODUCTION * artisans * ARTISAN_WOOD_USAGE
        self._resources["iron"] -= \
            TOOLS_PRODUCTION * artisans * ARTISAN_IRON_USAGE
        self._resources["tools"] += \
            (TOOLS_PRODUCTION - ARTISAN_TOOL_USAGE) * artisans

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
            self._resources["tools"] += -3 * number
