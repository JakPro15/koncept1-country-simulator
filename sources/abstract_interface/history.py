from ..state.state_data import State_Data
from ..auxiliaries.arithmetic_dict import Arithmetic_Dict


class History:
    """
    Stores and handles the history of the state.
    Attributes:
    starting_state_dict - dict representing the starting state
                          (loaded from starting_state.json)
    history_lines - list of commands inputted by the user necessary to
                    remake the history of the state
    """
    def __init__(self, starting_state_dict, history_lines):
        self.starting_state_dict = starting_state_dict.copy()
        self.history_lines = history_lines.copy()
        self.keys_info = {
            # "key": (double_dict?, round_digits, new_key_if_total)
            "population_after": (False, 0, None),
            "resources_after": (True, 1, None),
            "change_population": (False, 0, None),
            "change_resources": (True, 1, None),
            "prices": (False, 4, None),
            "total_resources": (False, 1, "resources_after"),
            "growth_modifiers": (None, 0, None),
            "employees": (False, 0, None),
            "wages": (False, 2, None),
            "happiness": (False, 2, None)
        }

    def obtain_data(self, keys: list[str]):
        """
        Returns the data about the keys from the whole history of the country.
        """
        result = {key: [] for key in keys}

        state = State_Data.from_dict(self.starting_state_dict)
        for line in self.history_lines:
            command = line.split(' ')
            if command[0] == "next":
                amount = int(command[1])
                for _ in range(amount):
                    month_data = state.do_month()
                    for key in keys:
                        old_key = key
                        double_dict = self.keys_info[key][0]
                        ndigits = self.keys_info[key][1]
                        total = self.keys_info[key][2]
                        if total:
                            key = self.keys_info[key][2]

                        key_data = month_data[key]

                        if total:
                            new_data = {}
                            for dicti in key_data.values():
                                for key2 in dicti:
                                    if key2 in new_data:
                                        new_data[key2] += dicti[key2]
                                    else:
                                        new_data[key2] = dicti[key2]
                            key_data = new_data
                            double_dict = False

                        if double_dict is not None:
                            if double_dict:
                                key_data = History.round_dict_of_dicts_values(
                                    key_data, ndigits
                                )
                            else:
                                key_data = Arithmetic_Dict(key_data)
                                key_data = key_data.round(ndigits)

                        result[old_key].append(key_data)
            else:
                state.execute_commands([line])
        return result

    @staticmethod
    def round_dict_of_dicts_values(dictionary, ndigits=0):
        result = dictionary.copy()
        for key in result:
            result[key] = Arithmetic_Dict(result[key])
            result[key] = result[key].round(ndigits)
        return result

    def population(self):
        return self.obtain_data(["population_after"])["population_after"]

    def resources(self):
        return self.obtain_data(["resources_after"])["resources_after"]

    def population_change(self):
        return self.obtain_data(["change_population"])["change_population"]

    def resources_change(self):
        return self.obtain_data(["change_resources"])["change_resources"]

    def prices(self):
        return self.obtain_data(["prices"])["prices"]

    def total_resources(self):
        return self.obtain_data(["total_resources"])["total_resources"]

    def growth_modifiers(self):
        return self.obtain_data(["growth_modifiers"])["growth_modifiers"]

    def employment(self):
        return self.obtain_data(["employees", "wages"])

    def happiness(self):
        return self.obtain_data(["happiness"])["happiness"]

    def add_history_line(self, command):
        """
        Adds the given command to the history lines. The given command should
        be a singular command (for example "next 3" won't work properly).
        """
        if command == "next":
            if len(self.history_lines) == 0:
                self.history_lines.append(f'{command} 1')
            else:
                if self.history_lines[-1].split(' ')[0] != command:
                    self.history_lines.append(f'{command} 1')
                else:
                    line = self.history_lines[-1].split(' ')
                    line[1] = str(int(line[1]) + 1)
                    self.history_lines[-1] = ' '.join(line)
        else:
            self.history_lines.append(command)
