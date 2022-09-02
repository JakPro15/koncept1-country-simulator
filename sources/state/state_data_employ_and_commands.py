from __future__ import annotations

from abc import abstractmethod
from math import inf, isinf, log
from typing import TYPE_CHECKING, Any, Mapping, Protocol, Sequence, TypedDict

from ..auxiliaries.arithmetic_dict import Arithmetic_Dict
from ..auxiliaries.constants import (BRIGAND_STRENGTH_CLASS,
                                     BRIGAND_STRENGTH_SOLDIER, DEFAULT_PRICES,
                                     FOOD_CONSUMPTION, INBUILT_RESOURCES,
                                     REBELLION_THRESHOLD, WAGE_CHANGE,
                                     WOOD_CONSUMPTION)
from ..auxiliaries.enums import Class_Name, Month, Resource
from ..auxiliaries.resources import Resources
from .government import Government
from .market import Market, SupportsTrade
from .social_classes.artisans import Artisans
from .social_classes.class_file import Class
from .social_classes.nobles import Nobles
from .social_classes.others import Others
from .social_classes.peasants import Peasants
from .state_modifiers import State_Modifiers

if TYPE_CHECKING:
    from .state_data import State_Data


class InvalidCommandError(Exception):
    """
    Raised when a command or a command's argument given is not valid.
    """


class StateDataNotFinalizedError(Exception):
    """
    Raised when a the state data object is used before initializing classes
    and government.
    """


class EveryoneDeadError(Exception):
    """
    Raised when there are no people left in the country - game over.
    """


class RebellionError(Exception):
    """
    Raised when a social class rebels - game over.
    """
    def __init__(self, class_name: Class_Name) -> None:
        self.class_name = class_name.name


class Employer(Protocol):
    parent: State_Data
    resources: Resources
    employees: float
    wage: float
    increase_wage: bool
    profit_share: float
    old_wage: float

    @property
    @abstractmethod
    def real_resources(self) -> Resources:
        """
        Should return all the resources the classlike owns, including inbuilt
        and secure.
        """

    @property
    @abstractmethod
    def optimal_resources(self) -> Resources:
        """
        Should return optimal resources for the given classlike object, for
        trade purposes.
        """

    @property
    @abstractmethod
    def max_employees(self) -> float:
        """
        Should return how many employees at most the classlike can employ.
        """

    @abstractmethod
    def validate(self) -> None:
        """
        Should handle very small amounts of negative resources resulting from
        floating-point math and raise an exception if resources is negative
        after that.
        """


class Month_Data(TypedDict):
    prices: dict[str, float]
    resources_after: dict[str, dict[str, float]]
    population_after: dict[str, float]
    change_resources: dict[str, dict[str, float]]
    change_population: dict[str, float]
    growth_modifiers: dict[str, dict[str, bool]]
    employees: dict[str, float]
    wages: dict[str, float]
    happiness: dict[str, float]


class State_Data_Creation_And_Do_Month:
    def __init__(self, starting_month: Month = Month.January,
                 starting_year: int = 0) -> None:
        """
        Creates a State_Data object. Note that classes and government remain
        uninitialized and need to be manually set after the creation of the
        state.
        """
        self.year: int = starting_year
        self.month: Month = starting_month
        self.prices: Resources = DEFAULT_PRICES.copy()
        # self will always be State_Data when this is executed
        self.sm: State_Modifiers = State_Modifiers(self)  # type: ignore

        self._classes: dict[Class_Name, Class] | None = None
        self._government: Government | None = None
        self._market: Market | None = None

        self._brigands: float = 0.0
        self._brigand_strength: float = 0.8

    @property
    def classes(self) -> dict[Class_Name, Class]:
        if self._classes is not None:
            return self._classes.copy()
        else:
            raise StateDataNotFinalizedError("classes have not been set")

    @classes.setter
    def classes(self, new: Mapping[Class_Name, Class]):
        for name in Class_Name:
            assert new[name].class_name == name

        self._classes = dict(new)
        if self._government is not None:
            self._create_market()

        # These are used for demotions
        self._classes[Class_Name.nobles].lower_class = \
            self._classes[Class_Name.peasants]
        self._classes[Class_Name.artisans].lower_class = \
            self._classes[Class_Name.others]
        self._classes[Class_Name.peasants].lower_class = \
            self._classes[Class_Name.others]
        self._classes[Class_Name.others].lower_class = \
            self._classes[Class_Name.others]

    @property
    def government(self) -> Government:
        if self._government is not None:
            return self._government
        else:
            raise StateDataNotFinalizedError("government has not been set")

    @government.setter
    def government(self, new: Government):
        self._government = new
        if self._classes is not None:
            self._create_market()

    @property
    def market(self) -> Market:
        if self._market is not None:
            return self._market
        else:
            raise StateDataNotFinalizedError("market has not been set")

    @property
    def brigands(self) -> float:
        return self._brigands

    @brigands.setter
    def brigands(self, new: float):
        if new < 0:
            raise ValueError("brigands cannot be negative")
        self._brigands = new

    @property
    def brigands_strength(self) -> float:
        return self._brigands_strength

    @brigands_strength.setter
    def brigands_strength(self, new: float):
        if new < 0:
            raise ValueError("brigands cannot be negative")
        self._brigands_strength = new

    def _set_wages_and_employers(self) -> list[Employer]:
        """
        Makes employers' wages compliant with minimum wage and returns a list
        of employers classes.
        """
        employers_classes: list[Employer] = []
        for social_class in self.classes.values():
            social_class.employees = 0
            if social_class.real_resources.land > 0:
                employers_classes.append(social_class)
                social_class.wage = max(
                    social_class.wage, self.sm.others_minimum_wage
                )
        if self.government.real_resources.land > 0:
            self.government.employees = 0
            employers_classes.append(self.government)
            self.government.wage = max(
                self.government.wage, self.sm.others_minimum_wage
            )
        return employers_classes

    def _set_employees_and_wage_shares(self,
                                       employers_classes: Sequence[Employer]
                                       ) -> tuple[list[Class], float, float]:
        """
        Sets wage share for each employee class (what part of produced
        resources given to employees this class will get) and returns a list
        of employee classes, total number of employees and ratio of employees
        to total max employees.
        """
        employees_classes: list[Class] = []
        employees = 0
        for social_class in self.classes.values():
            if social_class.employable:
                employees_classes.append(social_class)
                employees += social_class.population
        for social_class in employees_classes:
            if employees > 0:
                social_class.wage_share = social_class.population / employees
            else:
                social_class.wage_share = 0

        max_employees = sum([social_class.max_employees
                             for social_class
                             in employers_classes])
        if max_employees < employees:
            employees = max_employees
        emp_ratio = employees / max_employees if max_employees > 0 else inf

        return employees_classes, employees, emp_ratio

    def _get_tools_used(self, employees: Mapping[Resource, float]) -> float:
        """
        Returns the amount of tools that will be used in production this month.
        """
        peasant_tools_used = self.sm.peasant_tool_usage * \
            (employees[Resource.food] + employees[Resource.wood])
        miner_tools_used = self.sm.miner_tool_usage * \
            (employees[Resource.stone] + employees[Resource.iron])

        return peasant_tools_used + miner_tools_used

    @staticmethod
    def _add_employees(employees: Mapping[Employer, float]) -> None:
        """
        Adds the given employees numbers to the given employers classes.
        """
        for employer, value in employees.items():
            if hasattr(employer, "employees"):
                employer.employees += value
            else:
                employer.employees = value

    def _get_produced_and_used(
        self, ratioed_employees: Arithmetic_Dict[Resource]
    ) -> tuple[Resources, Resources]:
        """
        Calculates how much resources will be produced and used as a result of
        this month's employment.
        """
        per_capita = Resources({
            Resource.food: self.sm.food_production[self.month],
            Resource.wood: self.sm.wood_production,
            Resource.stone: self.sm.stone_production,
            Resource.iron: self.sm.iron_production
        })

        produced = per_capita * ratioed_employees
        used = Resources()
        used.tools = self._get_tools_used(ratioed_employees)

        return produced, used

    @staticmethod
    def _set_employers_employees(employers_classes: Sequence[Employer],
                                 employees: float, emp_ratio: float) -> None:
        """
        Decides what part of produced and used resources will each employer
        class be given.
        """
        wages = Arithmetic_Dict({social_class: social_class.wage
                                 for social_class
                                 in employers_classes})
        ratios = wages.calculate_ratios()
        State_Data_Creation_And_Do_Month._add_employees(ratios * employees)

        checked = 0
        while checked < len(employers_classes):
            checked = 0
            for social_class in employers_classes:
                if social_class.employees > social_class.max_employees:
                    employees = \
                        social_class.employees - social_class.max_employees
                    social_class.employees = social_class.max_employees
                    del wages[social_class]
                    ratios = wages.calculate_ratios()
                    State_Data_Creation_And_Do_Month._add_employees(
                        ratios * employees
                    )
                else:
                    checked += 1

        for employer in employers_classes:
            if employer.employees < emp_ratio * employer.max_employees:
                employer.increase_wage = True
            else:
                employer.increase_wage = False

    @staticmethod
    def _employees_to_profit(employers_classes: Sequence[Employer]) -> None:
        """
        Removes employees attribute from employers classes, adding
        profit_share attribute instead, indicating what part of total produced
        resources were produced in the employ of this class.
        """
        total_employees = 0
        for employer in employers_classes:
            total_employees += employer.employees

        for employer in employers_classes:
            if total_employees > 0:
                employer.profit_share = employer.employees / total_employees
            else:
                employer.profit_share = 0

    def _distribute_produced_and_used(self,
                                      employers_classes: Sequence[Employer],
                                      employees_classes: Sequence[Class],
                                      produced: Resources, used: Resources
                                      ) -> None:
        """
        Distributes the produced and used resources among employers and
        employees.
        """
        total_employers_share = Resources()

        full_value = produced.worth(self.prices)
        used_value = used.worth(self.prices)
        if full_value > 0:
            self.max_wage = 1 - used_value / full_value
        else:
            self.max_wage = 1

        for employer in employers_classes:
            share = produced * employer.profit_share * (1 - employer.wage)
            employer.resources += share
            total_employers_share += share

            employer.resources -= used * employer.profit_share

            del employer.profit_share

        produced -= total_employers_share
        for employee in employees_classes:
            employee.resources += produced * employee.wage_share

    def _set_new_wages(self, employers_classes: Sequence[Employer]) -> None:
        """
        Sets new wages for the next month based on employment in this month.
        """
        for employer in employers_classes:
            employer.old_wage = employer.wage
            if not getattr(employer, "wage_autoregulation", True):
                continue

            if employer.increase_wage:
                employer.wage += WAGE_CHANGE
                employer.wage = min(
                    employer.wage, getattr(self, "max_wage", 1)
                )
            else:
                employer.wage -= WAGE_CHANGE
                employer.wage = max(employer.wage, 0)
                employer.wage = min(
                    employer.wage, getattr(self, "max_wage", 1)
                )

    def _employ(self) -> None:
        """
        Executes employable classes' production.
        """
        employers_classes = self._set_wages_and_employers()

        employees_classes, employees, emp_ratio = \
            self._set_employees_and_wage_shares(employers_classes)

        raw_prices = Arithmetic_Dict(self.prices / DEFAULT_PRICES)
        del raw_prices[Resource.tools]
        del raw_prices[Resource.land]

        ratioed_employees = raw_prices.calculate_ratios() * employees

        produced, used = self._get_produced_and_used(ratioed_employees)

        State_Data_Creation_And_Do_Month._set_employers_employees(
            employers_classes, employees, emp_ratio
        )
        State_Data_Creation_And_Do_Month._employees_to_profit(
            employers_classes
        )

        self._distribute_produced_and_used(
            employers_classes, employees_classes, produced, used
        )
        self._set_new_wages(employers_classes)

    def _advance_month(self) -> None:
        """
        Advances month, and possibly year, by one.
        """
        self.month = Month((self.month.value + 1) % 12)
        if self.month == Month.January:
            self.year += 1

    def _create_market(self) -> None:
        """
        Creates a market for the object. Needs classes and government to be
        initialized.
        """
        trading_objects: list[SupportsTrade] = list(self.classes.values())
        trading_objects.append(self.government)
        # When this is executed self will be a State_Data object
        self._market = Market(trading_objects, self)  # type: ignore

    def get_available_employees(self) -> float:
        """
        Returns the number of employees available to be hired this month.
        """
        employees = 0.0
        for social_class in self.classes.values():
            if social_class.employable:
                employees += social_class.population
        return employees

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> State_Data:
        """
        Creates a State_Data object from the given dict.
        """
        # When this is executed cls will be State_Data or a subtype
        state: State_Data = cls(data["month"], data["year"])  # type: ignore

        nobles = Nobles.from_dict(state, data["classes"]["nobles"])
        artisans = Artisans.from_dict(state, data["classes"]["artisans"])
        peasants = Peasants.from_dict(state, data["classes"]["peasants"])
        others = Others.from_dict(state, data["classes"]["others"])
        state.government = Government.from_dict(state, data["government"])
        state.classes = {
            Class_Name.nobles: nobles,
            Class_Name.artisans: artisans,
            Class_Name.peasants: peasants,
            Class_Name.others: others
        }

        state.prices = Resources(data["prices"])

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

    def to_dict(self) -> dict[str, Any]:
        """
        Returns a dict with the object's data. It's valid for from_dict
        function.
        """
        data = {
            "year": self.year,
            "month": self.month,
            "classes": {
                "nobles": self.classes[Class_Name.nobles].to_dict(),
                "artisans": self.classes[Class_Name.artisans].to_dict(),
                "peasants": self.classes[Class_Name.peasants].to_dict(),
                "others": self.classes[Class_Name.others].to_dict()
            },
            "government": self.government.to_dict(),
            "prices": self.prices.copy(),
            "laws": {
                "tax_personal": self.sm.tax_rates["personal"].copy(),
                "tax_property": self.sm.tax_rates["property"].copy(),
                "tax_income": self.sm.tax_rates["income"].copy(),
                "wage_minimum": self.sm.others_minimum_wage,
                "wage_government": self.government.wage,
                "wage_autoregulation": self.government.wage_autoregulation,
                "max_prices": self.sm.max_prices.copy(),
            }
        }
        return data

    def _do_growth(self) -> None:
        """
        Does the natural population growth for all classes.
        """
        factor = self.sm.default_growth_factor / 12
        for social_class in self.classes.values():
            old_pop = social_class.population
            social_class.grow_population(factor)
            if __debug__:
                print(f"Grown {social_class.population - old_pop} "
                      f"{social_class.class_name.name}")

    def _do_starvation(self) -> None:
        """
        Does starvation and freezing to fix negative food and wood.
        Starving or freezing is marked with a bool attribute of the class.
        """
        for social_class in self.classes.values():
            old_pop = social_class.population

            missing_food = social_class.missing_resources.food
            starving_number = 0
            if missing_food > 0:
                starving_number = self.sm.starvation_mortality * missing_food \
                    / FOOD_CONSUMPTION

                social_class.resources.food = 0
                social_class.starving = True
            else:
                social_class.starving = False

            missing_wood = social_class.missing_resources.wood
            freezing_number = 0
            if missing_wood > 0:
                freezing_number = self.sm.freezing_mortality * missing_wood \
                    / WOOD_CONSUMPTION[self.month]

                social_class.resources.wood = 0
                social_class.freezing = True
            else:
                social_class.freezing = False

            dead = starving_number + freezing_number
            if starving_number + freezing_number < social_class.population:
                part_dead = dead / social_class.population
                social_class.population -= dead
                social_class.happiness += Class.starvation_happiness(part_dead)
            elif social_class.population != 0:
                social_class.population = 0
                social_class.happiness = 0

            if __debug__:
                print(f"Starved {old_pop - social_class.population} "
                      f"{social_class.class_name.name}")

    def _reset_flags(self) -> None:
        """
        Resets promotion and demotion flags on all classes to False.
        """
        for social_class in self.classes.values():
            social_class.promoted_from = False
            social_class.promoted_to = False
            social_class.demoted_from = False
            social_class.demoted_to = False

    def _do_demotions(self) -> None:
        """
        Does demotions to fix as many negative resources as possible.
        """
        for social_class in self.classes.values():
            lower_class = social_class.lower_class
            lower_name = lower_class.class_name

            moved_pop = min(
                social_class.class_overpopulation, social_class.population
            )
            if moved_pop == social_class.population:
                moved_res = social_class.resources + \
                    INBUILT_RESOURCES[social_class.class_name] * moved_pop
            else:
                moved_res = INBUILT_RESOURCES[lower_name] * moved_pop

            social_class.resources -= moved_res
            lower_class.resources += moved_res
            social_class.population -= moved_pop
            lower_class.population += moved_pop
            if moved_pop > 0:
                social_class.demoted_from = True
                lower_class.demoted_to = True

            if __debug__:
                print(f"Demoted {moved_pop} {social_class.class_name.name}")

    def _secure_classes(self) -> None:
        """
        Secures and validates all classes and the government.
        """
        for social_class in self.classes.values():
            social_class.validate()
            social_class.handle_empty_class()
        self.government.validate()

    @staticmethod
    def _promotion_math(from_wealth: float, from_pop: float,
                        increase_price: float) -> tuple[float, float]:
        """
        Calculates how many of the class will be promoted.
        Returns tuple (part_paid, transferred)
        part_paid is what part of resources will be transferred together with
        the promoted people, in range [0, 1]
        transferred is the number of promoted people
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
            # that is, if the class can afford such a promotion
            assert part_paid * from_wealth < transferred * increase_price
        else:
            part_paid = 0.0
            transferred = 0.0

        return part_paid, transferred

    def _do_one_promotion(
        self, class_from: Class, class_to: Class, increase_price: float
    ) -> None:
        """
        Does one promotion on the given classes.
        """
        from_wealth = sum((class_from.resources * self.prices).values())
        part_paid, transferred = State_Data._promotion_math(
            from_wealth, class_from.population, increase_price
        )

        class_to.resources += class_from.resources * part_paid
        class_from.resources -= class_from.resources * part_paid

        class_to.population += transferred
        class_from.population -= transferred

        if transferred > 0:
            class_from.promoted_from = True
            class_to.promoted_to = True

        if __debug__:
            print(f"Promoted {transferred} {class_from.class_name.name} to "
                  f"{class_to.class_name.name}")

    def _do_double_promotion(
        self, class_from: Class, class_to_1: Class, increase_price_1: float,
        class_to_2: Class, increase_price_2: float
    ) -> None:
        """
        Does one promotion on the given classes. Same number of people is
        promoted into both of the destination classes.
        """
        from_wealth = sum((class_from.resources * self.prices).values())

        summed_price = (increase_price_1 + increase_price_2)
        increase_price = summed_price / 2

        part_paid, transferred = State_Data._promotion_math(
            from_wealth, class_from.population, increase_price
        )

        part_paid_1 = part_paid * increase_price_1 / summed_price
        part_paid_2 = part_paid * increase_price_2 / summed_price

        class_to_1.resources += class_from.resources * part_paid_1
        class_to_2.resources += class_from.resources * part_paid_2
        class_from.resources -= class_from.resources * part_paid

        class_to_1.population += transferred / 2
        class_to_2.population += transferred / 2
        class_from.population -= transferred

        if transferred > 0:
            class_from.promoted_from = True
            class_to_1.promoted_to = True
            class_to_2.promoted_to = True

        if __debug__:
            print(f"Double promoted {transferred} {class_from.class_name.name}"
                  f" to {class_to_1.class_name.name} and "
                  f"{class_to_2.class_name.name}")

    def _do_promotions(self) -> None:
        """
        Does all the promotions of one month end.
        """
        nobles = self.classes[Class_Name.nobles]
        artisans = self.classes[Class_Name.artisans]
        peasants = self.classes[Class_Name.peasants]
        others = self.classes[Class_Name.others]

        if others.population > 0:
            if (not others.starving) and (not others.freezing):
                # Peasants and artisans (from others):
                increase_price_1 = self.sm.increase_price_factor * \
                    sum((INBUILT_RESOURCES[Class_Name.peasants] * self.prices
                         ).values())
                increase_price_2 = self.sm.increase_price_factor * \
                    sum((INBUILT_RESOURCES[Class_Name.artisans] * self.prices
                         ).values())
                self._do_double_promotion(others, peasants, increase_price_1,
                                          artisans, increase_price_2)

        # Check the nobles' cap
        if nobles.population < self.sm.nobles_cap * \
                self.get_available_employees():
            # Increase price for nobles
            increase_price = self.sm.increase_price_factor * \
                sum((INBUILT_RESOURCES[Class_Name.nobles] * self.prices
                     ).values())

            if peasants.population > 0:
                if (not peasants.starving) and (not peasants.freezing):
                    # Nobles (from peasants):
                    self._do_one_promotion(peasants, nobles, increase_price)

            if artisans.population > 0:
                if (not artisans.starving) and (not artisans.freezing):
                    # Nobles (from artisans):
                    self._do_one_promotion(artisans, nobles, increase_price)

    def _get_personal_taxes(self,
                            populations: Arithmetic_Dict[Class_Name],
                            net_worths: Arithmetic_Dict[Class_Name]
                            ) -> Arithmetic_Dict[Class_Name]:
        """
        Returns how much of the resources of each class is to be taxed
        based on its population, as defined by the tax_rates modifier.
        """
        flat_taxes = self.sm.tax_rates["personal"] * populations
        rel_taxes = flat_taxes / net_worths
        return rel_taxes

    def _get_property_taxes(self) -> Arithmetic_Dict[Class_Name]:
        """
        Returns how much of the resources of each class is to be taxed
        based on its net worth, as defined by the tax_rates modifier.
        """
        rel_taxes = self.sm.tax_rates["property"]
        return rel_taxes

    def _get_income_taxes(self,
                          net_worths_change: Arithmetic_Dict[Class_Name],
                          net_worths: Arithmetic_Dict[Class_Name]
                          ) -> Arithmetic_Dict[Class_Name]:
        """
        Returns how much of the resources of each class is to be taxed
        based on its net worth increase, as defined by the tax_rates modifier.
        """
        flat_taxes = self.sm.tax_rates["income"] * net_worths_change
        rel_taxes = flat_taxes / net_worths
        return rel_taxes

    def _do_taxes(self, old_net_worths: Arithmetic_Dict[Class_Name]
                  ) -> None:
        """
        Siphons part of the classes' resources into the government.
        """
        populations = Arithmetic_Dict({
            name: social_class.population
            for name, social_class
            in self.classes.items()
        })
        net_worths = Arithmetic_Dict({
            name: social_class.net_worth
            for name, social_class
            in self.classes.items()
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
        for social_class in self.classes.values():
            tax: Resources = social_class.real_resources * \
                rel_taxes[social_class.class_name]
            self.government.resources += tax
            social_class.resources -= tax

            value_of_tax = tax.worth(self.prices)
            if social_class.population > 0:
                social_class.happiness += Class.resources_seized_happiness(
                    value_of_tax / social_class.population
                )

    @staticmethod
    def _get_flee_rate(happiness: float) -> float:
        """
        Math for the flee rate based on happiness.
        """
        if happiness > 0:
            flee_rate = 0
        else:
            flee_rate = (happiness / 100) ** 2 / 10
            flee_rate = min(flee_rate, 1)
        return flee_rate

    def _add_brigands(self, number: float, strength: float) -> None:
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
    def total_population(self) -> float:
        total = self.government.soldiers.number
        for social_class in self.classes.values():
            total += social_class.population
        total += self.brigands
        return total

    def _do_theft(self) -> None:
        """
        Makes brigands steal resources. Stolen resources are not stored
        anywhere, they disappear.
        """
        crime_rate = self.brigands / self.total_population

        for social_class in self.classes.values():
            stolen = social_class.real_resources * (crime_rate / 2)
            stolen.land = 0
            social_class.resources -= stolen
            if social_class.net_worth > 0:
                social_class.happiness += Class.resources_seized_happiness(
                    stolen.worth(self.prices) / social_class.population
                )
        stolen = self.government.real_resources * (crime_rate / 2)
        stolen.land = 0
        self.government.resources -= stolen

    def _make_new_brigands(self) -> None:
        """
        Makes people from unhappy social classes flee to become brigands.
        """
        for social_class in self.classes.values():
            if social_class.happiness < 0:
                flee_rate = State_Data._get_flee_rate(social_class.happiness)
                fled = social_class.population * flee_rate
                self._add_brigands(
                    fled, BRIGAND_STRENGTH_CLASS[social_class.class_name]
                )
                social_class.population -= fled
        if self.government.soldier_revolt \
           and self.government.soldiers.number > 0:
            soldiers_happiness = -100 * self.government.missing_food / \
                self.government.soldiers.number
            flee_rate = State_Data._get_flee_rate(soldiers_happiness)
            for sold, number in self.government.soldiers.items():
                fled = number * flee_rate
                self._add_brigands(fled, BRIGAND_STRENGTH_SOLDIER[sold])
                self.government.soldiers[sold] -= fled

    def _do_crime(self) -> None:
        """
        Handles crime and people fleeing to join the brigands.
        """
        # Do crime - steal resources
        self._do_theft()

        # Increase of number of criminals
        self._make_new_brigands()

    def do_month(self) -> Month_Data:
        """
        Does all the needed calculations and changes to end the month and move
        on to the next. Returns a dict with data from the month.
        """
        if __debug__:
            print(f"Ending month {self.month} {self.year}")
        # Check for game over
        someone_alive = False
        for social_class in self.classes.values():
            if social_class.population > 0:
                someone_alive = True
        if not someone_alive:
            raise EveryoneDeadError

        for social_class in self.classes.values():
            if social_class.happiness < REBELLION_THRESHOLD:
                raise RebellionError(social_class.class_name)

        # Save old data to calculate the changes
        old_resources = {
            class_name.name: self.classes[class_name].real_resources
            for class_name in Class_Name
        }
        old_resources["government"] = self.government.real_resources

        old_population = {
            class_name.name: self.classes[class_name].population
            for class_name in Class_Name
        }

        old_net_worths = Arithmetic_Dict({
            class_name: self.classes[class_name].population
            for class_name in Class_Name
        })

        # decay happiness
        for social_class in self.classes.values():
            social_class.decay_happiness()

        # growth - resources might become negative
        self._do_growth()

        # production
        for social_class in self.classes.values():
            social_class.produce()
        self._employ()

        # consumption (and crime)
        for social_class in self.classes.values():
            social_class.consume()
        self.government.consume()
        self._do_crime()

        # taxes
        self._do_taxes(old_net_worths)

        # demotions - should fix all except food and some wood
        self._reset_flags()
        self._do_demotions()
        self._secure_classes()

        # starvation - should fix all remaining resources
        self._do_starvation()

        # security and flushing
        self._secure_classes()

        # promotions
        self._do_promotions()  # Might make resources negative
        self._do_demotions()  # Fix resources again

        # trade
        self.market.do_trade()
        self.prices = self.market.prices

        # calculations done - advance to the next month
        self._secure_classes()
        self._advance_month()

        # Create returned dict
        res_after = {
            class_name.name:
            self.classes[class_name].real_resources.to_raw_dict()
            for class_name in Class_Name
        }
        res_after["government"] = \
            self.government.real_resources.to_raw_dict()

        pop_after = {
            class_name.name: self.classes[class_name].population
            for class_name in Class_Name
        }

        month_data: Month_Data = {
            "prices": self.prices.to_raw_dict(),
            "resources_after": res_after,
            "population_after": pop_after,
            "change_resources": {
                key: dict(Arithmetic_Dict(res_after[key])
                          - old_resources[key])
                for key
                in [cls_name.name for cls_name in Class_Name] + ["government"]
            },
            "change_population": {
                key: pop_after[key] - old_population[key]
                for key
                in [cls_name.name for cls_name in Class_Name]
            },
            "growth_modifiers": {
                class_name.name: {
                    "starving": self.classes[class_name].starving,
                    "freezing": self.classes[class_name].freezing,
                    "demoted_from": self.classes[class_name].demoted_from,
                    "demoted_to": self.classes[class_name].demoted_to,
                    "promoted_from": self.classes[class_name].promoted_from,
                    "promoted_to": self.classes[class_name].promoted_to
                }
                for class_name in Class_Name
            },
            "employees": {
                class_name.name:
                self.classes[class_name].employees
                for class_name in Class_Name
            },
            "wages": {
                class_name.name:
                self.classes[class_name].old_wage
                for class_name in Class_Name
            },
            "happiness": {
                class_name.name:
                self.classes[class_name].happiness
                for class_name in Class_Name
            }
        }

        month_data["wages"]["government"] = self.government.old_wage
        month_data["employees"]["government"] = self.government.employees

        return month_data
