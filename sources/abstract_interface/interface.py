from sources.auxiliaries.constants import CLASS_NAME_TO_INDEX, CLASSES
from ..state.state_data import State_Data
from .history import History
from math import inf
import json


class NotEnoughGovtResources(Exception):
    pass


class NotEnoughClassResources(Exception):
    pass


class SaveAccessError(Exception):
    pass


class MalformedSaveError(Exception):
    pass


class Interface:
    """
    Handles State_Data and subclasses communicating with the outside world.
    Properties:
    state - the State_Data object the interface handles
    history - History of the State_Data object
    """
    def __init__(self, dirname=None, debug=False):
        if dirname is not None:
            self.load_data(dirname)
        self.debug = debug

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
                history_lines = []
                for line in load_file:
                    history_lines.append(line)

            self.history = History(starting_state, history_lines)
            self.state.execute_commands(history_lines)
            self.state.debug = self.debug
        except IOError:
            raise SaveAccessError
        except Exception:
            raise MalformedSaveError

    def save_data(self, dirname):
        """
        Saves the game state into the given directory.
        """
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
        self.history.add_history_line("next")

    def transfer_resources(self, class_name: str, resource: str, amount: int):
        """
        Transfers the given amount of a resource from government to the given
        class. Negative amount signifies a reverse direction of the transfer.
        """
        class_index = CLASS_NAME_TO_INDEX[class_name]
        if self.state.government.real_resources[resource] < amount:
            raise NotEnoughGovtResources
        if self.state.classes[class_index].real_resources[resource] < -amount:
            raise NotEnoughClassResources

        self.state.do_transfer(class_name, resource, amount)

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
        assert amount >= 0

        self.state.do_optimal(resource, amount)

        self.history.add_history_line(
            f"optimal {resource} {amount}"
        )

    def set_law(self, law: str, social_class: str | None, value: float):
        """
        Sets the given law to the given value.
        """
        laws = {
            "tax_personal": ((0, inf), True),
            "tax_property": ((0, 1), True),
            "tax_income": ((0, 1), True),
            "wages": ((0, 1), False)
        }
        assert laws[law][0][0] <= value <= laws[law][0][1]
        if laws[law][1]:
            assert social_class in CLASSES
        else:
            assert social_class is None

        self.state.do_set_law(law, social_class, value)

        self.history.add_history_line(
            f"laws set {law} {social_class} {value}"
        )
