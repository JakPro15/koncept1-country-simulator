from math import inf
from ..auxiliaries.constants import (
    BASE_BATTLE_LOSSES,
    CLASS_NAME_TO_INDEX,
    CLASS_TO_SOLDIER,
    DEFAULT_PRICES,
    EMPTY_RESOURCES,
    PLUNDER_FACTOR,
    RECRUITMENT_COST,
    WAGE_CHANGE,
    INBUILT_RESOURCES
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
            if hasattr(social_class, "employees"):
                del social_class.employees
            if social_class.real_resources["land"] > 0:
                employers_classes.append(social_class)
                if not hasattr(social_class, "wage"):
                    social_class.wage = self.sm.others_minimum_wage
                else:
                    social_class.wage = max(
                        social_class.wage, self.sm.others_minimum_wage
                    )
        if self.government.real_resources["land"] > 0:
            if hasattr(self.government, "employees"):
                del self.government.employees
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
            if employees > 0:
                social_class.wage_share = social_class.population / employees
            else:
                social_class.wage_share = 0

        max_employees = sum([social_class.max_employees
                             for social_class
                             in employers_classes])
        if max_employees < employees:
            employees = max_employees
        self.emp_ratio = employees / max_employees

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
                                 employees: int, emp_ratio: float):
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
            if employer.employees < emp_ratio * employer.max_employees:
                employer.increase_wage = True
            else:
                employer.increase_wage = False

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
            if total_employees > 0:
                employer.profit_share = employer.employees / total_employees
            else:
                employer.profit_share = 0

    def _get_monetary_value(self, resources):
        """
        Returns the monetary value, at the current prices, of the given
        resources.
        """
        return sum((self.prices * resources).values())

    def _distribute_produced_and_used(self, employers_classes,
                                      employees_classes, produced, used):
        """
        Distributes the produced and used resources among employers and
        employees.
        """
        total_employers_share = EMPTY_RESOURCES.copy()

        full_value = self._get_monetary_value(produced)
        used_value = self._get_monetary_value(used)
        if full_value > 0:
            self.max_wage = 1 - used_value / full_value
        else:
            self.max_wage = 1

        for employer in employers_classes:
            share = produced * employer.profit_share * (1 - employer.wage)
            employer.new_resources += share
            total_employers_share += share

            employer.new_resources -= used * employer.profit_share

            del employer.profit_share

        produced -= total_employers_share
        for employee in employees_classes:
            employee.new_resources += produced * employee.wage_share

    def _set_new_wages(self, employers_classes):
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
            employers_classes, employees, self.emp_ratio
        )
        _State_Data_Employment_and_Commands._employees_to_profit(
            employers_classes
        )

        self._distribute_produced_and_used(
            employers_classes, employees_classes, produced, used
        )
        self._set_new_wages(employers_classes)

    def do_transfer(self, class_name: str, resource: str, amount: int,
                    demote: bool = True):
        """
        Moves resources between the government and a social class.
        """
        class_index = CLASS_NAME_TO_INDEX[class_name]

        res = self.government.new_resources
        res[resource] -= amount
        self.government.new_resources = res

        res = self.classes[class_index].new_resources
        res[resource] += amount
        self.classes[class_index].new_resources = res

        res_price = -amount * self.prices[resource]

        self.classes[class_index].happiness += \
            Class.resources_seized_happiness(
                res_price / self.classes[class_index].population
            )

        if demote:
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

    def do_set_law(self, law: str, argument: str | None, value: float):
        """
        Sets the given law to the given value.
        """
        try:
            if law == "tax_personal":
                self.sm.tax_rates['personal'][argument] = value
            elif law == "tax_property":
                self.sm.tax_rates['property'][argument] = value
            elif law == "tax_income":
                self.sm.tax_rates['income'][argument] = value
            elif law == "wage_minimum":
                self.sm.others_minimum_wage = value
            elif law == "wage_government":
                self.government.wage = value
                if hasattr(self.government, "old_wage"):
                    del self.government.old_wage
            elif law == "wage_autoregulation":
                self.government.wage_autoregulation = bool(value)
                if hasattr(self.government, "old_wage"):
                    self.government.wage = self.government.old_wage
            elif law == "max_prices":
                self.sm.max_prices[argument] = value
            else:
                raise InvalidCommandError
        except KeyError:
            raise InvalidCommandError

    def do_force_promotion(self, class_name: str, number: int):
        """
        Promotes the given number of people to the given class using
        government resources.
        """
        class_to = self.classes[CLASS_NAME_TO_INDEX[class_name]]
        class_from = class_to.lower_class
        removal_res = INBUILT_RESOURCES[class_from.class_name] * number
        addition_res = INBUILT_RESOURCES[class_name] * number

        class_from.new_population -= number
        class_from.new_resources -= removal_res

        class_to.new_resources += addition_res
        class_to.new_population += number

        self.government.new_resources -= addition_res - removal_res

        self._secure_classes()

    def do_recruit(self, class_name: str, number: int):
        """
        Recruits the given number of people from the given social class to the
        military.
        """
        class_from = self.classes[CLASS_NAME_TO_INDEX[class_name]]
        soldier_type = CLASS_TO_SOLDIER[class_name]
        cost = RECRUITMENT_COST[soldier_type] * number

        class_from.new_population -= number

        self.government.new_resources -= cost
        self.government.soldiers[soldier_type] += number

        self._secure_classes()

    @staticmethod
    def _get_battle_losses(ally_to_enemy_ratio: float) -> tuple[float, float]:
        """
        From the ratio of allied army strength to enemy army strength
        calculates and returns ally and enemy losses.
        Return: (ally_losses, enemy_losses)
        Losses are given as a fraction of the beginning army, between 0 and 1.
        """
        x = ally_to_enemy_ratio

        def div(y, z):
            if z != 0:
                return y / z
            else:
                return inf

        # a is a coefficient of the function
        # It is calculated so that a ratio of 1 gives exactly base losses
        a = (1 - BASE_BATTLE_LOSSES) / BASE_BATTLE_LOSSES
        # The whole function (ally losses) is designed so that:
        # It's increasing for all nonnegative ratios
        # For ratio 0 it returns 1
        # For ratio float positive infinity returns 0
        # Enemy losses function is the same, but the argument is reversed (1/x)
        return 1 / (a * x + 1), 1 / (div(a, x) + 1)

    def do_fight(self, target: str, enemies: int = None)\
            -> tuple[bool, Arithmetic_Dict[str, float], float]:
        """
        Executes an attack against the given target.
        Return is a 3-tuple: (victory?, dead_soldiers, profits)
        Meaning of profits float depends on the target:
            crime - profits is number of dead brigands
            conquest - profits is amount of land conquered
            plunder - profits is amount of resources (except land) gained
        """
        ally_strength = self.government.soldiers_fighting_strength
        if target == "crime":
            enemy_strength = self.brigands * self.brigand_strength
            ratio = ally_strength / enemy_strength \
                if enemy_strength > 0 else inf
            ally_losses, enemy_losses = self._get_battle_losses(ratio)

            dead_soldiers = self.government.soldiers * ally_losses
            self.government.soldiers *= (1 - ally_losses)
            dead_brigands = self.brigands * enemy_losses
            self.brigands *= (1 - enemy_losses)

            return ally_losses < enemy_losses, dead_soldiers, dead_brigands

        elif target == "conquest":
            ratio = ally_strength / enemies
            ally_losses, enemy_losses = self._get_battle_losses(ratio)

            dead_soldiers = self.government.soldiers * ally_losses
            self.government.soldiers *= (1 - ally_losses)
            gains = EMPTY_RESOURCES.copy()
            if enemy_losses > ally_losses:
                gains["land"] = enemy_losses * PLUNDER_FACTOR
            self.government.new_resources += gains
            self.government.flush()

            return ally_losses < enemy_losses, dead_soldiers, gains["land"]

        elif target == "plunder":
            ratio = ally_strength / enemies
            ally_losses, enemy_losses = self._get_battle_losses(ratio)

            dead_soldiers = self.government.soldiers * ally_losses
            self.government.soldiers *= (1 - ally_losses)
            gains = {
                "food": enemy_losses * PLUNDER_FACTOR,
                "wood": enemy_losses * PLUNDER_FACTOR,
                "stone": enemy_losses * PLUNDER_FACTOR,
                "iron": enemy_losses * PLUNDER_FACTOR,
                "tools": enemy_losses * PLUNDER_FACTOR,
                "land": 0
            }
            self.government.new_resources += gains
            self.government.flush()

            return ally_losses < enemy_losses, dead_soldiers, gains["food"]

    def execute_commands(self, commands: list[str]):
        """
        Executes the given commands.
        Format: [
            "<command> <argument> <argument> ...",
            "<command> <argument> <argument> ...",
            ...
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
            elif command[0] == "promote":
                self.do_force_promotion(command[1], int(command[2]))
            elif command[0] == "recruit":
                self.do_recruit(command[1], int(command[2]))
            elif command[0] == "fight":
                if command[2] == "None":
                    command[2] = None
                else:
                    command[2] = int(command[2])
                self.do_fight(command[1], command[2])
            else:
                raise InvalidCommandError
