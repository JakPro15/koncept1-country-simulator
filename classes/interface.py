import json
from .state_data import State_Data
from .history import History


class Interface:
    """
    Handles State_Data and subclasses communicating with the outside world.
    Properties:
    state - the State_Data object the interface handles
    history - history of the State_Data object
    """
    def __init__(self):
        self.history = History()

    def load_data(self, dirname):
        state_file_name = "saves/" + dirname + "/state.json"
        with open(state_file_name, 'r') as load_file:
            data = json.load(load_file)
            self.state = State_Data()
            self.state.from_dict(data)

        starting_state_file_name = "saves/" + dirname + "/starting_state.json"
        with open(starting_state_file_name, 'r') as load_file:
            starting_state = json.load(load_file)

        history_file_name = "saves/" + dirname + "/history.txt"
        with open(history_file_name, 'r') as load_file:
            history_lines = []
            for line in load_file:
                history_lines.append(line)

        self.history = History(starting_state, history_lines)

    def save_data(self, dirname):
        state_file_name = "saves/" + dirname + "/state.json"
        with open(state_file_name, 'w') as save_file:
            json.dump(save_file, self.state.to_dict(), indent=4)

        starting_state_file_name = "saves/" + dirname + "/starting_state.json"
        with open(starting_state_file_name, 'w') as save_file:
            json.dump(save_file, self.history.starting_state_dict, indent=4)

        history_file_name = "saves/" + dirname + "/history.txt"
        with open(history_file_name, 'w') as save_file:
            for line in self.history.history_lines:
                save_file.write(line + '\n')

    def next_month(self):
        self.state.do_month()
        if len(self.history.history_lines) == 0:
            self.history.history_lines.append('next 1')
        else:
            if self.history.history_lines[-1].split(' ')[0] != "next":
                self.history.history_lines.append('next 1')
            else:
                command = self.history.history_lines[-1].split(' ')
                command[1] = str(int(command[1]) + 1)
                self.history.history_lines[-1] = ' '.join(command)
