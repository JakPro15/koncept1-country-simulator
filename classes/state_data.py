from .constants import MONTHS
from .class_file import Class
from .nobles import Nobles
from .artisans import Artisans
from .peasants import Peasants
from .others import Others
from .market import Market


class State_Data:
    """
    Represents the data of an entire state, including all its classes.
    Properties:
    month - the current month
    classes - social classes of the country
    _market - Market of the country
    payments - employee payments from the last produce
    prices - last month's resource prices on the market
    """
    def __init__(self, starting_month: str = "January"):
        self.month = starting_month
        self.payments = {
            "food": 0,
            "wood": 0,
            "iron": 0,
            "stone": 0,
            "tools": 0
        }
        self.prices = {
            "food": 0,
            "wood": 0,
            "iron": 0,
            "stone": 0,
            "tools": 0
        }

    @property
    def month(self):
        return self._month

    @month.setter
    def month(self, new_month: str):
        assert new_month in MONTHS
        self._month = new_month

    @property
    def classes(self):
        return self._classes.copy()

    @classes.setter
    def classes(self, new_classes_list: "list[Class]"):
        assert isinstance(new_classes_list[0], Nobles)
        assert isinstance(new_classes_list[1], Artisans)
        assert isinstance(new_classes_list[2], Peasants)
        assert isinstance(new_classes_list[3], Others)
        self._classes = new_classes_list.copy()

    def _advance_month(self):
        months_moved = MONTHS[1:] + [MONTHS[0]]
        next_months = {
            month1: month2
            for month1, month2
            in zip(MONTHS, months_moved)}
        self._month = next_months[self.month]

    def _create_market(self):
        self._market = Market(self.classes)

    def get_available_employees(self):
        pass

    def from_dict(self, data: dict):
        self.month = data["month"]

        nobles = Nobles.create_from_dict(self, data["classes"]["nobles"])
        artisans = Artisans.create_from_dict(self, data["classes"]["artisans"])
        peasants = Peasants.create_from_dict(self, data["classes"]["peasants"])
        others = Others.create_from_dict(self, data["classes"]["others"])
        classes_list = [nobles, artisans, peasants, others]
        self.classes = classes_list

        self._create_market()

        self.prices = data["prices"]

    def to_dict(self):
        data = {
            "month": self.month,
            "classes": {
                "nobles": self.classes[0].to_dict(),
                "artisans": self.classes[1].to_dict(),
                "peasants": self.classes[2].to_dict(),
                "others": self.classes[3].to_dict()
            },
            "prices": self.prices
        }
        return data
