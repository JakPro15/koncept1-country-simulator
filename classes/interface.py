import json
from state_data import State_Data


class Interface:
    """
    Handles State_Data and subclasses communicating with the outside world.
    Properties:
    state - the State_Data object the interface handles
    """
    def __init__(self):
        pass

    def load_data(self, filename):
        with open(filename, 'r') as load_file:
            data = json.load(load_file)
            self.state = State_Data()
            self.state.from_dict(data["state"])

    def save_data(self, filename):
        with open(filename, 'w') as save_file:
            data = self.state.to_dict()
            json.dump(data, save_file)
