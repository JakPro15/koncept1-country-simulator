from sources.auxiliaries.constants import (
    CLASS_NAME_TO_INDEX, CLASS_TO_SOLDIER, CLASSES, INBUILT_RESOURCES,
    RESOURCES, RECRUITMENT_COST
)
from ..state.state_data import State_Data
from .history import History
import json
from math import log10, floor
from random import gauss


class NotEnoughGovtResources(Exception):
    pass


class NotEnoughClassResources(Exception):
    pass


class NotEnoughClassPopulation(Exception):
    pass


class EmptyClassError(Exception):
    pass


class SaveAccessError(Exception):
    pass


class MalformedSaveError(Exception):
    pass


class InvalidArgumentError(Exception):
    pass


def check_input(condition, desc):
    if not condition:
        raise InvalidArgumentError(desc)


class Interface:
    """
    Handles State_Data and subclasses communicating with the outside world.
    Properties:
    state - the State_Data object the interface handles
    history - History of the State_Data object
    """
    def __init__(self, dirname=None):
        if dirname is not None:
            self.load_data(dirname)

    def load_data(self, dirname):
        """
        Loads a game state from the given directory.
        """
        try:
            starting_state_file_name = \
                "saves/" + dirname + "/starting_state.json"
            with open(starting_state_file_name, 'r') as load_file:
                starting_state = json.load(load_file)

            self.state = State_Data.from_dict(starting_state)

            history_file_name = "saves/" + dirname + "/history.txt"
            with open(history_file_name, 'r') as load_file:
                history_lines = load_file.read().splitlines()

            self.history = History(starting_state, history_lines)
            self.state.execute_commands(history_lines)
            self.save_name = dirname if dirname != "starting" else ""
        except IOError:
            raise SaveAccessError
        except Exception:
            raise MalformedSaveError

    def save_data(self, dirname: str | None = None):
        """
        Saves the game state into the given directory.
        """
        if not dirname:
            dirname = self.save_name
        try:
            starting_state_file_name = \
                "saves/" + dirname + "/starting_state.json"
            with open(starting_state_file_name, 'w') as save_file:
                json.dump(
                    self.history.starting_state_dict, save_file, indent=4
                )

            history_file_name = "saves/" + dirname + "/history.txt"
            with open(history_file_name, 'w') as save_file:
                for line in self.history.history_lines:
                    save_file.write(line + '\n')
        except IOError:
            raise SaveAccessError

    def next_month(self):
        """
        Advances the month by one and saves it in history.
        """
        self.state.do_month()
        self.state.fought = False
        self.history.add_history_line("next")

    def transfer_resources(self, class_name: str, resource: str, amount: int,
                           demote: bool = True):
        """
        Transfers the given amount of a resource from government to the given
        class. Negative amount signifies a reverse direction of the transfer.
        """
        class_index = CLASS_NAME_TO_INDEX[class_name]
        if self.state.classes[class_index].population == 0:
            raise EmptyClassError
        if self.state.government.real_resources[resource] < amount:
            raise NotEnoughGovtResources
        if self.state.classes[class_index].real_resources[resource] < -amount:
            raise NotEnoughClassResources

        self.state.do_transfer(class_name, resource, amount, demote)

        self.history.add_history_line(
            f"transfer {class_name} {resource} {amount}"
        )

    def secure_resources(self, resource: str, amount: int | None):
        """
        Makes the given amount of a resource owned by the government
        untradeable (secured). Negative amount signifies making a resource
        tradeable again.
        """
        if amount is None:
            amount = self.state.government.new_resources[resource]

        if self.state.government.new_resources[resource] < amount or \
           self.state.government.secure_resources[resource] < -amount:
            raise NotEnoughGovtResources

        self.state.do_secure(resource, amount)

        self.history.add_history_line(
            f"secure {resource} {amount}"
        )

    def set_govt_optimal(self, resource: str, amount: int):
        """
        Sets government's optimal resource to the given value.
        """
        check_input(amount >= 0, "negative optimal resources")

        self.state.do_optimal(resource, amount)

        self.history.add_history_line(
            f"optimal {resource} {amount}"
        )

    def set_law(self, law: str, argument: str | None, value: float):
        """
        Sets the given law to the given value.
        """
        laws_conditions = {
            "tax_personal": (lambda val: 0 <= val,
                             lambda arg: arg in CLASSES),
            "tax_property": (lambda val: 0 <= val <= 1,
                             lambda arg: arg in CLASSES),
            "tax_income": (lambda val: 0 <= val <= 1,
                           lambda arg: arg in CLASSES),
            "wage_minimum": (lambda val: 0 <= val <= 1,
                             lambda arg: arg is None),
            "wage_government": (lambda val: 0 <= val <= 1,
                                lambda arg: arg is None),
            "wage_autoregulation": (lambda val: val in {0, 1},
                                    lambda arg: arg is None),
            "max_prices": (lambda val: 1 <= val,
                           lambda arg: arg in RESOURCES),
        }
        check_input(laws_conditions[law][0](value), "invalid law value")
        check_input(laws_conditions[law][1](argument), "invalid law argument")

        self.state.do_set_law(law, argument, value)

        self.history.add_history_line(
            f"laws set {law} {argument} {value}"
        )

    def force_promotion(self, class_name: str, number: int):
        """
        Promotes the given number of people to the given class using
        government resources.
        """
        check_input(number >= 0, "negative number of people")
        class_index = CLASS_NAME_TO_INDEX[class_name]
        lower_class = self.state.classes[class_index].lower_class

        if lower_class.population < number:
            raise NotEnoughClassPopulation
        if self.state.government.real_resources < (
             INBUILT_RESOURCES[class_name] -
             INBUILT_RESOURCES[lower_class.class_name]) * number:
            raise NotEnoughGovtResources

        self.state.do_force_promotion(class_name, number)

        self.history.add_history_line(
            f"promote {class_name} {number}"
        )

    def recruit(self, class_name: str, number: int):
        """
        Recruits the given number of people from the given social class to the
        military.
        """
        check_input(number >= 0, "negative number of people")
        class_index = CLASS_NAME_TO_INDEX[class_name]
        soldier_type = CLASS_TO_SOLDIER[class_name]

        if self.state.classes[class_index].population < number:
            raise NotEnoughClassPopulation
        if self.state.government.real_resources < \
           RECRUITMENT_COST[soldier_type] * number:
            raise NotEnoughGovtResources

        self.state.do_recruit(class_name, number)

        self.history.add_history_line(
            f"recruit {class_name} {number}"
        )

    def get_brigands(self, debug=__debug__):
        """
        Returns the number of brigands and their strength, estimated if debug
        mode is off.
        """
        brigands = self.state.brigands
        strength = self.state.brigand_strength
        if not debug:
            estimation = max(floor(log10(max(1, brigands))), 1)
            uncertainty = 10 ** estimation / 2
            brigands += uncertainty
            brigands = round(brigands + 0.0000001, -estimation)
            brigands -= uncertainty
            brigands = (int(brigands - uncertainty),
                        int(brigands + uncertainty))
            strength *= 2
            strength = floor(strength)
            strength /= 2
            strength = (strength, strength + 0.5)
        return brigands, strength

    def fight(self, target: str):
        """
        Executes an attack against the given target.
        """
        enemies = max(floor(gauss(100, 20)), 10) if target != "crime" else None
        results = self.state.do_fight(target, enemies)
        self.state.fought = True

        self.history.add_history_line(
            f"fight {target} {enemies}"
        )
        return results
