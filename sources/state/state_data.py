from ..auxiliaries.constants import (
    BRIGAND_STRENGTH,
    CLASSES,
    DEFAULT_PRICES,
    FOOD_CONSUMPTION,
    INBUILT_RESOURCES,
    MONTHS,
    REBELLION_THRESHOLD,
    WOOD_CONSUMPTION
)
from ..auxiliaries.arithmetic_dict import Arithmetic_Dict
from .social_classes.class_file import Class
from .social_classes.nobles import Nobles
from .social_classes.artisans import Artisans
from .social_classes.peasants import Peasants
from .social_classes.others import Others
from .state_modifiers import State_Modifiers
from .state_data_employ_and_commands import _State_Data_Employment_and_Commands
from .government import Government
from .market import Market
from math import isinf, log


class EveryoneDeadError(Exception):
    pass


class RebellionError(Exception):
    pass


class InvalidYearChangeError(Exception):
    pass


class InvalidClassesListError(Exception):
    pass


class MathTmFailure(Exception):
    pass


class State_Data(_State_Data_Employment_and_Commands):
    """
    Represents the data of an entire state, including all its classes.
    Properties:
    month - the current month
    classes - social classes of the country
    government - government of the country's object
    _market - object executing trade within the country
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
        self.prices = DEFAULT_PRICES.copy()
        self.sm = State_Modifiers(self)

        class Fake_Nobles:
            def __init__(self):
                self.population = 0
        self._classes = [Fake_Nobles()]
        self._government = None
        self.debug = False

        self.brigands = 0
        self.brigand_strength = 0.8

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

        if "laws" in data:
            state.sm.tax_rates["personal"] = data["laws"]["tax_personal"]
            state.sm.tax_rates["property"] = data["laws"]["tax_property"]
            state.sm.tax_rates["income"] = data["laws"]["tax_income"]
            state.sm.others_minimum_wage = data["laws"]["wage_minimum"]
            state.government.wage = data["laws"]["wage_government"]
            state.government.wage_autoregulation = \
                data["laws"]["wage_autoregulation"]
            state.sm.max_prices = data["laws"]["max_prices"]

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
            "prices": self.prices,
            "laws": {
                "tax_personal": self.sm.tax_rates["personal"],
                "tax_property": self.sm.tax_rates["property"],
                "tax_income": self.sm.tax_rates["income"],
                "wage_minimum": self.sm.others_minimum_wage,
                "wage_government": self.government.wage,
                "wage_autoregulation": self.government.wage_autoregulation,
                "max_prices": self.sm.max_prices,
            }
        }
        return data

    def _do_growth(self):
        """
        Does the natural population growth for all classes.
        """
        factor = self.sm.default_growth_factor / 12
        for social_class in self.classes:
            old_pop = social_class.new_population
            social_class.grow_population(factor)
            if self.debug:
                print(f"Grown {social_class.new_population - old_pop} "
                      f"{social_class.class_name}")

    def _do_starvation(self):
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

            dead = starving_number + freezing_number
            if starving_number + freezing_number < social_class.new_population:
                part_dead = dead / social_class.new_population
                social_class.new_population -= dead
                social_class.happiness += Class.starvation_happiness(part_dead)
            else:
                social_class.new_population = 0
                social_class.happiness += Class.starvation_happiness(1)

            if self.debug:
                print(f"Starved {old_pop - social_class.new_population} "
                      f"{social_class.class_name}")

    def _reset_flags(self):
        """
        Resets promotion and demotion flags on all classes to False.
        """
        for social_class in self.classes:
            social_class.promoted_from = False
            social_class.promoted_to = False
            social_class.demoted_from = False
            social_class.demoted_to = False

    def _do_demotions(self):
        """
        Does demotions to fix as many negative resources as possible.
        """
        for social_class in self.classes:
            lower_class = social_class.lower_class
            lower_name = lower_class.class_name

            moved_pop = min(
                social_class.class_overpopulation, social_class.new_population
            )
            if moved_pop == social_class.new_population:
                moved_res = social_class.new_resources + \
                    INBUILT_RESOURCES[social_class.class_name] * moved_pop
            else:
                moved_res = INBUILT_RESOURCES[lower_name] * moved_pop

            social_class.new_resources -= moved_res
            lower_class.new_resources += moved_res
            social_class.new_population -= moved_pop
            lower_class.new_population += moved_pop
            if moved_pop > 0:
                social_class.demoted_from = True
                lower_class.demoted_to = True

            if self.debug:
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
        if flush:
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
                avger_wealth + 0.6666, 100
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
        self, class_from: Class, class_to: Class, increase_price
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

        if self.debug:
            print(f"Promoted {transferred} {class_from.class_name} to "
                  f"{class_to.class_name}")

    def _do_double_promotion(
        self, class_from: Class, class_to_1: Class, increase_price_1,
        class_to_2: Class, increase_price_2
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

        if self.debug:
            print(f"Double promoted {transferred} {class_from.class_name} to "
                  f"{class_to_1.class_name} and {class_to_2.class_name}")

    def _do_promotions(self):
        """
        Does all the promotions of one month end.
        """
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
                                          artisans, increase_price_2)

        # Check the nobles' cap
        if nobles.population < self.sm.nobles_cap * \
                self.get_available_employees():
            # Increase price for nobles
            increase_price = self.sm.increase_price_factor * \
                sum((INBUILT_RESOURCES["nobles"] * self.prices).values())

            if peasants.population > 0:
                if (not peasants.starving) and (not peasants.freezing):
                    # Nobles (from peasants):
                    self._do_one_promotion(peasants, nobles, increase_price)

            if artisans.population > 0:
                if (not artisans.starving) and (not artisans.freezing):
                    # Nobles (from artisans):
                    self._do_one_promotion(artisans, nobles, increase_price)

    def _get_personal_taxes(self, populations, net_worths):
        """
        Returns how much of the resources of each class is to be taxed
        based on its population, as defined by the tax_rates modifier.
        """
        flat_taxes = self.sm.tax_rates["personal"] * populations
        rel_taxes = flat_taxes / net_worths
        return rel_taxes

    def _get_property_taxes(self):
        """
        Returns how much of the resources of each class is to be taxed
        based on its net worth, as defined by the tax_rates modifier.
        """
        rel_taxes = self.sm.tax_rates["property"]
        return rel_taxes

    def _get_income_taxes(self, net_worths_change, net_worths):
        """
        Returns how much of the resources of each class is to be taxed
        based on its net worth increase, as defined by the tax_rates modifier.
        """
        flat_taxes = self.sm.tax_rates["income"] * net_worths_change
        rel_taxes = flat_taxes / net_worths
        return rel_taxes

    def _do_taxes(self, old_net_worths):
        """
        Siphons part of the classes' resources into the government.
        """
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
        net_worths_change = net_worths - old_net_worths

        rel_taxes = self._get_personal_taxes(populations, net_worths)
        rel_taxes += self._get_property_taxes()
        rel_taxes += self._get_income_taxes(net_worths_change, net_worths)

        rel_taxes = {
            class_name: min(tax, 1)
            for class_name, tax
            in rel_taxes.items()
        }
        for social_class in self.classes:
            tax = social_class.real_resources * \
                rel_taxes[social_class.class_name]
            self.government.new_resources += tax
            social_class.new_resources -= tax
            social_class.happiness += Class.resources_seized_happiness(
                rel_taxes[social_class.class_name]
            )

    @staticmethod
    def _get_flee_rate(happiness):
        """
        Math for the flee rate based on happiness.
        """
        if happiness > 0:
            flee_rate = 0
        else:
            flee_rate = (happiness / 100) ** 4 / 15
            flee_rate = min(flee_rate, 1)
        return flee_rate

    def _add_brigands(self, number, strength):
        """
        Adds the given number of brigands of the given strength to the state.
        """
        # Monthly rate of turning criminal: (happiness)^4 / (1,5 * 10^9)
        old_strength = self.brigands * self.brigand_strength
        new_strength = number * strength
        total_strength = old_strength + new_strength
        self.brigands += number
        self.brigand_strength = total_strength / self.brigands

    @property
    def total_population(self):
        total = self.government.soldiers_population
        for social_class in self.classes:
            total += social_class.population
        total += self.brigands
        return total

    def _do_theft(self):
        """
        Makes brigands steal resources. Stolen resources are not stored
        anywhere, they disappear.
        """
        crime_rate = self.brigands / self.total_population

        for social_class in self.classes:
            stolen = social_class.real_resources * (crime_rate / 2)
            stolen["land"] = 0
            social_class.new_resources -= stolen
            if social_class.net_worth > 0:
                social_class.happiness += Class.resources_seized_happiness(
                    self._get_monetary_value(stolen) / social_class.net_worth
                )
        stolen = self.government.real_resources * (crime_rate / 2)
        stolen["land"] = 0
        self.government.new_resources -= stolen

    def _make_new_brigands(self):
        """
        Makes people from unhappy social classes flee to become brigands.
        """
        for social_class in self.classes:
            if social_class.happiness < 0:
                flee_rate = State_Data._get_flee_rate(social_class.happiness)
                fled = social_class.population * flee_rate
                self._add_brigands(
                    fled, BRIGAND_STRENGTH[social_class.class_name]
                )
                social_class.new_population -= fled
        if self.government.soldier_revolt \
           and self.government.soldiers_population > 0:
            soldiers_happiness = -100 * self.government.missing_food / \
                self.government.soldiers_population
            flee_rate = State_Data._get_flee_rate(soldiers_happiness)
            for soldier_kind, number in self.government.soldiers.items():
                fled = number * flee_rate
                self._add_brigands(fled, BRIGAND_STRENGTH[soldier_kind])
                self.government.soldiers[soldier_kind] -= fled

    def _do_crime(self):
        """
        Handles crime and people fleeing to join the brigands.
        """
        # Do crime - steal resources
        self._do_theft()

        # Increase of number of criminals
        self._make_new_brigands()

    def get_state_data(self, attribute: str, govt: bool, default=None):
        """
        Returns a dict with the given name containing the chosen attribute to
        month_data.
        """
        result = Arithmetic_Dict({
            class_name: getattr(self.classes[index], attribute, default)
            for index, class_name
            in enumerate(CLASSES)
        })
        if govt:
            result["government"] = getattr(self.government, attribute, default)
        return result

    def do_month(self):
        """
        Does all the needed calculations and changes to end the month and move
        on to the next. Returns a dict with data from the month.
        """
        if self.debug:
            print(f"Ending month {self.month} {self.year}")
        # Check for game over
        someone_alive = False
        for social_class in self.classes:
            if social_class.population > 0:
                someone_alive = True
        if not someone_alive:
            raise EveryoneDeadError

        for social_class in self.classes:
            if social_class.happiness < REBELLION_THRESHOLD:
                raise RebellionError(social_class.class_name)

        # Save old data to calculate the changes
        old_resources = self.get_state_data("real_resources", True)
        old_population = self.get_state_data("population", False)
        old_net_worths = self.get_state_data("net_worth", False)

        # Create returned dict
        month_data = {
            "year": self.year,
            "month": self.month
        }

        # Zeroth: decay happiness
        for social_class in self.classes:
            social_class.decay_happiness()

        # First: growth - resources might become negative
        self._do_growth()

        # Second: production
        for social_class in self.classes:
            social_class.produce()
        self._employ()

        # Third: consumption (and crime)
        for social_class in self.classes:
            social_class.consume()
        self.government.consume()
        self._do_crime()

        # Fourth: taxes
        self._do_taxes(old_net_worths)

        # Fifth: demotions - should fix all except food and some wood
        self._reset_flags()
        self._do_demotions()
        self._secure_classes(flush=False)

        # Sixth: starvation - should fix all remaining resources
        self._do_starvation()

        # Seventh: security and flushing
        self._secure_classes()

        # Eighth: promotions
        self._do_promotions()  # Might make resources negative
        self._do_demotions()  # Fix resources again

        # Ninth: trade
        self._market.do_trade()
        self.prices = self._market.prices
        month_data["prices"] = self.prices

        # Tenth: calculations done - advance to the next month
        self._secure_classes()
        self._advance_month()

        # Eleventh: update happiness plateau
        for social_class in self.classes:
            social_class.update_happiness_plateau()

        # Twelfth: return the necessary data
        month_data["resources_after"] = self.get_state_data(
            "real_resources", True
        )
        month_data["population_after"] = self.get_state_data(
            "population", False
        )
        month_data["resources_change"] = \
            month_data["resources_after"] - old_resources
        month_data["population_change"] = \
            month_data["population_after"].round() - old_population.round()

        month_data["growth_modifiers"] = {
            class_name: {
                "starving": self.classes[index].starving,
                "freezing": self.classes[index].freezing,
                "demoted_from": self.classes[index].demoted_from,
                "demoted_to": self.classes[index].demoted_to,
                "promoted_from": self.classes[index].promoted_from,
                "promoted_to": self.classes[index].promoted_to
            }
            for index, class_name
            in enumerate(CLASSES)
        }

        month_data["employees"] = self.get_state_data("employees", True, 0)
        month_data["wages"] = self.get_state_data(
            "old_wage", True, self.sm.others_minimum_wage
        )
        month_data["happiness"] = self.get_state_data("happiness", False)
        return month_data
