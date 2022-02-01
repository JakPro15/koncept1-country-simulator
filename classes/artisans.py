from .classfile import Class
from .constants import (
    ARTISAN_IRON_USAGE,
    ARTISAN_TOOL_USAGE,
    ARTISAN_WOOD_USAGE,
    TOOLS_PRODUCTION
)
from math import ceil


class Artisans(Class):
    def _add_population(self, number: int):
        """
        Adds new artisans to the class. Does not modify _population, only
        handles the initiation resources.
        """
        self.resources["wood"] -= 2 * number
        self.resources["tools"] -= 3 * number
        resources = {"tools", "wood"}
        for resource in resources:
            if self.resources[resource] < 0:
                self.class_overpopulation = \
                    max(self.class_overpopulation,
                        ceil(self.resources[resource] / 3))

    def grow_population(self, modifier: float):
        """
        Modifier specifies by how much to modify the population,
        negative means decrease in numbers.
        Modifier 0 means no change in population.
        Also consumes the class' resources, if they are needed for growth.
        """
        grown = super().grow_population(modifier)
        self._add_population(grown)

    @staticmethod
    def optimal_resources_per_capita(month: str):
        """
        Food needed: enough to survive till harvest, plus three months
        Wood needed: yearly consumption + 1 (3 needed for new peasant)
        Iron needed: none
        Stone needed: none
        Tools needed: enough to work half a year + 1 (3 needed for new peasant)
        """
        optimal_resources = super().optimal_resources_per_capita(month)
        optimal_resources["wood"] += 0.5
        optimal_resources["tools"] += ARTISAN_TOOL_USAGE * 6 + 1
        return optimal_resources

    def _get_working_artisans(self):
        """
        Returns the number of fully working artisans.
        """
        wood_available = self.resources["wood"] / ARTISAN_WOOD_USAGE
        iron_available = self.resources["iron"] / ARTISAN_IRON_USAGE
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
        self.resources["wood"] -= \
            TOOLS_PRODUCTION * artisans * ARTISAN_WOOD_USAGE
        self.resources["iron"] -= \
            TOOLS_PRODUCTION * artisans * ARTISAN_IRON_USAGE
        self.resources["tools"] += \
            (TOOLS_PRODUCTION - ARTISAN_TOOL_USAGE) * artisans

    def move_population(self, number: int, demotion: bool):
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
            self.resources["wood"] += 2 * number
            self.resources["tools"] += 3 * number
