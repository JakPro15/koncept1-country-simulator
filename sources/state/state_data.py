from ..auxiliaries.constants import (
    DEFAULT_GROWTH_FACTOR,
    DEFAULT_PRICES,
    EMPTY_RESOURCES,
    FREEZING_MORTALITY,
    INBUILT_RESOURCES,
    INCREASE_PRICE_FACTOR,
    MONTHS,
    STARVATION_MORTALITY,
    WOOD_CONSUMPTION
)
from ..auxiliaries.arithmetic_dict import Arithmetic_Dict
from .social_classes.class_file import Class
from .social_classes.nobles import Nobles
from .social_classes.artisans import Artisans
from .social_classes.peasants import Peasants
from .social_classes.others import Others
from .market import Market


class EveryoneDeadError(Exception):
    pass


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
        self.payments = Arithmetic_Dict({
            "food": 0,
            "wood": 0,
            "iron": 0,
            "stone": 0,
            "tools": 0
        })
        self.prices = DEFAULT_PRICES.copy()

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

        # Create some more attributes for the classes
        # These are used for demotions
        self._classes[0].lower_class = self._classes[2]
        self._classes[1].lower_class = self._classes[3]
        self._classes[2].lower_class = self._classes[3]
        self._classes[3].lower_class = self._classes[3]
        # These are used for securing almost-empty classes
        for social_class in self._classes:
            social_class.is_temp = False
            social_class.temp = \
                {"population": 0, "resources": EMPTY_RESOURCES.copy()}
        # These are used in promotions
            social_class.starving = False
            social_class.freezing = False

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

        nobles = Nobles.from_dict(self, data["classes"]["nobles"])
        artisans = Artisans.from_dict(self, data["classes"]["artisans"])
        peasants = Peasants.from_dict(self, data["classes"]["peasants"])
        others = Others.from_dict(self, data["classes"]["others"])
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

    def _do_growth(self):
        """
        Does the natural population growth for all classes.
        """
        factor = DEFAULT_GROWTH_FACTOR / 12
        for social_class in self.classes:
            social_class.grow_population(factor)

    def _do_starvation(self):
        """
        Does starvation and freezing to fix negative food and wood.
        Starving or freezing is marked with a bool attribute of the class.
        """
        modifiers = set()
        for social_class in self.classes:
            missing_food = social_class.missing_resources["food"]
            starving_number = 0
            if missing_food > 0:
                starving_number = STARVATION_MORTALITY * missing_food \
                    / social_class.population

                social_class.resources["food"] = 0
                modifiers.add("Starving")
                social_class.starving = True
            else:
                social_class.starving = False

            missing_wood = social_class.missing_resources["wood"]
            freezing_number = 0
            if missing_wood > 0:
                freezing_number = FREEZING_MORTALITY * missing_wood \
                    / WOOD_CONSUMPTION[self.month]

                social_class.resources["wood"] = 0
                modifiers.add("Freezing")
                social_class.freezing = True
            else:
                social_class.freezing = False

            social_class.population -= (starving_number + freezing_number)
        return modifiers

    def _do_payments(self):
        """
        Moves the payments into Others' pockets.
        """
        self.classes[3].resources += self.payments
        for resource in self.payments:
            self.payments[resource] = 0

    def _do_demotions(self):
        """
        Does demotions to fix as many negative resources as possible.
        """
        for social_class in self.classes:
            lower_class = social_class.lower_class
            lower_name = lower_class.class_name

            moved_pop = \
                min(social_class.class_overpopulation, social_class.population)
            moved_res = INBUILT_RESOURCES[lower_name] * moved_pop

            social_class.resources -= moved_res
            lower_class.resources += moved_res
            social_class.population -= moved_pop
            lower_class.population += moved_pop

    def _secure_classes(self):
        """
        Secures and flushes all classes.
        """
        for social_class in self.classes:
            social_class.handle_negative_resources()
            social_class.handle_empty_class()

    def _do_one_promotion(self, class_from, class_to, increase_price):
        """
        Does one promoton on the given classes.
        """
        from_wealth = sum((class_from.resources * self.prices).values())
        if from_wealth < increase_price / 10:
            return

        paid = min(
            class_from.population * increase_price, from_wealth / 5
        )
        part_paid = paid / from_wealth
        class_to.resources += class_from.resources * part_paid
        class_from.resources -= class_from.resources * part_paid

        transferred = paid / increase_price
        class_to.population += transferred
        class_from.population -= transferred

    def _do_promotions(self):
        """
        Does all the promotions of one month end.
        """
        nobles = self.classes[0]
        artisans = self.classes[1]
        peasants = self.classes[2]
        others = self.classes[3]

        if not(others.starving) and (not others.freezing):
            # Peasants:
            increase_price = INCREASE_PRICE_FACTOR * \
                (3 * self.prices["wood"] + 3 * self.prices["tools"])
            self._do_one_promotion(others, peasants, increase_price)

            # Artisans:
            increase_price = INCREASE_PRICE_FACTOR * \
                (2 * self.prices["wood"] + 3 * self.prices["tools"])
            self._do_one_promotion(others, artisans, increase_price)

        # Modifiers for nobles
        increase_price = INCREASE_PRICE_FACTOR * (
            7 * self.prices["wood"] + 4 * self.prices["stone"] +
            1 * self.prices["tools"]
        )
        if not(peasants.starving) and (not peasants.freezing):
            # Nobles (from peasants):
            self._do_one_promotion(
                peasants, nobles, increase_price
            )

        if not(artisans.starving) and (not artisans.freezing) == 0:
            # Nobles (from artisans):
            self._do_one_promotion(
                artisans, nobles, increase_price
            )

    def do_month(self):
        """
        Does all the needed calculations and changes to end the month and move
        on to the next. Returns a dict with data from the month.
        """
        # Check for game over
        someone_alive = False
        for social_class in self.classes:
            if social_class.population > 0:
                someone_alive = True
        if not someone_alive:
            raise EveryoneDeadError

        # Save old resources to calculate the changes
        old_resources = {
            "nobles": self.classes[0].resources,
            "artisans": self.classes[1].resources,
            "peasants": self.classes[2].resources,
            "others": self.classes[3].resources
        }
        old_population = {
            "nobles": self.classes[0].population,
            "artisans": self.classes[1].population,
            "peasants": self.classes[2].population,
            "others": self.classes[3].population
        }

        # Create returned dict
        month_data = {
            "year": self.year,
            "month": self.month
        }

        # First: growth - resources might become negative
        self._do_growth()

        # Second: production
        for social_class in self.classes:
            social_class.produce()
        self._do_payments()

        # Third: consumption
        for social_class in self.classes:
            social_class.consume()

        # Fourth: demotions - should fix all except food and some wood
        self._do_demotions()

        # Fifth: starvation - should fix all remaining resources
        self._do_starvation()

        # Sixth: security and flushing
        self._secure_classes()

        # Seventh: promotions
        self._do_promotions()  # Might make resources negative again
        self._do_demotions()  # Fix resources again

        # Eighth: trade
        self._market.do_trade()
        self.prices = self._market.prices
        month_data["trade_prices"] = self.prices

        # Ninth: calculations done - advance to the next month
        self._advance_month()

        # Tenth: return the necessary data
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
        month_data["resources_change"] = \
            month_data["resources_after"] - old_resources
        month_data["population_change"] = \
            month_data["population_change"] - old_population
        return month_data

    def execute_commands(self, commands: list[str]):
        """
        Executes the given commands.
        Format:
        <command> <argument>
        """
        for line in commands:
            command = line.split(' ')
            if command[0] == "next":
                amount = int(command[1])
                for _ in range(amount):
                    self.do_month()
