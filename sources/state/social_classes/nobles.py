from ...auxiliaries.enums import Class_Name
from .class_file import Class


class Nobles(Class):
    """
    Represents the Nobles of the country.
    Nobles do not make anything.
    They cannot work as employees.
    They employ employable classes.
    They do not promote.
    They demote to Peasants.
    """
    @property
    def class_name(self) -> Class_Name:
        return Class_Name.nobles

    def produce(self) -> None:
        """
        Nobles do not produce anything by themselves.
        """
