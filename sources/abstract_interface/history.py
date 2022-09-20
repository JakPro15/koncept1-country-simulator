from typing import Any, Hashable, TypeVar

from ..state.state_data import State_Data
from ..state.state_data_base_and_do_month import Month_Data


class History:
    """
    Stores and handles the history of the state.
    Attributes:
    starting_state_dict - dict representing the starting state
                          (loaded from starting_state.json)
    history_lines - list of commands inputted by the user necessary to
                    remake the history of the state
    """
    def __init__(self, starting_state_dict: dict[str, Any],
                 history_lines: list[str]) -> None:
        """
        Creates an object storing and dispensing the history of the state.
        starting_state_dict - dict representing the starting state
                            (loaded from starting_state.json)
        history_lines - list of commands inputted by the user necessary to
                        remake the history of the state
        """
        self.starting_state_dict: dict[str, Any] = starting_state_dict.copy()
        self.history_lines: list[str] = history_lines.copy()

    def obtain_whole_history(self) -> list[Month_Data]:
        """
        Returns the whole history of the country.
        """
        result: list[Month_Data] = []

        state = State_Data.from_dict(self.starting_state_dict)
        for line in self.history_lines:
            command = line.split(' ')
            if command[0] == "next":
                amount = int(command[1])
                for _ in range(amount):
                    result.append(state.do_month())
            else:
                state.execute_commands([line])
        return result

    Key1 = TypeVar("Key1", bound=Hashable)
    Key2 = TypeVar("Key2", bound=Hashable)
    T = TypeVar("T")

    def population(self) -> list[dict[str, float]]:
        """
        Returns data about the state's social classes' populations over the
        months.
        """
        data = self.obtain_whole_history()
        return [month_data["population_after"] for month_data in data]

    def resources(self) -> list[dict[str, dict[str, float]]]:
        """
        Returns data about the state's social classes' and government's
        resources over the months.
        """
        data = self.obtain_whole_history()
        return [month_data["resources_after"] for month_data in data]

    def population_change(self) -> list[dict[str, float]]:
        """
        Returns data about the changes in the state's social classes'
        populations over the months.
        """
        data = self.obtain_whole_history()
        return [month_data["change_population"] for month_data in data]

    def resources_change(self) -> list[dict[str, dict[str, float]]]:
        """
        Returns data about the changes in the state's social classes'
        and government's resources over the months.
        """
        data = self.obtain_whole_history()
        return [month_data["change_resources"] for month_data in data]

    def prices(self) -> list[dict[str, float]]:
        """
        Returns data about the state's prices over the months.
        """
        data = self.obtain_whole_history()
        return [month_data["prices"] for month_data in data]

    def total_resources(self) -> list[dict[str, float]]:
        """
        Returns data about the state's total resources over the months.
        """
        data = self.obtain_whole_history()
        result: list[dict[str, float]] = []
        for month_data in data:
            res_after = month_data["resources_after"]
            total_res: dict[str, float] = {
                "food": 0,
                "wood": 0,
                "stone": 0,
                "iron": 0,
                "tools": 0,
                "land": 0
            }
            for resources in res_after.values():
                for res, val in resources.items():
                    total_res[res] += val
            result.append(total_res)
        return result

    def growth_modifiers(self) -> list[dict[str, dict[str, bool]]]:
        """
        Returns data about the state's growth modifiers over the months.
        """
        data = self.obtain_whole_history()
        return [month_data["growth_modifiers"] for month_data in data]

    def employment(self) -> list[dict[str, tuple[float, float]]]:
        """
        Returns data about employment in the state over the months.
        The tuple contains the number of employees and their wages.
        """
        data = self.obtain_whole_history()
        results: list[dict[str, tuple[float, float]]] = []
        for month_data in data:
            merged: dict[str, tuple[float, float]] = {}
            for key in month_data["employees"]:
                merged[key] = (month_data["employees"][key],
                               month_data["wages"][key])
            results.append(merged)
        return results

    def happiness(self) -> list[dict[str, float]]:
        """
        Returns data about the state's social classes' happiness over the
        months.
        """
        data = self.obtain_whole_history()
        return [month_data["happiness"] for month_data in data]

    def add_history_line(self, command: str) -> None:
        """
        Adds the given command to the history.
        """
        if command == "next":
            split_command = command.split(' ')
            number = 1
            if len(split_command) > 1:
                number = int(split_command[1])

            if len(self.history_lines) == 0:
                self.history_lines.append(f'{command} {number}')
            else:
                if self.history_lines[-1].split(' ')[0] != "next":
                    self.history_lines.append(f'{command} {number}')
                else:
                    line = self.history_lines[-1].split(' ')
                    line[1] = str(int(line[1]) + number)
                    self.history_lines[-1] = ' '.join(line)
        else:
            self.history_lines.append(command)
