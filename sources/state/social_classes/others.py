from ...auxiliaries.constants import CLASSES
from .class_file import Class


class Others(Class):
    """
    Represents Other people of the country.
    They can work as peasants or in mines, on noble or government land.
    They do not own land and they can work as employees.
    """
    def class_name(self):
        return CLASSES[3]

    @property
    def employable(self):
        return True

    def produce(self):
        """
        Others do not produce anything by themselves.
        """
        pass
