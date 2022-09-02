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
