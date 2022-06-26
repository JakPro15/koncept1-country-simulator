# Advanced commands for the state.
# These commands, combined with the basic ones, allow the program to function
# as a game.


# from ..abstract_interface.history import History
from ..abstract_interface.interface import (
    Interface,
    NotEnoughClassResources,
    NotEnoughGovtResources
)
from .cli_commands import fill_command
from ..auxiliaries.constants import CLASSES, RESOURCES


def transfer(args: list[str], interface: Interface):
    """
    Transfers the given amount of a resource from government to the given
    class. Negative amount signifies a reverse direction of the transfer.
    """
    try:
        assert len(args) == 4

        args[1] = fill_command(args[1], CLASSES)
        assert len(args[1]) == 1
        args[1] = args[1][0]

        args[2] = fill_command(args[2], RESOURCES)
        assert len(args[2]) == 1
        args[2] = args[2][0]

        try:
            args[3] = int(args[3])
        except ValueError:
            raise AssertionError

        try:
            interface.transfer_resources(args[1], args[2], args[3])
        except NotEnoughGovtResources:
            print("The government does not have enough resources for this"
                  " operation.")
        except NotEnoughClassResources:
            print("The chosen class does not have enough resources for this"
                  " operation.")
    except AssertionError:
        print("Invalid syntax. See help for proper usage of transfer command")


def secure(args: list[str], interface: Interface):
    """
    Makes the given amount of a resource owned by the government untradeable
    (secured). Negative amount signifies making a resource tradeable again.
    """
    try:
        assert len(args) == 3

        args[1] = fill_command(args[1], RESOURCES)
        assert len(args[1]) == 1
        args[1] = args[1][0]

        try:
            args[2] = int(args[2])
        except ValueError:
            raise AssertionError

        try:
            interface.secure_resources(args[1], args[2])
        except NotEnoughGovtResources:
            print("The government does not have enough resources for this"
                  " operation.")
    except AssertionError:
        print("Invalid syntax. See help for proper usage of secure command")
