# Advanced commands for the state.
# These commands, combined with the basic ones, allow the program to function
# as a game.


from math import ceil, inf, isnan, log10
from typing import Any, Iterable

from ..abstract_interface.interface import (Interface, InvalidArgumentError,
                                            check_arg)
from ..auxiliaries.enums import (CLASS_NAME_STR, RESOURCE_STR, Class_Name,
                                 Resource)
from ..auxiliaries import globals


class InternalCommandError(Exception):
    pass


def fill_command(string: str, commands: Iterable[str]) -> set[str]:
    """
    Finds all commands beginning with the given string. Returns a list of them.
    """
    results: set[str] = set()
    for command in commands:
        if string == command[0:len(string)]:
            results.add(command)
    return results


def round_format(amount: float, pref_digits: int, max_chars: int) -> str:
    """
    Returns a string representing the given amount rounded to pref_digits,
    unless the string would be too long - then more rounding is done.
    """
    if pref_digits < 0:
        raise ValueError("Preferred digits number cannot be negative")
    if max_chars < 1:
        raise ValueError("Max characters number must be positive")

    if amount == 0:
        return ("0." + "0" * min(pref_digits, max_chars - 2)) \
            if pref_digits > 0 and max_chars >= 3 else "0"
    elif amount == inf:
        return "∞"
    elif amount == -inf:
        return "-∞"
    elif isnan(amount):
        return "nan"

    prepoint_digits = max(1, ceil(log10(abs(amount))))
    if amount < 0:
        prepoint_digits += 1

    max_postpoint_digits = \
        max(0, max_chars - prepoint_digits - 1)  # -1 for the point

    pref_digits = min(pref_digits, max_postpoint_digits)
    if pref_digits == 0:
        return str(round(amount))

    amount = float(round(amount, pref_digits))
    string = str(amount)
    while len(string.split('.')[1]) < pref_digits:
        string += '0'

    return string


def cond_round(amount: float, pref_debug: int, pref_normal: int,
               max_chars: int) -> str:
    """
    Rounds and converts to a string (using round_format) the given amount to
    pref_debug digits if in debug mode, otherwise to pref_normal digits.
    """
    if globals.debug:
        return round_format(amount, pref_debug, max_chars)
    else:
        return round_format(amount, pref_normal, max_chars)


def format_iterable(iterable: Iterable[Any]) -> str:
    """
    Converts the given iterable into a string of a format:
    "element", "element", ...
    """
    iterator = iter(iterable)
    try:
        result = f"\"{next(iterator)}\""
    except StopIteration:
        return ""

    for element in iterator:
        result += f", \"{element}\""
    return result


def transfer(args: list[str], interface: Interface) -> None:
    """
    Transfers the given amount of a resource from government to the given
    class. Negative amount signifies a reverse direction of the transfer.
    Args should be: ["transfer", class_name, resource_name, amount]
    """
    check_arg(len(args) == 4, "invalid number of arguments")

    arg1s = fill_command(args[1], CLASS_NAME_STR)
    check_arg(len(arg1s) == 1, "argument 1 ambiguous or invalid. Valid"
              f" options: {format_iterable(CLASS_NAME_STR)}")
    class_name = Class_Name[arg1s.pop()]

    arg2s = fill_command(args[2], RESOURCE_STR)
    check_arg(len(arg2s) == 1, "argument 2 ambiguous or invalid. Valid"
              f" options: {format_iterable(RESOURCE_STR)}")
    resource = Resource[arg2s.pop()]

    try:
        amount = float(args[3])
    except ValueError:
        raise InvalidArgumentError("amount of resources not a number")

    interface.transfer_resources(class_name, resource, amount)


def secure(args: list[str], interface: Interface) -> None:
    """
    Makes the given amount of a resource owned by the government untradeable
    (secured). Negative amount signifies making a resource tradeable again.
    Args should be: ["secure", resource, amount]
    """
    check_arg(len(args) in {2, 3}, "invalid number of arguments")

    arg1s = fill_command(args[1], RESOURCE_STR)
    check_arg(len(arg1s) == 1, "argument 1 ambiguous or invalid. Valid"
              f" options: {format_iterable(RESOURCE_STR)}")
    resource = Resource[arg1s.pop()]

    if len(args) == 3:
        try:
            amount = float(args[2])
        except ValueError:
            raise InvalidArgumentError("amount of resources not a number")
    else:
        amount = None

    interface.secure_resources(resource, amount)


def optimal(args: list[str], interface: Interface) -> None:
    """
    Sets government optimal amount of resource to the given value.
    Args should be: ["optimal", resource, amount]
    """
    check_arg(len(args) == 3, "invalid number of arguments")

    arg1s = fill_command(args[1], RESOURCE_STR)
    check_arg(len(arg1s) == 1, "argument 1 ambiguous or invalid. Valid"
              f" options: {format_iterable(RESOURCE_STR)}")
    resource = Resource[arg1s.pop()]

    try:
        amount = float(args[2])
    except ValueError:
        raise InvalidArgumentError("amount of resources not a number")
    interface.set_govt_optimal(resource, amount)


def print_law(law: str, interface: Interface) -> None:
    """
    Prints information about the given law.
    """
    line = ""
    if law == "tax_personal":
        print("tax_personal")
        print("Personal tax (monetary value taken each month from each"
              " person in the class):")
        print(" Nobles  Artisans Peasants  Others")
        taxes = interface.state.sm.tax_rates['personal']
        for class_name in Class_Name:
            line += f" {round_format(taxes[class_name], 2, 8): ^8}"
        print(line)
    elif law == "tax_property":
        print("tax_property")
        print("Property tax rate (what part of the class' total resources will"
              " be taken each month):")
        print(" Nobles  Artisans Peasants  Others")
        taxes = interface.state.sm.tax_rates['property']
        for class_name in Class_Name:
            line += f" {round_format(taxes[class_name], 2, 8): ^8}"
        print(line)
    elif law == "tax_income":
        print("tax_income")
        print("Income tax rate (what part of the class' profits earned this"
              " month will be taken each month):")
        print(" Nobles  Artisans Peasants  Others")
        taxes = interface.state.sm.tax_rates['income']
        for class_name in Class_Name:
            line += f" {round_format(taxes[class_name], 2, 8): ^8}"
        print(line)
    elif law == "wage_minimum":
        print("wage_minimum")
        print("Minimum wages (what part of employees' produced resources is "
              "actually given to them; the employers take the rest):")
        print(f"{interface.state.sm.others_minimum_wage}")
    elif law == "wage_government":
        print("wage_government")
        print("Wages for government employees (what part of employees' "
              "produced resources is actually given to them; the government"
              " takes the rest):")
        govt_wage = max(interface.state.government.wage,
                        interface.state.sm.others_minimum_wage)
        print(f"{govt_wage}")
    elif law == "wage_autoregulation":
        print("wage_autoregulation")
        print("Whether wages for government employees will be automatically "
              "regulated:")
        print(f"{interface.state.government.wage_autoregulation}")
    elif law == "max_prices":
        print("max_prices")
        print("Maximum prices:")
        prices = interface.state.sm.max_prices
        print("  Food    Wood   Stone    Iron   Tools    Land")
        print(f"{round_format(prices.food, 4, 7): ^7}"
              f" {round_format(prices.wood, 4, 7): ^7}"
              f" {round_format(prices.stone, 4, 7): ^7}"
              f" {round_format(prices.iron, 4, 7): ^7}"
              f" {round_format(prices.tools, 4, 7): ^7}"
              f" {round_format(prices.land, 4, 7): ^7}")
    else:
        raise InternalCommandError


LAWS = {
    "tax_personal", "tax_property", "tax_income", "wage_minimum",
    "wage_government", "wage_autoregulation", "max_prices"
}


def laws(args: list[str], interface: Interface) -> None:
    """
    Sets or views the current laws of the country.
    Args should be: ["laws", "set" | "view", law, argument, value]
    Argument is only needed with some laws, value is only needed when setting.
    See help for more information.
    """
    check_arg(len(args) >= 2, "too few arguments")
    arg1s = fill_command(args[1], {"view", "set"})
    check_arg(len(arg1s) == 1, "argument 1 ambiguous or invalid. Valid"
              ' options: "view", "set"')
    args[1] = arg1s.pop()

    if args[1] == "view":
        check_arg(len(args) in {2, 3}, "invalid number of arguments")
        if len(args) == 2:
            args.append("")

        laws_for_help = fill_command(args[2], LAWS)
        check_arg(len(laws_for_help) > 0, "argument 2 invalid. There is no"
                  " such law")

        for law in laws_for_help:
            print_law(law, interface)
    elif args[1] == "set":
        check_arg(len(args) in {4, 5}, "invalid number of arguments")

        arg2s = fill_command(args[2], LAWS)
        check_arg(len(arg2s) == 1, "argument 2 ambiguous or invalid. Valid"
                  f" options {format_iterable(LAWS)}")
        args[2] = arg2s.pop()

        try:
            value = float(args[len(args) - 1])
        except ValueError:
            raise InvalidArgumentError("law value not a number")

        if args[2][:4] in {"tax_", "max_"}:
            check_arg(len(args) == 5, "invalid number of arguments")
            valid_args = CLASS_NAME_STR \
                if args[2][:4] == "tax_" else RESOURCE_STR
            arg3s = fill_command(args[3], valid_args)
            check_arg(len(arg3s) == 1, "argument 3 ambiguous or invalid. Valid"
                      f" options {format_iterable(valid_args)}")
            args[3] = arg3s.pop()

            interface.set_law(args[2], args[3], value)
        else:
            check_arg(len(args) == 4, "invalid number of arguments")
            interface.set_law(args[2], None, value)
    else:
        raise InternalCommandError


def promote(args: list[str], interface: Interface) -> None:
    """
    Forces a promotion using government resources.
    Args should be: ["promote", class_name, amount]
    Promotes {amount} people to {class_name}.
    """
    check_arg(len(args) == 3, "invalid number of arguments")

    valid_classes = CLASS_NAME_STR.copy()
    valid_classes.remove("others")
    arg1s = fill_command(args[1], valid_classes)
    check_arg(len(arg1s) == 1, "argument 1 ambiguous or invalid. Valid"
              f" options: {format_iterable(valid_classes)}")
    class_name = Class_Name[arg1s.pop()]

    try:
        amount = float(args[2])
    except ValueError:
        raise InvalidArgumentError("argument 2 must be a real number")

    interface.force_promotion(class_name, amount)


def recruit(args: list[str], interface: Interface) -> None:
    """
    Recruits {amount} soldiers from {class_name}.
    Args should be: ["recruit", class_name, amount]
    """
    check_arg(len(args) == 3, "invalid number of arguments")

    arg1s = fill_command(args[1], CLASS_NAME_STR)
    check_arg(len(arg1s) == 1, "argument 1 ambiguous or invalid. Valid"
              f" options {format_iterable(CLASS_NAME_STR)}")
    class_name = Class_Name[arg1s.pop()]

    try:
        amount = float(args[2])
    except ValueError:
        raise InvalidArgumentError("amount of soldiers not a number")

    interface.recruit(class_name, amount)


def fight(args: list[str], interface: Interface) -> None:
    """
    Sends all soldiers to combat.
    Args should be: ["fight", ("crime" | "plunder" | "conquest")]
    """
    check_arg(len(args) == 2, "invalid number of arguments")

    targets = {"crime", "plunder", "conquest"}
    arg1s = fill_command(args[1], targets)
    check_arg(len(arg1s) == 1, "argument 1 ambiguous or invalid. Valid"
              ' options: "crime", "plunder", "conquest"')
    target = arg1s.pop()

    results = interface.fight(target)
    dead_soldiers = results[1] if globals.debug else round(results[1], 0)
    print("The battle has been", "won." if results[0] else "lost.")
    print(dead_soldiers.knights,
          f"knight{'s' if dead_soldiers.knights != 1 else ''} and",
          dead_soldiers.footmen,
          f"footm{'e' if dead_soldiers.footmen != 1 else 'a'}n died.")
    if args[1] == "crime":
        dead_brigands = results[2] if globals.debug else round(results[2])
        print(dead_brigands,
              f"brigand{'s' if dead_brigands != 1 else ''} died.")
    elif args[1] == "conquest":
        print("Conquered", round(results[2], 2), "land.")
    elif args[1] == "plunder":
        print("Plundered", round(results[2], 2),
              "food, wood, stone, iron and tools.")
