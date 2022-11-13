from ...auxiliaries.enums import Class_Name
from .class_file import Class


class Others(Class):
    """
    Represents Other people of the country.
    They can work as employees.
    They promote to Peasants or Artisans.
    They do not demote.
    """
    @property
    def class_name(self) -> Class_Name:
        return Class_Name.others

    @property
    def employable(self) -> bool:
        return True

    def produce(self) -> None:
        """
        Others do not produce anything by themselves.
        """

    def recruitment_happiness(self, recruited: float) -> float:
        """
        Returns the change in happiness of the social class from which a given
        number of people was recruited. Should be called before the
        recruitment takes place (before population changes).
        """
        percent_recruited = 100 * recruited / self.population
        return -0.05 * percent_recruited ** 2 + 0.5 * percent_recruited
