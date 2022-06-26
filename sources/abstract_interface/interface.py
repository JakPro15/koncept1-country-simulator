from sources.auxiliaries.constants import CLASS_NAME_TO_INDEX, DEBUG_MODE
from ..state.state_data import State_Data
from .history import History
import json


class NotEnoughGovtResources(Exception):
    pass


class NotEnoughClassResources(Exception):
    pass


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
        starting_state_file_name = "saves/" + dirname + "/starting_state.json"
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

    def save_data(self, dirname):
        """
        Saves the game state into the given directory.
        """
        starting_state_file_name = "saves/" + dirname + "/starting_state.json"
        with open(starting_state_file_name, 'w') as save_file:
            json.dump(self.history.starting_state_dict, save_file, indent=4)

        history_file_name = "saves/" + dirname + "/history.txt"
        with open(history_file_name, 'w') as save_file:
            for line in self.history.history_lines:
                save_file.write(line + '\n')

    def next_month(self):
        """
        Advances the month by one and saves it in history.
        """
        self.state.do_month(DEBUG_MODE)
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
