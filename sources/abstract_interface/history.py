from ..state.state_data import State_Data
from math import isnan, isinf


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

    def obtain_data(self, key: str, double_dict: bool, ndigits=0):
        result = []

        total = False
        if(key == "total_resources"):
            total = True
            key = "resources_after"

        state = State_Data.from_dict(self.starting_state_dict)
        for line in self.history_lines:
            command = line.split(' ')
            if command[0] == "next":
                amount = int(command[1])
                for _ in range(amount):
                    month_data = state.do_month()[key]

                    if total:
                        new_data = {}
                        for dicti in month_data.values():
                            for key2 in dicti:
                                if key2 in new_data:
                                    new_data[key2] += dicti[key2]
                                else:
                                    new_data[key2] = dicti[key2]
                        month_data = new_data
                        double_dict = False

                    if double_dict:
                        month_data = History.round_dict_of_dicts_values(
                            month_data, ndigits
                        )
                    else:
                        month_data = History.round_dict_values(
                            month_data, ndigits
                        )

                    result.append(month_data)
        return result

    @staticmethod
    def round_dict_values(dictionary, ndigits=0):
        result = dictionary.copy()
        for key in result:
            result[key] = round(result[key], ndigits)
            if ndigits > 0:
                result[key] = float(result[key])
            else:
                if not (isnan(result[key]) or isinf(result[key])):
                    result[key] = int(result[key])
                else:
                    result[key] = result[key]
        return result

    @staticmethod
    def round_dict_of_dicts_values(dictionary, ndigits=0):
        result = dictionary.copy()
        for key in result:
            for key2 in result[key]:
                result[key][key2] = round(result[key][key2], ndigits)
                if ndigits > 0:
                    result[key][key2] = float(result[key][key2])
                else:
                    result[key][key2] = int(result[key][key2])
        return result

    def population(self):
        return self.obtain_data("population_after", False)

    def resources(self):
        return self.obtain_data("resources_after", True, 1)

    def population_change(self):
        return self.obtain_data("population_change", False)

    def resources_change(self):
        return self.obtain_data("resources_change", True, 1)

    def prices(self):
        return self.obtain_data("prices", False, 4)

    def total_resources(self):
        return self.obtain_data("total_resources", False, 1)
