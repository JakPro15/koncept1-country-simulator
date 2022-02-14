class History(list):
    """
    Stores and handles the history of the state.
    """
    def to_list(self):
        return [month for month in self]

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
        return [
            History.round_dict_values(month["population_after"])
            for month
            in self
        ]

    def resources_stats(self):
        return [
            History.round_dict_of_dicts_values(month["resources_after"], 2)
            for month
            in self
        ]

    def growth_modifiers_stats(self):
        return [
            History.round_dict_values(month["growth_modifiers"], 4)
            for month
            in self
        ]

    def growth_stats(self):
        return [
            History.round_dict_values(month["grown"], 2)
            for month
            in self
        ]

    def production_stats(self):
        return [
            History.round_dict_values(month["produced"], 2)
            for month
            in self
        ]

    def usage_stats(self):
        return [
            History.round_dict_values(month["used"], 2)
            for month
            in self
        ]

    def consumption_stats(self):
        return [
            History.round_dict_values(month["consumed"], 2)
            for month
            in self
        ]

    def prices_stats(self):
        return [
            History.round_dict_values(month["prices"], 4)
            for month
            in self
        ]
