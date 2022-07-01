from ..auxiliaries.constants import (
    CLASS_NAME_TO_INDEX,
    DEFAULT_PRICES,
    EMPTY_RESOURCES,
    WAGE_CHANGE
)
from ..auxiliaries.arithmetic_dict import Arithmetic_Dict
from .social_classes.class_file import Class


class InvalidCommandError(Exception):
    pass


class _State_Data_Employment_and_Commands:
    def _set_wages_and_employers(self):
        """
        Makes employers' wages compliant with minimum wage and returns a list
        of employers classes.
        """
        employers_classes = []
        for social_class in self.classes:
            if social_class.real_resources["land"] > 0:
                employers_classes.append(social_class)
                if not hasattr(social_class, "wage"):
                    social_class.wage = self.sm.others_minimum_wage
                else:
                    social_class.wage = max(
                        social_class.wage, self.sm.others_minimum_wage
                    )
        if self.government.real_resources["land"] > 0:
            employers_classes.append(self.government)
            self.government.wage = max(
                self.government.wage, self.sm.others_minimum_wage
            )
        return employers_classes

    def _set_employees_and_wage_shares(self, employers_classes):
        """
        Sets wage share for each employee class (what part of produced
        resources given to employees this class will get) and returns a list
        of employees and total number of employees.
        """
        employees_classes = []
        employees = 0
        for social_class in self.classes:
            if social_class.employable:
                employees_classes.append(social_class)
                employees += social_class.population
        for social_class in employees_classes:
            social_class.wage_share = social_class.population / employees

        max_employees = sum([social_class.max_employees
                             for social_class
                             in employers_classes])
        if max_employees < employees:
            employees = max_employees

        return employees_classes, employees

    @staticmethod
    def _get_ratios(dictionary: dict):
        """
        Returns a dict of ratios:
            key: value / sum of values.
        """
        dictionary = Arithmetic_Dict(dictionary)
        total = sum(dictionary.values())
        if total != 0:
            ratios = dictionary / total
        else:
            ratios = Arithmetic_Dict({
                key: 0
                for key
                in dictionary
            })
        return ratios

    def _get_tools_used(self, employees: dict[str, int]):
        """
        Returns the amount of tools that will be used in production this month.
        """
        peasant_tools_used = self.sm.peasant_tool_usage * \
            (employees["food"] + employees["wood"])
        miner_tools_used = self.sm.miner_tool_usage * \
            (employees["stone"] + employees["iron"])

        return peasant_tools_used + miner_tools_used

    @staticmethod
    def _add_employees(employees: dict[Class, int]):
        """
        Adds the given employees numbers to the given employers classes.
        """
        for employer, value in employees.items():
            if hasattr(employer, "employees"):
                employer.employees += value
            else:
                employer.employees = value

    def _get_produced_and_used(self, ratioed_employees):
        """
        Calculates how much resources will be produced and used as a result of
        this month's employment.
        """
        per_capita = Arithmetic_Dict({
            "food": self.sm.food_production[self.month],
            "wood": self.sm.wood_production,
            "stone": self.sm.stone_production,
            "iron": self.sm.iron_production
        })

        produced = per_capita * ratioed_employees
        used = EMPTY_RESOURCES.copy()
        used["tools"] = self._get_tools_used(ratioed_employees)

        return produced, used

    @staticmethod
    def _set_employers_employees(employers_classes: list[Class],
                                 employees: int):
        """
        Decides what part of produced and used resources will each employer
        class be given.
        """
        wages = {social_class: social_class.wage
                 for social_class
                 in employers_classes}
        ratios = _State_Data_Employment_and_Commands._get_ratios(wages)
        _State_Data_Employment_and_Commands._add_employees(ratios * employees)

        checked = 0
        while checked < len(employers_classes):
            checked = 0
            for social_class in employers_classes:
                if social_class.employees > social_class.max_employees:
                    employees = \
                        social_class.employees - social_class.max_employees
                    social_class.employees = social_class.max_employees
                    del wages[social_class]
                    ratios = _State_Data_Employment_and_Commands._get_ratios(
                        wages
                    )
                    _State_Data_Employment_and_Commands._add_employees(
                        ratios * employees
                    )
                else:
                    checked += 1

        for employer in employers_classes:
            if employer.employees == employer.max_employees:
                employer.increase_wage = False
            else:
                employer.increase_wage = True

    @staticmethod
    def _employees_to_profit(employers_classes: list[Class]):
        """
        Removes employees attribute from employers classes, adding
        profit_share attribute instead, indicating what part of total produced
        resources were produced in the employ of this class.
        """
        total_employees = 0
        for employer in employers_classes:
            total_employees += employer.employees

        for employer in employers_classes:
            employer.profit_share = employer.employees / total_employees
            del employer.employees

    @staticmethod
    def _distribute_produced_and_used(employers_classes, employees_classes,
                                      produced, used):
        """
        Distributes the produced and used resources among employers and
        employees.
        """
        employers_share = EMPTY_RESOURCES.copy()
        for employer in employers_classes:
            share = produced * employer.profit_share * (1 - employer.wage)
            employer.new_resources += share
            employers_share += share
            employer.new_resources -= used * employer.profit_share
            del employer.profit_share

        produced -= employers_share
        for employee in employees_classes:
            employee.new_resources += produced * employee.wage_share

    @staticmethod
    def _set_new_wages(employers_classes):
        """
        Sets new wages for the next month based on employment in this month.
        """
        for employer in employers_classes:
            if employer.increase_wage:
                employer.wage += WAGE_CHANGE
                employer.wage = min(employer.wage, 1)
            else:
                employer.wage -= WAGE_CHANGE
                employer.wage = max(employer.wage, 0)

    def _employ(self):
        """
        Executes employable classes' production.
        """
        employers_classes = self._set_wages_and_employers()

        employees_classes, employees = self._set_employees_and_wage_shares(
            employers_classes
        )

        raw_prices = self.prices / DEFAULT_PRICES
        del raw_prices["tools"]
        del raw_prices["land"]

        ratioed_employees = _State_Data_Employment_and_Commands._get_ratios(
            raw_prices) * employees

        produced, used = self._get_produced_and_used(ratioed_employees)

        _State_Data_Employment_and_Commands._set_employers_employees(
            employers_classes, employees
        )
        _State_Data_Employment_and_Commands._employees_to_profit(
            employers_classes
        )

        _State_Data_Employment_and_Commands._distribute_produced_and_used(
            employers_classes, employees_classes, produced, used
        )
        _State_Data_Employment_and_Commands._set_new_wages(employers_classes)

    def do_transfer(self, class_name: str, resource: str, amount: int):
        """
        Moves resources between the government and a social class. More info
        in interface transfer command.
        """
        class_index = CLASS_NAME_TO_INDEX[class_name]

        res = self.government.new_resources
        res[resource] -= amount
        self.government.new_resources = res

        res = self.classes[class_index].new_resources
        res[resource] += amount
        self.classes[class_index].new_resources = res

        self._do_demotions()
        self._secure_classes()

    def do_secure(self, resource: str, amount: int):
        """
        Makes the given amount of a resource owned by the government
        untradeable (secured). Negative amount signifies making a resource
        tradeable again.
        """
        res = self.government.new_resources
        res[resource] -= amount
        self.government.new_resources = res

        res = self.government.secure_resources
        res[resource] += amount
        self.government.secure_resources = res

        self.government.flush()

    def do_optimal(self, resource: str, amount: int):
        """
        Sets government's optimal resource to the given value.
        """
        self.government.optimal_resources[resource] = amount

    def do_set_law(self, law: str, social_class: str | None, value: float):
        """
        Sets the given law to the given value.
        """
        try:
            if law == "tax_personal":
                self.sm.tax_rates['personal'][social_class] = value
            elif law == "tax_property":
                self.sm.tax_rates['property'][social_class] = value
            elif law == "tax_income":
                self.sm.tax_rates['income'][social_class] = value
            elif law == "wage_minimum":
                self.sm.others_minimum_wage = value
            elif law == "wage_government":
                self.government.wage = value
            else:
                raise InvalidCommandError
        except KeyError:
            raise InvalidCommandError

    def execute_commands(self, commands: list[str]):
        """
        Executes the given commands.
        Format: [
            "<command> <argument> <argument>...",
            "<command> <argument> <argument>...",
            and so on
        ]
        """
        for line in commands:
            command = line.split(' ')
            if command[0] == "next":
                amount = int(command[1])
                for _ in range(amount):
                    self.do_month()
            elif command[0] == "transfer":
                self.do_transfer(command[1], command[2], int(command[3]))
            elif command[0] == "secure":
                self.do_secure(command[1], int(command[2]))
            elif command[0] == "optimal":
                self.do_optimal(command[1], int(command[2]))
            elif command[0] == "laws" and command[1] == "set":
                if command[3] == "None":
                    command[3] = None
                self.do_set_law(command[2], command[3], float(command[4]))
            else:
                raise InvalidCommandError
