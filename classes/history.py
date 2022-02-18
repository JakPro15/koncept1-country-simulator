from .state_data import State_Data


class History:
    """
    Stores and handles the history of the state.
    """
    def __init__(self, starting_state_dict, history_lines):
        self.starting_state_dict = starting_state_dict
        self.history_lines = history_lines

    def to_list(self):
        return [month for month in self]

    def obtain_data(self, key: str, double_dict: bool, ndigits=None):
        result = []

        state = State_Data()
        state.from_dict(self.starting_state_dict)
        for line in self.history_lines:
            command = line.split(' ')
            if command[0] == "next":
                amount = command[1]
                for _ in range(amount):
                    month_data = state.do_month()[key]
                    if double_dict:
                        month_data = History.round_dict_of_dicts_values(
                            month_data, ndigits
                        )
                    else:
                        month_data = History.round_dict_values(
                            month_data, ndigits
                        )
                    result.append(month_data)

    @staticmethod
    def round_dict_values(dictionary, ndigits=None):
        result = dictionary.copy()
        for key in result:
            result[key] = round(result[key], ndigits)
        return result

    @staticmethod
    def round_dict_of_dicts_values(dictionary, ndigits=None):
        result = dictionary.copy()
        for key in result:
            for key2 in result[key]:
                result[key][key2] = round(result[key][key2], ndigits)
        return result

    def population_stats(self):
        return self.obtain_data("population", False)

    def resources_stats(self):
        return self.obtain_data("resources_after", True, 2)

    def growth_modifiers_stats(self):
        return self.obtain_data("growth_modifiers", True, 4)

    def growth_stats(self):
        return self.obtain_data("grown", False, 2)

    def production_stats(self):
        return self.obtain_data("produced", True, 2)

    def usage_stats(self):
        return self.obtain_data("used", True, 2)

    def consumption_stats(self):
        return self.obtain_data("consumed", True, 2)

    def prices_stats(self):
        return self.obtain_data("trade_prices", False, 4)
