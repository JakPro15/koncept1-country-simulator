from ...auxiliaries.constants import CLASSES
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
    def class_name(self):
        return CLASSES[0]

    def produce(self):
        """
        Nobles do not produce anything by themselves.
        """
        pass
