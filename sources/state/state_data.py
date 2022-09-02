from __future__ import annotations

from math import inf

from ..auxiliaries.constants import (BASE_BATTLE_LOSSES, CLASS_TO_SOLDIER,
                                     INBUILT_RESOURCES, PLUNDER_FACTOR,
                                     RECRUITMENT_COST)
from ..auxiliaries.enums import Class_Name, Resource
from ..auxiliaries.resources import Resources
from ..auxiliaries.soldiers import Soldiers
from .social_classes.class_file import Class
from .state_data_employ_and_commands import State_Data_Creation_And_Do_Month


class InvalidCommandError(ValueError):
    """
    Raised when a command method is called with wrong arguments.
    """


class State_Data(State_Data_Creation_And_Do_Month):
    """
    Represents the data of an entire state, including all its classes.
    Properties:
    month - the current month
    classes - social classes of the country
    government - government of the country's object
    _market - object executing trade within the country
    prices - last month's resource prices on the market
    """
    def do_transfer(self, class_name: Class_Name, resource: Resource,
                    amount: float, demote: bool = True) -> None:
        """
        Moves resources between the government and a social class.
        demote should be given False only if another transfer is coming up.
        """
        self.government.resources[resource] -= amount

        self.classes[class_name].resources[resource] += amount

        res_price = -amount * self.prices[resource]

        self.classes[class_name].happiness += \
            Class.resources_seized_happiness(
                res_price / self.classes[class_name].population
            )

        if demote:
            self._do_demotions()
            self._secure_classes()

    def do_secure(self, resource: Resource, amount: float) -> None:
        """
        Makes the given amount of a resource owned by the government
        untradeable (secured). Negative amount signifies making a resource
        tradeable again.
        """
        self.government.resources[resource] -= amount
        self.government.secure_resources[resource] += amount

        self.government.validate()

    def do_optimal(self, resource: Resource, amount: float) -> None:
        """
        Sets government's optimal resource to the given value.
        """
        self.government.optimal_resources[resource] = amount

    def do_set_law(self, law: str, argument: str | None, value: float) -> None:
        """
        Sets the given law to the given value.
        """
        try:
            if law == "tax_personal":
                assert argument is not None
                self.sm.tax_rates['personal'][Class_Name[argument]] = value
            elif law == "tax_property":
                assert argument is not None
                self.sm.tax_rates['property'][Class_Name[argument]] = value
            elif law == "tax_income":
                assert argument is not None
                self.sm.tax_rates['income'][Class_Name[argument]] = value
            elif law == "wage_minimum":
                self.sm.others_minimum_wage = value
            elif law == "wage_government":
                self.government.wage = value
                try:
                    del self.government.old_wage
                except AttributeError:
                    pass
            elif law == "wage_autoregulation":
                self.government.wage_autoregulation = bool(value)
                self.government.wage = self.government.old_wage

            elif law == "max_prices":
                assert argument is not None
                self.sm.max_prices[Resource[argument]] = value
            else:
                raise InvalidCommandError
        except (KeyError, AssertionError, InvalidCommandError) as e:
            raise InvalidCommandError("do_set_law argument(s) invalid") from e

    def do_force_promotion(self, class_name: Class_Name, number: float
                           ) -> None:
        """
        Promotes the given number of people to the given class using
        government resources.
        """
        class_to = self.classes[class_name]
        class_from = class_to.lower_class
        removal_res = INBUILT_RESOURCES[class_from.class_name] * number
        addition_res = INBUILT_RESOURCES[class_name] * number

        class_from.population -= number
        class_from.resources -= removal_res

        class_to.resources += addition_res
        class_to.population += number

        self.government.resources -= addition_res - removal_res

        self._secure_classes()

    def do_recruit(self, class_name: Class_Name, number: float):
        """
        Recruits the given number of people from the given social class to the
        military.
        """
        class_from = self.classes[class_name]
        soldier_type = CLASS_TO_SOLDIER[class_name]
        cost = RECRUITMENT_COST[soldier_type] * number

        class_from.population -= number

        self.government.resources -= cost
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

        def div(y: float, z: float) -> float:
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

    def do_fight(self, target: str, enemies: float | None = None
                 ) -> tuple[bool, Soldiers, float]:
        """
        Executes an attack against the given target.
        Return is a 3-tuple: (victory?, dead_soldiers, profits)
        Meaning of profits float depends on the target:
            crime - profits is number of dead brigands
            conquest - profits is amount of land conquered
            plunder - profits is amount of resources (except land) gained
        """
        ally_strength = self.government.soldiers.strength
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
            if enemies is None:
                raise InvalidCommandError(
                    "do_fight conquest enemies argument is None"
                )
            ratio = ally_strength / enemies
            ally_losses, enemy_losses = self._get_battle_losses(ratio)

            dead_soldiers = self.government.soldiers * ally_losses
            self.government.soldiers *= (1 - ally_losses)
            gains = Resources()
            if enemy_losses > ally_losses:
                gains.land = enemy_losses * PLUNDER_FACTOR
            self.government.resources += gains

            return ally_losses < enemy_losses, dead_soldiers, gains.land

        elif target == "plunder":
            if enemies is None:
                raise InvalidCommandError(
                    "do_fight plunder enemies argument is None"
                )
            ratio = ally_strength / enemies
            ally_losses, enemy_losses = self._get_battle_losses(ratio)

            dead_soldiers = self.government.soldiers * ally_losses
            self.government.soldiers *= (1 - ally_losses)
            gains = Resources(enemy_losses * PLUNDER_FACTOR)
            del gains[Resource.land]
            self.government.resources += gains

            return ally_losses < enemy_losses, dead_soldiers, gains.food

        else:
            raise InvalidCommandError("do_fight target argument invalid")

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
                self.do_transfer(Class_Name[command[1]], Resource[command[2]],
                                 float(command[3]))
            elif command[0] == "secure":
                self.do_secure(Resource[command[1]], int(command[2]))
            elif command[0] == "optimal":
                self.do_optimal(Resource[command[1]], int(command[2]))
            elif command[0] == "laws" and command[1] == "set":
                self.do_set_law(
                    command[2], command[3] if command[3] != "None" else None,
                    float(command[4])
                )
            elif command[0] == "promote":
                self.do_force_promotion(Class_Name[command[1]],
                                        int(command[2]))
            elif command[0] == "recruit":
                self.do_recruit(Class_Name[command[1]], int(command[2]))
            elif command[0] == "fight":
                self.do_fight(
                    command[1],
                    int(command[2]) if command[2] != "None" else None
                )
            else:
                raise InvalidCommandError("execute_commands invalid command")
