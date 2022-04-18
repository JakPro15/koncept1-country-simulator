from ...auxiliaries.constants import (
    CLASSES,
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
    They cannot work as employees.
    They promote to Nobles.
    They demote to Others.
    """
    @staticmethod
    @property
    def class_name():
        return CLASSES[1]

    def produce(self):
        """
        Adds resources the class produced in the current month.
        """
        produced = Arithmetic_Dict({
            "tools": TOOLS_PRODUCTION * self.population
        })
        used = Arithmetic_Dict({
            "wood": ARTISAN_WOOD_USAGE * self.population,
            "iron": ARTISAN_IRON_USAGE * self.population,
            "tools": ARTISAN_TOOL_USAGE * self.population
        })

        self.resources -= used
        self.resources += produced
