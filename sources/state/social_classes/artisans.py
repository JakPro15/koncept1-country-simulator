from ...auxiliaries.enums import Class_Name, Resource
from ...auxiliaries.resources import Resources
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
    def class_name(self) -> Class_Name:
        return Class_Name.artisans

    def produce(self) -> None:
        """
        Adds resources the class produced in the current month.
        """
        produced = Resources({
            Resource.tools: self.parent.sm.tools_production * self.population
        })
        used = Resources({
            Resource.wood: self.parent.sm.artisan_wood_usage * self.population,
            Resource.iron: self.parent.sm.artisan_iron_usage * self.population,
            Resource.tools: self.parent.sm.artisan_tool_usage * self.population
        })

        self.resources -= used
        self.resources += produced

    def recruitment_happiness(self, recruited: float) -> float:
        """
        Returns the change in happiness of the social class from which a given
        number of people was recruited. Should be called before the
        recruitment takes place (before population changes).
        """
        part_recruited = recruited / self.population
        return -part_recruited * 100
