from .constants import (
    DEFAULT_GROWTH_FACTOR,
    FREEZING_MORTALITY,
    MONTHS,
    STARVATION_MORTALITY,
    WOOD_CONSUMPTION,
    INDEX_TO_CLASS_NAME
)
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
    log - whether to log the actions
    """
    def __init__(self, starting_month: str = "January",
                 starting_year: int = 0):
        self.year = starting_year
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
    def year(self):
        return self._year

    @year.setter
    def year(self, new_year: int):
        assert new_year >= 0
        self._year = new_year

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
        self._create_market()

    def _advance_month(self):
        months_moved = MONTHS[1:] + [MONTHS[0]]
        next_months = {
            month1: month2
            for month1, month2
            in zip(MONTHS, months_moved)}
        self._month = next_months[self.month]
        if self._month == "January":
            self.year += 1

    def _create_market(self):
        self._market = Market(self.classes)

    def get_available_employees(self):
        employees = 0
        for social_class in self.classes:
            if social_class.employable:
                employees += social_class.population
        return employees

    def from_dict(self, data: dict):
        self.year = data["year"]
        self.month = data["month"]

        nobles = Nobles.create_from_dict(self, data["classes"]["nobles"])
        artisans = Artisans.create_from_dict(self, data["classes"]["artisans"])
        peasants = Peasants.create_from_dict(self, data["classes"]["peasants"])
        others = Others.create_from_dict(self, data["classes"]["others"])
        classes_list = [nobles, artisans, peasants, others]
        self.classes = classes_list

        self.prices = data["prices"]

    def to_dict(self):
        data = {
            "year": self.year,
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

    def _grow_populations(self):
        modifiers = {}
        grown = {}
        for index, social_class in enumerate(self.classes):
            class_name = INDEX_TO_CLASS_NAME[index]
            modifiers[class_name] = {}
            modifiers[class_name]["Base"] = DEFAULT_GROWTH_FACTOR / 12

            missing_food = social_class.missing_resources["food"]
            if missing_food > 0:
                starving_part = missing_food / social_class.population
                modifiers[class_name]["Starving"] = \
                    -starving_part * STARVATION_MORTALITY
                social_class.resources["food"] = 0

            missing_wood = social_class.missing_resources["wood"]
            if missing_wood > 0:
                freezing_number = missing_wood / WOOD_CONSUMPTION[self.month]
                freezing_part = freezing_number / social_class.population
                modifiers[class_name]["Freezing"] = \
                    -freezing_part * FREEZING_MORTALITY
                social_class.resources["wood"] = 0

            total_modifier = sum(modifiers[class_name].values())
            grown[class_name] = social_class.grow_population(total_modifier)

        return modifiers, grown

    def _do_payments(self):
        for resource in self.payments:
            self.classes[3].resources[resource] += self.payments[resource]
            self.payments[resource] = 0

    def _do_demotions(self):
        nobles = self._classes[0]
        artisans = self._classes[1]
        peasants = self._classes[2]
        others = self._classes[3]

        nobles_moved = min(nobles.class_overpopulation, nobles.population)
        peasants.resources["wood"] += 3 * nobles_moved
        peasants.resources["tools"] += 3 * nobles_moved
        peasants.move_population(nobles_moved)
        nobles.move_population(-nobles_moved, demotion=True)

        artisans_moved = \
            min(artisans.class_overpopulation, artisans.population)
        others.move_population(artisans_moved)
        artisans.move_population(-artisans_moved, demotion=True)

        peasants_moved = \
            min(peasants.class_overpopulation, peasants.population)
        others.move_population(peasants_moved)
        peasants.move_population(-peasants_moved, demotion=True)

    @staticmethod
    def _handle_empty_class(social_class, lower_class):
        if social_class.population < 0.5:
            social_class.population = 0
            for resource in social_class.resources:
                if social_class.resources[resource] > 0:
                    lower_class.resources[resource] += \
                        social_class.resources[resource]
                social_class.resources[resource] = 0

    @staticmethod
    def _handle_negative_resources(social_class):
        for resource in social_class.resources:
            if social_class.resources[resource] < 0 and \
                 abs(social_class.resources[resource]) < 0.001:
                social_class.resources[resource] = 0

    def _secure_classes(self):
        nobles = self.classes[0]
        artisans = self.classes[1]
        peasants = self.classes[2]
        others = self.classes[3]
        self._handle_empty_class(nobles, peasants)
        self._handle_empty_class(artisans, others)
        self._handle_empty_class(peasants, others)
        self._handle_empty_class(others, others)
        for social_class in self.classes:
            self._handle_negative_resources(social_class)

    def do_month(self):
        month_data = {
            "year": self.year,
            "month": self.month,
            "produced": {},
            "used": {},
            "consumed": {},
            "resources_after": {}
        }

        for index, social_class in enumerate(self.classes):
            produced, used = social_class.produce()
            class_name = INDEX_TO_CLASS_NAME[index]
            month_data["produced"][class_name] = produced
            month_data["used"][class_name] = used

        self._do_payments()
        self._do_demotions()
        self._secure_classes()

        self._market.do_trade()
        self.prices = self._market.prices
        month_data["trade_prices"] = self.prices

        for index, social_class in enumerate(self.classes):
            consumed = social_class.consume()
            class_name = INDEX_TO_CLASS_NAME[index]
            month_data["consumed"][class_name] = consumed

        modifiers, grown = self._grow_populations()
        month_data["growth_modifiers"] = modifiers
        month_data["grown"] = grown
        self._do_demotions()
        self._secure_classes()

        self._advance_month()

        month_data["resources_after"] = {
            "nobles": self.classes[0].resources,
            "artisans": self.classes[1].resources,
            "peasants": self.classes[2].resources,
            "others": self.classes[3].resources
        }
        month_data["population_after"] = {
            "nobles": self.classes[0].population,
            "artisans": self.classes[1].population,
            "peasants": self.classes[2].population,
            "others": self.classes[3].population
        }
        return month_data

    def execute_commands(self, commands):
        for line in commands:
            command = line.split(' ')
            if command[0] == "next":
                amount = int(command[1])
                for _ in range(amount):
                    self.do_month()
