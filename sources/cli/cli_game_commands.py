# Advanced commands for the state.
# These commands, combined with the basic ones, allow the program to function
# as a game.


from ..abstract_interface.interface import (
    Interface,
    NotEnoughClassResources,
    NotEnoughGovtResources
)
from .cli_commands import InvalidCommand, fill_command, res_to_str
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
        assert len(args) in {2, 3}

        args[1] = fill_command(args[1], RESOURCES)
        assert len(args[1]) == 1
        args[1] = args[1][0]

        if len(args) == 3:
            try:
                args[2] = int(args[2])
            except ValueError:
                raise AssertionError
        else:
            args.append(None)

        try:
            interface.secure_resources(args[1], args[2])
        except NotEnoughGovtResources:
            print("The government does not have enough resources for this"
                  " operation.")
    except AssertionError:
        print("Invalid syntax. See help for proper usage of secure command")


def optimal(args: list[str], interface: Interface):
    """
    Sets government optimal amount of resource to the given value.
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

        interface.set_govt_optimal(args[1], args[2])
    except AssertionError:
        print("Invalid syntax. See help for proper usage of optimal command")


def print_law(law: str, interface: Interface):
    """
    Prints information about the given law.
    """
    line = ""
    if law == "tax_personal":
        print("Personal tax (monetary value taken each month from each"
              " person in the class):")
        print(" Nobles  Artisans Peasants  Others")
        taxes = interface.state.sm.tax_rates['personal']
        for class_name in CLASSES:
            line += f" {res_to_str(taxes[class_name]): ^8}"
        print(line)
    elif law == "tax_property":
        print("Property tax rate (what part of the class' total resources will"
              " be taken each month):")
        print(" Nobles  Artisans Peasants  Others")
        taxes = interface.state.sm.tax_rates['property']
        for class_name in CLASSES:
            line += f" {res_to_str(taxes[class_name]): ^8}"
        print(line)
    elif law == "tax_income":
        print("Income tax rate (what part of the class' profits earned this"
              " month will be taken each month):")
        print(" Nobles  Artisans Peasants  Others")
        taxes = interface.state.sm.tax_rates['income']
        for class_name in CLASSES:
            line += f" {res_to_str(taxes[class_name]): ^8}"
        print(line)
    elif law == "wages":
        print("Others' wages (what part of others' produced resources is "
              "actually given to them; the employers take the rest):")
        print(f"{interface.state.sm.others_wage}")
    else:
        raise InvalidCommand


def laws(args: list[str], interface: Interface):
    """
    Sets or views the current laws of the country.
    """
    try:
        assert len(args) >= 2
        args[1] = fill_command(args[1], {"view", "set"})
        assert len(args[1]) == 1
        args[1] = args[1][0]

        laws = {
            "tax_personal", "tax_property", "tax_income", "wages"
        }

        if args[1] == "view":
            assert len(args) in {2, 3}
            if len(args) == 2:
                args.append("")

            args[2] = fill_command(args[2], laws)
            for law in args[2]:
                print_law(law, interface)
        elif args[1] == "set":
            assert len(args) in {4, 5}

            args[2] = fill_command(args[2], laws)
            assert len(args[2]) == 1
            args[2] = args[2][0]

            try:
                args[len(args) - 1] = float(args[len(args) - 1])
            except ValueError:
                raise AssertionError

            if args[2][:4] == "tax_":
                assert len(args) == 5
                args[3] = fill_command(args[3], CLASSES)
                assert len(args[3]) == 1
                args[3] = args[3][0]

                interface.set_law(args[2], args[3], args[4])
            else:
                assert len(args) == 4
                interface.set_law(args[2], None, args[3])
        else:
            raise AssertionError
    except AssertionError:
        print("Invalid syntax. See help for proper usage of laws command")
