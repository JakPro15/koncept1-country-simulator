from ...auxiliaries.constants import (
    CLASSES
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
    @property
    def class_name(self):
        return CLASSES[1]

    def produce(self):
        """
        Adds resources the class produced in the current month.
        """
        produced = Arithmetic_Dict({
            "tools": self.parent.sm.tools_production * self.population
        })
        used = Arithmetic_Dict({
            "wood": self.parent.sm.artisan_wood_usage * self.population,
            "iron": self.parent.sm.artisan_iron_usage * self.population,
            "tools": self.parent.sm.artisan_tool_usage * self.population
        })

        self.new_resources -= used
        self.new_resources += produced
