import json
from .state_data import State_Data
from .history import History
from copy import deepcopy


class Interface:
    """
    Handles State_Data and subclasses communicating with the outside world.
    Properties:
    state - the State_Data object the interface handles
    history - history of the State_Data object
    """
    def __init__(self):
        self.history = History()

    def load_data(self, filename):
        with open(filename, 'r') as load_file:
            data = json.load(load_file)
            self.state = State_Data()
            self.state.from_dict(data["state"])
            self.history = History(data["history"])

    def save_data(self, filename):
        with open(filename, 'w') as save_file:
            data = {
                "state": self.state.to_dict(),
                "history": self.history.to_list()
            }
            json.dump(data, save_file, indent=4)

    def next_month(self):
        month_data = self.state.do_month()
        self.history.append(deepcopy(month_data))
