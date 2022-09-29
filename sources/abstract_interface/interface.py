import json
from math import floor, log10
from random import gauss
from typing import Callable, overload

from ..auxiliaries.constants import (CLASS_TO_SOLDIER, INBUILT_RESOURCES,
                                     RECRUITMENT_COST)
from ..auxiliaries.enums import (CLASS_NAME_STR, RESOURCE_STR, Class_Name,
                                 Resource)
from ..auxiliaries.soldiers import Soldiers
from ..state.state_data import State_Data
from .history import History


class NotEnoughGovtResources(Exception):
    pass


class NotEnoughClassResources(Exception):
    pass


class NotEnoughClassPopulation(Exception):
    pass


class EmptyClassError(Exception):
    pass


class SaveAccessError(Exception):
    pass


class MalformedSaveError(Exception):
    pass


class InvalidArgumentError(Exception):
    pass


class NoSoldiersError(Exception):
    pass


class AlreadyFoughtError(Exception):
    pass


def check_arg(condition: bool, desc: str) -> None:
    """
    Raises InvalidArgumentError with given description if condition is false.
    """
    if not condition:
        raise InvalidArgumentError(desc)


class Interface:
    """
    Handles State_Data and subclasses communicating with the outside world.
    Properties:
    state - the State_Data object the interface handles
    history - History of the State_Data object
    to_load can be a string - name of the save to be loaded, or
    a State_Data object directly (in this case the history is set to be
    empty). If None is given, a new State_Data object will be created for
    the Interface.
    """
    @overload
    def __init__(self, to_load: str, /) -> None:
        ...

    @overload
    def __init__(self, to_load: State_Data | None = None,
                 history: History | None = None, /) -> None:
        ...

    def __init__(self, to_load: str | State_Data | None = None,
                 history: History | None = None, /) -> None:
        """
        Creates an Interface for the given state.
        """
        if to_load is None:
            self.state = State_Data.generate_empty_state()
            self.history = History(self.state.to_dict(), [])
            self.save_name: str | None = None
            self.fought: bool = False
        elif isinstance(to_load, State_Data):
            self.state: State_Data = to_load
            if history is not None:
                self.history = history
            else:
                self.history: History = History(self.state.to_dict(), [])
            self.save_name: str | None = None
            self.fought: bool = False
        else:
            self.load_data(to_load)

    def load_data(self, dirname: str | None = None) -> None:
        """
        Loads a game state from the given directory. If None is given,
        self.save_name is loaded.
        """
        if not dirname:
            if self.save_name is None:
                raise ValueError("loaded save name cannot be empty")
            dirname = self.save_name
        try:
            starting_state_file_name = \
                "saves/" + dirname + "/starting_state.json"
            with open(starting_state_file_name, 'r',
                      encoding="utf-8") as load_file:
                starting_state = json.load(load_file)

            self.state = State_Data.from_dict(starting_state)

            history_file_name = "saves/" + dirname + "/history.txt"
            with open(history_file_name, 'r',
                      encoding="utf-8") as load_file:
                history_lines = load_file.read().splitlines()

            self.history = History(starting_state, history_lines)
            self.state.execute_commands(history_lines)
            if dirname != "starting":
                self.save_name = dirname
            self.fought = False
        except IOError as e:
            raise SaveAccessError from e
        except Exception as e:
            raise MalformedSaveError from e

    def save_data(self, dirname: str | None = None) -> None:
        """
        Saves the game state into the given directory.
        """
        if not dirname:
            if self.save_name is None:
                raise ValueError("save name cannot be empty")
            dirname = self.save_name
        try:
            starting_state_file_name = \
                "saves/" + dirname + "/starting_state.json"
            with open(starting_state_file_name, 'w',
                      encoding="utf-8") as save_file:
                json.dump(
                    self.history.starting_state_dict, save_file, indent=4
                )

            history_file_name = "saves/" + dirname + "/history.txt"
            with open(history_file_name, 'w',
                      encoding="utf-8") as save_file:
                for line in self.history.history_lines:
                    save_file.write(line + '\n')
        except IOError:
            raise SaveAccessError

    def next_month(self) -> None:
        """
        Advances the month by one and saves it in history.
        """
        self.state.do_month()
        self.fought = False
        self.history.add_history_line("next")

    def transfer_resources(self, class_name: Class_Name, resource: Resource,
                           amount: float, demote: bool = True) -> None:
        """
        Transfers the given amount of a resource from government to the given
        class. Negative amount signifies a reverse direction of the transfer.
        """
        if self.state.classes[class_name].population == 0:
            raise EmptyClassError
        if self.state.government.real_resources[resource] < amount:
            raise NotEnoughGovtResources
        if self.state.classes[class_name].real_resources[resource] < -amount:
            raise NotEnoughClassResources

        self.state.do_transfer(class_name, resource, amount, demote)

        self.history.add_history_line(
            f"transfer {class_name.name} {resource.name} {amount}"
        )

    def secure_resources(self, resource: Resource, amount: float | None
                         ) -> None:
        """
        Makes the given amount of a resource owned by the government
        untradeable (secured). Negative amount signifies making a resource
        tradeable again.
        """
        if amount is None:
            amount = self.state.government.resources[resource]

        if self.state.government.resources[resource] < amount or \
           self.state.government.secure_resources[resource] < -amount:
            raise NotEnoughGovtResources

        self.state.do_secure(resource, amount)

        self.history.add_history_line(
            f"secure {resource.name} {amount}"
        )

    def set_govt_optimal(self, resource: Resource, amount: float) -> None:
        """
        Sets government's optimal resource to the given value.
        """
        check_arg(amount >= 0, "negative optimal resources")

        self.state.do_optimal(resource, amount)

        self.history.add_history_line(
            f"optimal {resource.name} {amount}"
        )

    laws_conditions: dict[str, tuple[Callable[[float], bool],
                                     Callable[[str | None], bool]]] = {
        "tax_personal": (lambda val: 0 <= val,
                         lambda arg: arg in CLASS_NAME_STR),
        "tax_property": (lambda val: 0 <= val <= 1,
                         lambda arg: arg in CLASS_NAME_STR),
        "tax_income": (lambda val: 0 <= val <= 1,
                       lambda arg: arg in CLASS_NAME_STR),
        "wage_minimum": (lambda val: 0 <= val <= 1,
                         lambda arg: arg is None),
        "wage_government": (lambda val: 0 <= val <= 1,
                            lambda arg: arg is None),
        "wage_autoregulation": (lambda val: val in {0, 1},
                                lambda arg: arg is None),
        "max_prices": (lambda val: 1 <= val,
                       lambda arg: arg in RESOURCE_STR),
    }

    def set_law(self, law: str, argument: str | None, value: float) -> None:
        """
        Sets the given law to the given value.
        """
        check_arg(Interface.laws_conditions[law][0](value),
                  "invalid law value")
        check_arg(Interface.laws_conditions[law][1](argument),
                  "invalid law argument")

        self.state.do_set_law(law, argument, value)

        self.history.add_history_line(
            f"laws set {law} {argument} {value}"
        )

    def force_promotion(self, class_name: Class_Name, number: float) -> None:
        """
        Promotes the given number of people to the given class using
        government resources.
        """
        check_arg(number >= 0, "negative number of people")
        lower_class = self.state.classes[class_name].lower_class

        if lower_class.population < number:
            raise NotEnoughClassPopulation
        if self.state.government.real_resources < (
             INBUILT_RESOURCES[class_name] -
             INBUILT_RESOURCES[lower_class.class_name]) * number:
            raise NotEnoughGovtResources

        self.state.do_force_promotion(class_name, number)

        self.history.add_history_line(
            f"promote {class_name.name} {number}"
        )

    def recruit(self, class_name: Class_Name, number: float) -> None:
        """
        Recruits the given number of people from the given social class to the
        military.
        """
        check_arg(number >= 0, "negative number of people")
        soldier_type = CLASS_TO_SOLDIER[class_name]

        if self.state.classes[class_name].population < number:
            raise NotEnoughClassPopulation
        if self.state.government.real_resources < \
           RECRUITMENT_COST[soldier_type] * number:
            raise NotEnoughGovtResources

        self.state.do_recruit(class_name, number)

        self.history.add_history_line(
            f"recruit {class_name.name} {number}"
        )

    def get_brigands(
        self, debug: bool = __debug__
    ) -> tuple[float, float] | tuple[tuple[int, int], tuple[float, float]]:
        """
        Returns a tuple: number of brigands, their strength; estimated if debug
        mode is off.
        """
        brigands: float = self.state.brigands
        strength: float = self.state.brigands_strength
        if debug:
            return brigands, strength
        else:
            estimation = max(floor(log10(max(1, brigands))), 1)
            uncertainty = 10 ** estimation / 2
            brigands += uncertainty
            brigands = round(brigands + 0.0000001, -estimation)
            brigands -= uncertainty
            est_brigands = (int(brigands - uncertainty),
                            int(brigands + uncertainty))
            strength *= 2
            strength = floor(strength)
            strength /= 2
            est_strength = (strength, strength + 0.5)
            return est_brigands, est_strength

    def fight(self, target: str) -> tuple[bool, Soldiers, float]:
        """
        Executes an attack against the given target.
        """
        if self.state.government.soldiers.number < 1:
            raise NoSoldiersError
        if self.fought:
            raise AlreadyFoughtError

        enemies = max(floor(gauss(100, 20)), 10) if target != "crime" else None
        results = self.state.do_fight(target, enemies)
        self.fought = True

        self.history.add_history_line(
            f"fight {target} {enemies}"
        )
        return results
