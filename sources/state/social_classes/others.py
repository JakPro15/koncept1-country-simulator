from ...auxiliaries.constants import CLASSES
from .class_file import Class


class Others(Class):
    """
    Represents Other people of the country.
    They can work as peasants or in mines, when employed.
    They can work as employees.
    They promote to Peasants or Artisans.
    They do not demote.
    """
    @property
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
