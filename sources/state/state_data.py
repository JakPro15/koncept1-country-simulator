from ..auxiliaries.constants import (
    AVG_FOOD_PRODUCTION,
    FOOD_RATIOS,
    MAX_PRICES,
    MINER_TOOL_USAGE,
    NOBLES_CAP,
    DEFAULT_GROWTH_FACTOR,
    DEFAULT_PRICES,
    EMPTY_RESOURCES,
    FOOD_CONSUMPTION,
    FREEZING_MORTALITY,
    INBUILT_RESOURCES,
    INCREASE_PRICE_FACTOR,
    MONTHS,
    STARVATION_MORTALITY,
    WOOD_CONSUMPTION,
    IRON_PRODUCTION,
    STONE_PRODUCTION,
    OTHERS_WAGE,
    ARTISAN_IRON_USAGE,
    ARTISAN_TOOL_USAGE,
    ARTISAN_WOOD_USAGE,
    TOOLS_PRODUCTION,
    PEASANT_TOOL_USAGE,
    WOOD_PRODUCTION,
    WORKER_LAND_USAGE,
    TAX_RATES
)
from ..auxiliaries.arithmetic_dict import Arithmetic_Dict
from .social_classes.class_file import Class
from .social_classes.nobles import Nobles
from .social_classes.artisans import Artisans
from .social_classes.peasants import Peasants
from .social_classes.others import Others
from .government import Government
from .market import Market
from math import isinf, log


class EveryoneDeadError(Exception):
    pass


class InvalidYearChangeError(Exception):
    pass


class InvalidClassesListError(Exception):
    pass


class MathTmFailure(Exception):
    pass


class State_Modifiers:
    """
    Stores the modifiers defining how the State works. Can be changed
    mid-game by the player's actions.
    They start out as constants from auxiliaries/constants.py.
    """
    def __init__(self, parent: "State_Data"):
        self.parent = parent

        self.miner_tool_usage = MINER_TOOL_USAGE
        self.iron_production = IRON_PRODUCTION
        self.stone_production = STONE_PRODUCTION
        self.others_wage = OTHERS_WAGE

        self.artisan_wood_usage = ARTISAN_WOOD_USAGE
        self.artisan_iron_usage = ARTISAN_IRON_USAGE
        self.artisan_tool_usage = ARTISAN_TOOL_USAGE
        self.tools_production = TOOLS_PRODUCTION

        self.peasant_tool_usage = PEASANT_TOOL_USAGE
        self.avg_food_production = AVG_FOOD_PRODUCTION

        self.wood_production = WOOD_PRODUCTION

        self.increase_price_factor = INCREASE_PRICE_FACTOR
        self.nobles_cap = NOBLES_CAP

        self.default_growth_factor = DEFAULT_GROWTH_FACTOR
        self.starvation_mortality = STARVATION_MORTALITY
        self.freezing_mortality = FREEZING_MORTALITY

        self.max_prices = DEFAULT_PRICES * MAX_PRICES

        self.worker_land_usage = WORKER_LAND_USAGE

        self.tax_rates = TAX_RATES

    @property
    def food_production(self):
        return FOOD_RATIOS * self.avg_food_production

    @property
    def optimal_resources(self):
        return {
            "nobles": Arithmetic_Dict({
                "food": 12 * FOOD_CONSUMPTION,
                "wood": sum(WOOD_CONSUMPTION.values()),
                "stone": 2 * INBUILT_RESOURCES["nobles"]["stone"],
                "iron": 0,
                "tools": 4 + (4 * self.parent.get_available_employees() /
                              self.parent.classes[0].population)
                if self.parent.classes[0].population > 0 else 4,
                "land": (self.worker_land_usage *
                         self.parent.get_available_employees() /
                         self.parent.classes[0].population)
                if self.parent.classes[0].population > 0 else 0,
            }),
            "artisans": Arithmetic_Dict({
                "food": 4 * FOOD_CONSUMPTION,
                "wood": sum(WOOD_CONSUMPTION.values()) / 3 +
                4 * self.artisan_wood_usage,
                "stone": 0,
                "iron": 20 * self.artisan_iron_usage,
                "tools": 4 * self.artisan_tool_usage,
                "land": 0
            }),
            "peasants": Arithmetic_Dict({
                "food": 4 * FOOD_CONSUMPTION,
                "wood": sum(WOOD_CONSUMPTION.values()) / 3,
                "stone": 0,
                "iron": 0,
                "tools": 4 * self.peasant_tool_usage,
                "land": 0.5 * self.worker_land_usage
            }),
            "others": Arithmetic_Dict({
                "food": 4 * FOOD_CONSUMPTION,
                "wood": sum(WOOD_CONSUMPTION.values()) / 3,
                "stone": 0,
                "iron": 0,
                "tools": 0,
                "land": 0
            }),
        }


class State_Data:
    """
    Represents the data of an entire state, including all its classes.
    Properties:
    month - the current month
    classes - social classes of the country
    government - government of the country's object
    _market - object executing trade within the country
    payments - employee payments from the last produce
    prices - last month's resource prices on the market
    """
    def __init__(self, starting_month: str = "January",
                 starting_year: int = 0):
        """
        Creates a State_Data object. Note that classes and government remain
        uninitialized and need to be manually set after the creation of the
        state.
        """
        self._year = starting_year
        self._month = starting_month
        self.payments = Arithmetic_Dict({
            "food": 0,
            "wood": 0,
            "iron": 0,
            "stone": 0,
            "tools": 0,
            "land": 0
        })
        self.prices = DEFAULT_PRICES.copy()
        self.sm = State_Modifiers(self)

        class Fake_Nobles:
            def __init__(self):
                self.population = 0
        self._classes = [Fake_Nobles()]
        self._government = None

    @property
    def month(self):
        return self._month

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, new_year: int):
        if new_year != self._year + 1:
            raise InvalidYearChangeError
        self._year = new_year

    @property
    def classes(self):
        return self._classes.copy()

    @classes.setter
    def classes(self, new_classes_list: "list[Class]"):
        if len(new_classes_list) != 4:
            raise InvalidClassesListError

        self._classes = new_classes_list.copy()
        if self.government is not None:
            self._create_market()

        # These are used for demotions
        self._classes[0].lower_class = self._classes[2]
        self._classes[1].lower_class = self._classes[3]
        self._classes[2].lower_class = self._classes[3]
        self._classes[3].lower_class = self._classes[3]

    @property
    def government(self):
        return self._government

    @government.setter
    def government(self, new_government: Government):
        self._government = new_government
        if len(self.classes) == 4:
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
        """
        Creates a market for the object. Needs classes and government to be
        initialized.
        """
        trading_objects = self.classes.copy()
        trading_objects.append(self.government)
        self._market = Market(trading_objects, self)

    def get_available_employees(self):
        """
        Returns the number of employees available to be hired this month.
        """
        employees = 0
        for social_class in self.classes:
            if social_class.employable:
                employees += social_class.population
        return employees

    @classmethod
    def from_dict(cls, data: dict):
        """
        Creates a State_Data object from the given dict.
        """
        state = cls(data["month"], data["year"])

        nobles = Nobles.from_dict(state, data["classes"]["nobles"])
        artisans = Artisans.from_dict(state, data["classes"]["artisans"])
        peasants = Peasants.from_dict(state, data["classes"]["peasants"])
        others = Others.from_dict(state, data["classes"]["others"])
        government = Government.from_dict(state, data["government"])
        classes_list = [nobles, artisans, peasants, others]

        state.classes = classes_list
        state.government = government
        state.prices = Arithmetic_Dict(data["prices"])

        return state

    def to_dict(self):
        """
        Returns a dict with the object's data. It's valid for from_dict
        function.
        """
        data = {
            "year": self.year,
            "month": self.month,
            "classes": {
                "nobles": self.classes[0].to_dict(),
                "artisans": self.classes[1].to_dict(),
                "peasants": self.classes[2].to_dict(),
                "others": self.classes[3].to_dict()
            },
            "government": self.government.to_dict(),
            "prices": self.prices
        }
        return data

    def _do_growth(self, debug=False):
        """
        Does the natural population growth for all classes.
        """
        factor = self.sm.default_growth_factor / 12
        for social_class in self.classes:
            old_pop = social_class.new_population
            social_class.grow_population(factor)
            if debug:
                print(f"Grown {social_class.new_population - old_pop} "
                      f"{social_class.class_name}")

    def _do_starvation(self, debug=False):
        """
        Does starvation and freezing to fix negative food and wood.
        Starving or freezing is marked with a bool attribute of the class.
        """
        for social_class in self.classes:
            old_pop = social_class.new_population

            missing_food = social_class.missing_resources["food"]
            starving_number = 0
            if missing_food > 0:
                starving_number = self.sm.starvation_mortality * missing_food \
                    / FOOD_CONSUMPTION

                food_zerofier = {
                    "food": 0,
                    "wood": 1,
                    "stone": 1,
                    "iron": 1,
                    "tools": 1,
                    "land": 1
                }
                social_class.new_resources *= food_zerofier
                social_class.starving = True
            else:
                social_class.starving = False

            missing_wood = social_class.missing_resources["wood"]
            freezing_number = 0
            if missing_wood > 0:
                freezing_number = self.sm.freezing_mortality * missing_wood \
                    / WOOD_CONSUMPTION[self.month]

                wood_zerofier = {
                    "food": 1,
                    "wood": 0,
                    "stone": 1,
                    "iron": 1,
                    "tools": 1,
                    "land": 1
                }
                social_class.new_resources *= wood_zerofier
                social_class.freezing = True
            else:
                social_class.freezing = False

            if starving_number + freezing_number < social_class.new_population:
                social_class.new_population -= (
                    starving_number + freezing_number
                )
            else:
                social_class.new_population = 0

            if debug:
                print(f"Starved {old_pop - social_class.new_population} "
                      f"{social_class.class_name}")

    def _do_payments(self):
        """
        Moves the payments into Others' pockets.
        """
        self.classes[3].new_resources += self.payments
        self.payments = EMPTY_RESOURCES.copy()

    def _do_demotions(self, debug=False):
        """
        Does demotions to fix as many negative resources as possible.
        """
        for social_class in self.classes:
            lower_class = social_class.lower_class
            lower_name = lower_class.class_name

            moved_pop = min(
                social_class.class_overpopulation, social_class.new_population
            )
            moved_res = INBUILT_RESOURCES[lower_name] * moved_pop

            social_class.new_resources -= moved_res
            lower_class.new_resources += moved_res
            social_class.new_population -= moved_pop
            lower_class.new_population += moved_pop
            if moved_pop > 0:
                social_class.demoted_from = True
                lower_class.demoted_to = True
            else:
                social_class.demoted_from = False
                lower_class.demoted_to = False

            if debug:
                print(f"Demoted {moved_pop} {social_class.class_name}")

    def _secure_classes(self, flush=True):
        """
        Secures and flushes (if needed) all classes.
        """
        for social_class in self.classes:
            social_class.handle_negative_resources()
            if flush:
                social_class.handle_empty_class()
        self.government.handle_negative_resources()
        self.government.flush()

    @staticmethod
    def _promotion_math(from_wealth, from_pop, increase_price):
        """
        Calculates how many of the class will be promoted.
        """
        if not isinf(increase_price):
            avg_wealth = from_wealth / from_pop
            # Average relative to increase price
            avger_wealth = avg_wealth / increase_price
            # Math™
            part_promoted = max(min(log(
                avger_wealth - 1 if avger_wealth > 1 else 1, 100
            ), 1), 0)
            part_paid = (part_promoted - 1) ** 3 + 1

            transferred = part_promoted * from_pop

            # quick check if Math™ hasn't failed
            if part_paid * from_wealth < transferred * increase_price:
                raise MathTmFailure
        else:
            part_paid = 0
            transferred = 0

        return part_paid, transferred

    def _do_one_promotion(
        self, class_from: Class, class_to: Class, increase_price, debug=False
    ):
        """
        Does one promotion on the given classes.
        """
        from_wealth = sum((class_from.resources * self.prices).values())
        part_paid, transferred = State_Data._promotion_math(
            from_wealth, class_from.population, increase_price
        )

        class_to.new_resources += class_from.resources * part_paid
        class_from.new_resources -= class_from.resources * part_paid

        class_to.new_population += transferred
        class_from.new_population -= transferred

        if transferred > 0:
            class_from.promoted_from = True
            class_to.promoted_to = True

        if debug:
            print(f"Promoted {transferred} {class_from.class_name} to "
                  f"{class_to.class_name}")

    def _do_double_promotion(
        self, class_from: Class, class_to_1: Class, increase_price_1,
        class_to_2: Class, increase_price_2, debug=False
    ):
        """
        Does one promotion on the given classes.
        """
        from_wealth = sum((class_from.resources * self.prices).values())

        summed_price = (increase_price_1 + increase_price_2)
        increase_price = summed_price / 2

        part_paid, transferred = State_Data._promotion_math(
            from_wealth, class_from.population, increase_price
        )

        part_paid_1 = part_paid * increase_price_1 / summed_price
        part_paid_2 = part_paid * increase_price_2 / summed_price

        class_to_1.new_resources += class_from.resources * part_paid_1
        class_to_2.new_resources += class_from.resources * part_paid_2
        class_from.new_resources -= class_from.resources * part_paid

        class_to_1.new_population += transferred / 2
        class_to_2.new_population += transferred / 2
        class_from.new_population -= transferred

        if transferred > 0:
            class_from.promoted_from = True
            class_to_1.promoted_to = True
            class_to_2.promoted_to = True

        if debug:
            print(f"Double promoted {transferred} {class_from.class_name} to "
                  f"{class_to_1.class_name} and {class_to_2.class_name}")

    def _reset_promotion_flags(self):
        for social_class in self.classes:
            social_class.promoted_from = False
            social_class.promoted_to = False

    def _do_promotions(self, debug=False):
        """
        Does all the promotions of one month end.
        """
        self._reset_promotion_flags()

        nobles = self.classes[0]
        artisans = self.classes[1]
        peasants = self.classes[2]
        others = self.classes[3]

        if others.population > 0:
            if (not others.starving) and (not others.freezing):
                # Peasants and artisans (from others):
                increase_price_1 = self.sm.increase_price_factor * \
                    sum((INBUILT_RESOURCES["peasants"] * self.prices).values())
                increase_price_2 = self.sm.increase_price_factor * \
                    sum((INBUILT_RESOURCES["artisans"] * self.prices).values())
                self._do_double_promotion(others, peasants, increase_price_1,
                                          artisans, increase_price_2, debug)

        # Check the nobles' cap
        if nobles.population < self.sm.nobles_cap * \
                self.get_available_employees():
            # Increase price for nobles
            increase_price = self.sm.increase_price_factor * \
                sum((INBUILT_RESOURCES["nobles"] * self.prices).values())

            if peasants.population > 0:
                if (not peasants.starving) and (not peasants.freezing):
                    # Nobles (from peasants):
                    self._do_one_promotion(
                        peasants, nobles, increase_price, debug
                    )

            if artisans.population > 0:
                if (not artisans.starving) and (not artisans.freezing):
                    # Nobles (from artisans):
                    self._do_one_promotion(
                        artisans, nobles, increase_price, debug
                    )

    def _do_personal_taxes(self, populations, net_worths):
        """
        Siphons part of the resources of each class into the government
        based on its population, as defined by the tax_rates constant.
        """
        flat_taxes = self.sm.tax_rates["personal"] * populations
        rel_taxes = flat_taxes / net_worths
        self._do_tax(rel_taxes)

    def _do_property_taxes(self):
        """
        Siphons part of the resources of each class into the government
        based on its net worth, as defined by the tax_rates constant.
        """
        rel_taxes = self.sm.tax_rates["property"]
        self._do_tax(rel_taxes)

    def _do_income_taxes(self, net_worths_change, net_worths):
        """
        Siphons part of the resources of each class into the government
        based on its net worth increase, as defined by the tax_rates constant.
        """
        flat_taxes = self.sm.tax_rates["income"] * net_worths_change
        rel_taxes = flat_taxes / net_worths
        self._do_tax(rel_taxes)

    def _do_tax(self, rel_taxes):
        """
        Siphons the given parts of resources from classes to the government.
        """
        rel_taxes = {
            class_name: min(tax, 1)
            for class_name, tax
            in rel_taxes.items()
        }
        for social_class in self.classes:
            tax_rate = rel_taxes[social_class.class_name]
            self.government.new_resources += \
                social_class.new_resources * tax_rate
            social_class.new_resources *= (1 - tax_rate)

    def do_month(self, debug=False):
        """
        Does all the needed calculations and changes to end the month and move
        on to the next. Returns a dict with data from the month.
        """
        if debug:
            print(f"Ending month {self.month} {self.year}")
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
            "others": self.classes[3].resources,
            "government": self.government.resources
        }
        old_population = {
            "nobles": self.classes[0].population,
            "artisans": self.classes[1].population,
            "peasants": self.classes[2].population,
            "others": self.classes[3].population
        }
        old_net_worths = Arithmetic_Dict({
            "nobles": self.classes[0].net_worth,
            "artisans": self.classes[1].net_worth,
            "peasants": self.classes[2].net_worth,
            "others": self.classes[3].net_worth
        })

        # Create returned dict
        month_data = {
            "year": self.year,
            "month": self.month
        }

        # First: growth - resources might become negative
        self._do_growth(debug)

        # Second: production
        for social_class in self.classes:
            social_class.produce()
        self._do_payments()

        # Third: consumption
        for social_class in self.classes:
            social_class.consume()

        # Fourth: demotions - should fix all except food and some wood
        self._do_demotions(debug)
        self._secure_classes(flush=False)

        # Fifth: starvation - should fix all remaining resources
        self._do_starvation(debug)

        # Sixth: security and flushing
        self._secure_classes()

        # Seventh: promotions
        self._do_promotions(debug)  # Might make resources negative
        self._do_demotions(debug)  # Fix resources again

        # Eighth: trade
        self._market.do_trade()
        self.prices = self._market.prices
        month_data["prices"] = self.prices

        # Ninth: taxes
        populations = {
            "nobles": self.classes[0].population,
            "artisans": self.classes[1].population,
            "peasants": self.classes[2].population,
            "others": self.classes[3].population
        }
        net_worths = Arithmetic_Dict({
            "nobles": self.classes[0].net_worth,
            "artisans": self.classes[1].net_worth,
            "peasants": self.classes[2].net_worth,
            "others": self.classes[3].net_worth
        })
        self._do_personal_taxes(populations, net_worths)
        self._do_property_taxes()
        net_worths_change = net_worths - old_net_worths
        self._do_income_taxes(net_worths_change, net_worths)

        # Tenth: calculations done - advance to the next month
        self._secure_classes()
        self._advance_month()

        # Eleventh: return the necessary data
        month_data["resources_after"] = {
            "nobles": self.classes[0].resources +
            (INBUILT_RESOURCES["nobles"] * self.classes[0].population),
            "artisans": self.classes[1].resources +
            (INBUILT_RESOURCES["artisans"] * self.classes[1].population),
            "peasants": self.classes[2].resources +
            (INBUILT_RESOURCES["peasants"] * self.classes[2].population),
            "others": self.classes[3].resources +
            (INBUILT_RESOURCES["others"] * self.classes[3].population),
            "government": self.government.resources
        }
        month_data["population_after"] = {
            "nobles": self.classes[0].population,
            "artisans": self.classes[1].population,
            "peasants": self.classes[2].population,
            "others": self.classes[3].population
        }
        month_data["resources_change"] = {
            social_class: dict(values_dict - old_resources[social_class])
            for social_class, values_dict
            in month_data["resources_after"].items()
        }
        month_data["population_change"] = dict(
            Arithmetic_Dict(month_data["population_after"]) - old_population
        )
        return month_data

    def execute_commands(self, commands: list[str]):
        """
        Executes the given commands.
        Format:
        <command> <arguments>
        """
        for line in commands:
            command = line.split(' ')
            if command[0] == "next":
                amount = int(command[1])
                for _ in range(amount):
                    self.do_month()
