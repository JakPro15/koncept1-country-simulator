# Advanced commands for the state.
# These commands, combined with the basic ones, allow the program to function
# as a game.


# from ..abstract_interface.history import History
from ..abstract_interface.interface import Interface


def transfer(args: list[str], interface: Interface):
    try:
        pass
    except AssertionError:
        print("Invalid syntax. See help for proper usage of transfer command")
