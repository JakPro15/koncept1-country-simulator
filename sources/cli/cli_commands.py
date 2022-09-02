# Basic commands for the state.
# These commands allow the program to function as a simulation
# of a country.


import re
from enum import Enum, auto
from math import floor, inf, log10
from numbers import Real
from os import mkdir
from os.path import isdir
from shutil import rmtree
from typing import TYPE_CHECKING, Any, Callable, Iterable, TypeVar

from ..abstract_interface.interface import (Interface, InvalidArgumentError,
                                            SaveAccessError, check_arg)
from ..auxiliaries.enums import (CLASS_NAME_STR, RESOURCE_STR, Class_Name,
                                 Month, Resource)
from ..auxiliaries.resources import Resources
from ..state.state_data_employ_and_commands import (EveryoneDeadError,
                                                    RebellionError)
from .cli_game_commands import (fight, laws, optimal, promote, recruit, secure,
                                transfer)

if TYPE_CHECKING:
    from ..state.social_classes.class_file import Class


class ShutDownCommand(Exception):
    pass


class InvalidCommand(Exception):
    pass


def fill_command(string: str, commands: Iterable[str]) -> list[str]:
    """
    Finds all commands beginning with the given string. Returns a list of them.
    """
    results: list[str] = []
    for command in commands:
        if string == command[0:len(string)]:
            results.append(command)
    return results


def help_default() -> None:
    """
    Prints general help about commands.
    """
    print("List of available commands:")
    print("help [<COMMAND>] - shows help about the program's commands")
    print("exit - exit the program")
    print("save <DIR> - save the game state")
    print("delete <DIR> - delete the game save")
    print("next [<AMOUNT>] - next month")
    print("history <STAT> [<CLASS>] [<MONTHS>] - view the country's history")
    print("state <STAT> - view the current state of the country")
    print("transfer <TARGET> <RESOURCE> <AMOUNT> - transfers resources between"
          " the government and a social class")
    print("secure <RESOURCE> [<AMOUNT>] - make government resources tradeable"
          " or not tradeable")
    print("optimal <RESOURCE> <AMOUNT> - set government optimal resources")
    print("laws view [<LAW>] - view laws of the country")
    print("laws set <LAW> <VALUE> - set laws of the country")
    print("promote <CLASS> <VALUE> - force promotion to a social class")
    print("recruit <CLASS> <VALUE> - recruit soldiers from a class")
    print("fight <TARGET> - send soldiers to battle")


def help_command(command: str) -> None:
    """
    Prints help about the given command.
    """
    if command == "help":
        print("help [<COMMAND>]")
        print("Shows information about the given <COMMAND>. If <COMMAND> is"
              " omitted, prints a list of all available commands. Arguments"
              " beyond the first are ignored.")
    elif command == "exit":
        print("exit")
        print("Shuts down the program without saving - current state is "
              "lost if not saved.")
    elif command == "save":
        print("save <DIR>")
        print("Saves the current game state into saves/<DIR> directory.")
    elif command == "delete":
        print("delete <DIR>")
        print("Deletes the game state from saves/<DIR> directory (deletes "
              "entire directory - anything manually saved there will be "
              "deleted as well).")
    elif command == "next":
        print("next [<AMOUNT>]")
        print("Ends the month and advances to the next <AMOUNT> times - only"
              " once if <AMOUNT> is omitted.")
    elif command == "history":
        print("history <STAT> [<CLASS>] [<MONTHS>]")
        print("Shows the history (past statistics) of the country.")
        print("    <STAT> decides which statistic to show")
        print("    Valid values:")
        print("        population")
        print("        resources")
        print("        total_resources")
        print("        population_change")
        print("        resources_change")
        print("        prices")
        print("        modifiers")
        print("        employment")
        print("        happiness")
        print("    <CLASS> decides which class' statistics to show - it should"
              " only be given when <STAT> is resources or resources_change.")
        print("    Valid values:")
        print("        nobles")
        print("        artisans")
        print("        peasants")
        print("        others")
        print("        government")
        print("    <MONTHS> decides how many months of history, counting back "
              "from the current month, should be shown - if omitted entire "
              "history is shown.")
    elif command == "state":
        print("state <STAT>")
        print("Shows the current state of the country.")
        print("    <STAT> decides which statistic to show")
        print("    Valid values:")
        print("        population")
        print("        resources")
        print("        total_resources")
        print("        prices")
        print("        modifiers")
        print("        government")
        print("        employment")
        print("        happiness")
        print("        military")
    elif command == "transfer":
        print("transfer <TARGET> <RESOURCE> <AMOUNT>")
        print("Transfers <AMOUNT> of <RESOURCE> from the government to "
              "<TARGET> social class. Negative <AMOUNT> signifies seizing "
              "resources from the social class to the government.")
        print("Valid values for <TARGET>:")
        print("    nobles")
        print("    artisans")
        print("    peasants")
        print("    others")
        print("Valid values for <RESOURCE>:")
        print("    food")
        print("    wood")
        print("    stone")
        print("    iron")
        print("    tools")
        print("    land")
    elif command == "secure":
        print("secure <RESOURCE> [<AMOUNT>]")
        print("Makes <AMOUNT> of tradeable <RESOURCE> from the government "
              "untradeable. Negative value of <AMOUNT> signifies making "
              "untradeable (secured) resources tradeable again. If <AMOUNT> is"
              " omitted, all of the resource will be made secure.")
        print("Valid values for <RESOURCE>:")
        print("    food")
        print("    wood")
        print("    stone")
        print("    iron")
        print("    tools")
        print("    land")
    elif command == "optimal":
        print("optimal <RESOURCE> <AMOUNT>")
        print("Sets the optimal amount of <RESOURCE> owned by the government"
              " to <AMOUNT>. When trading, the government will try to obtain "
              "this much of the resource. Secure resources do not count "
              "towards this amount - the government will aim to purchase this"
              " amount of tradeable resources.")
        print("Valid values for <RESOURCE>:")
        print("    food")
        print("    wood")
        print("    stone")
        print("    iron")
        print("    tools")
        print("    land")
        print("<AMOUNT> must be nonnegative.")
    elif command == "laws view":
        print("laws view [<LAW>]")
        print("Prints the chosen laws' data.")
        print("    If given, <LAW> specifies what data should be shown. If not"
              " given, all laws' data is printed.")
        print("Valid values for <LAW>:")
        print("    tax_personal")
        print("    tax_property")
        print("    tax_income")
        print("    wage_minimum")
        print("    wage_government")
        print("    wage_autoregulation")
        print("    max_prices")
    elif command == "laws set":
        print("laws set <LAW> [<CLASS>] [<RESOURCE>] <VALUE>")
        print("Changes the chosen <LAW>'s value for the given <CLASS> or the"
              " given <RESOURCE> to the given <VALUE>.")
        print("Valid values for <LAW> and their valid <VALUE>s:")
        print("    tax_personal - <VALUE> above or equal 0, <CLASS> must be"
              " given, <RESOURCE> must not be given")
        print("    tax_property - <VALUE> between 0 and 1 (including"
              " endpoints), <CLASS> must be given, <RESOURCE> must not be "
              "given")
        print("    tax_income - <VALUE> between 0 and 1 (including"
              " endpoints), <CLASS> must be given, <RESOURCE> must not be "
              "given")
        print("    wage_minimum - <VALUE> between 0 and 1 (including"
              " endpoints), <CLASS> must not be given, <RESOURCE> must not be"
              " given")
        print("    wage_government - <VALUE> between 0 and 1 (including"
              " endpoints), <CLASS> must not be given, <RESOURCE> must not be"
              " given")
        print("    wage_autoregulation - <VALUE> either 0 or 1 (meaning False"
              " or True), <CLASS> must not be given, <RESOURCE> must not be"
              " given")
        print("    max_prices - <VALUE> above 1, <CLASS> must not be given, "
              "<RESOURCE> must be given")
        print("Valid values for <CLASS>:")
        print("    nobles")
        print("    artisans")
        print("    peasants")
        print("    others")
        print("Valid values for <RESOURCE>:")
        print("    food")
        print("    wood")
        print("    stone")
        print("    iron")
        print("    tools")
        print("    land")
    elif command == "promote":
        print("promote <CLASS> <VALUE> - force promotion to a social class")
        print("Spends government resources to promote <VALUE> people to "
              "<CLASS>.")
        print("Valid values for <CLASS>:")
        print("    nobles - promotion from peasants")
        print("    artisans - promotion from others")
        print("    peasants - promotion from others")
        print("<VALUE> must be nonnegative and not higher than <CLASS> "
              "population.")
    elif command == "recruit":
        print("recruit <CLASS> <VALUE>")
        print("Recruit people from a social class to the military.")
        print("    <CLASS> specifies which class to recruit people from."
              " Nobles are made into knights, artisans, peasants and others'"
              "into footmen.")
        print("<VALUE> must be nonnegative and not higher than <CLASS> "
              "population.")
    elif command == "fight":
        print("fight <TARGET>")
        print("Send all soldiers to fight. "
              "<TARGET> specifies the goal of the fighting.")
        print("Valid values for <TARGET>:")
        print("    crime - attack brigands in the country")
        print("    plunder - attack neighboring lands for resources")
        print("    conquest - attack neighboring countries for land")
    else:
        raise InvalidCommand


def help(args: list[str], interface: Any) -> None:
    """
    Prints help about the given command(s).
    If none are given, prints general help.
    Args should be: ["help", commands]
    """
    if len(args) >= 2:
        help_cmds = fill_command(args[1], COMMANDS)
        if "laws" in help_cmds:
            if len(args) < 3:
                args.append("")
            subcommands = fill_command(args[2], {"view", "set"})
            if subcommands == []:
                subcommands = ["view", "set"]

            help_cmds.remove("laws")
            for arg in subcommands:
                help_cmds.append(f"laws {arg}")
        if len(help_cmds) == 0:
            help_default()
        else:
            for command in help_cmds:
                help_command(command)
    else:
        help_default()


T = TypeVar("T")


def set_months_of_history(months: int | None, interface: Interface,
                          data: list[T]) -> tuple[int, list[T]]:
    """
    Cuts the given history data to <months> most recent months. Also returns
    the number of the first month not cut.
    """
    current_month = interface.state.month.value + \
        interface.state.year * 12
    if months is not None:
        begin_month = max(0, current_month - months)
    else:
        begin_month = 0
    return begin_month, data[begin_month:]


def get_month_string(month_int: int) -> str:
    """
    Returns a 13-characters long string representing the given month.
    """
    month = Month(month_int % 12).name
    year = month_int // 12
    return f"{month: >9} {year: >3}"


def res_to_str(amount: float) -> str:
    """
    Returns a string representing the given amount of a resource.
    """
    if isinstance(amount, Real):
        if amount.is_integer():
            amount = int(amount)
    string = str(amount)
    if len(string) > 6:
        string = str(int(amount))
    return string


def price_to_str(amount: float) -> str:
    """
    Returns a string representing the given amount price.
    """
    if amount == inf:
        string = '∞'
    elif amount == 0:
        string = '0.0000'
    else:
        digits = floor(log10(abs(amount))) + 1
        if digits < 1:
            digits = 1
        if digits < 5:
            precision = 5 - digits
            rounded = round(float(amount), precision)
            string = str(rounded)
            while len(string.split('.')[1]) < precision:
                string += '0'
        else:
            rounded = round(amount)
            string = str(int(amount))
    return string


def get_modifiers_from_dict(data: dict[str, bool]) -> str:
    """
    Extracts a 6-character long string representing growth modifiers from the
    given growth modifiers dictionary.
    """
    modifiers_string = ""
    modifiers_string += "S" if data["starving"] else " "
    modifiers_string += "F" if data["freezing"] else " "
    modifiers_string += "P" if data["promoted_from"] else " "
    modifiers_string += "D" if data["demoted_from"] else " "
    modifiers_string += "p" if data["promoted_to"] else " "
    modifiers_string += "d" if data["demoted_to"] else " "
    return modifiers_string


def validate_target_name(target_name: str) -> str:
    """
    Fills the given target (class name or government) name to full with
    fill_command, raises InvalidArgumentError if it's ambiguous or invalid.
    """
    target_names = {
        "nobles", "artisans", "peasants", "others", "government"
    }

    results = fill_command(target_name, target_names)
    check_arg(len(results) == 1, "target name ambiguous or invalid")
    return results[0]


class Print_Type(Enum):
    classes = auto()
    resources = auto()
    employment = auto()


V = TypeVar("V")


def print_history(
    title: str, type: Print_Type, begin_month: int, data: list[dict[str, V]],
    transform: Callable[[V], str]
) -> None:
    """
    Prints history given in data. Each value is converted to a string with
    transform. begin_month decides row headers, type decides column headers.
    title is printed before everything else.
    """
    print(title)
    match type:
        case Print_Type.classes:
            keys = CLASS_NAME_STR
            print(" " * 14 + " ".join([f"{key.title(): >8}" for key in keys]))
        case Print_Type.resources:
            keys = RESOURCE_STR
            print(" " * 14 + " ".join([f"{key.title(): ^6}" for key in keys]))
        case Print_Type.employment:
            keys = CLASS_NAME_STR + ["government"]
            print(" " * 14 + " ".join([f"{key.title(): ^17}" for key in keys]))
            print(" " * 14 + " Employees   Wages  " * 5)
    for index, month_data in enumerate(data):
        header = f"{get_month_string(index + begin_month)}"
        strings = [transform(month_data[key]) for key in keys]
        print(header, ' '.join(strings))


def print_resources(full_data: list[dict[str, dict[str, float]]],
                    target_name: str, begin_month: int, changes: bool) -> None:
    """
    Prints the history of resources or resource changes from the given data.
    target_name decides which class or govt's data to print, changes True
    signifies resource changes are printes, changes False signifies resources
    are printed.
    """
    data = [{  # Limit data to only the printed target
                key: vals_dict[target_name]
                for key, vals_dict in month_data.items()
            } for month_data in full_data]
    print_history(
        f"{target_name.title()} resources "
        f"{'changes ' if changes else ''}stats:",
        Print_Type.resources, begin_month, data,
        lambda res: f"{res_to_str(res): >6}"
    )


def history(args: list[str], interface: Interface) -> None:
    """
    Prints data about the state's history.
    Valid args depend on the option chosen - see help for more information.
    """
    try:
        check_arg(len(args) > 1, "too few arguments")
        arguments = {
            "population", "resources", "prices", "modifiers",
            "change_population", "change_resources", "total_resources",
            "employment", "happiness"
        }
        arg1s = fill_command(args[1], arguments)
        check_arg(len(arg1s) == 1, "argument 1 ambiguous or invalid")
        args[1] = arg1s[0]

        months: int | None
        try:
            months = int(args[-1])
            check_arg(months > 0, "number of months not positive")
            args.pop()
        except ValueError:
            months = None

        match args:
            case "population":
                data = interface.history.population()
                begin_month, data = set_months_of_history(
                    months, interface, data
                )
                print_history("Population stats:", Print_Type.classes,
                              begin_month, data, lambda pop: f"{pop: >8}")

            case "resources", target_name:
                target_name = validate_target_name(target_name)

                full_data = interface.history.resources()
                begin_month, full_data = set_months_of_history(
                    months, interface, full_data
                )
                print_resources(full_data, target_name, begin_month, False)

            case "prices":
                data = interface.history.prices()
                begin_month, data = set_months_of_history(
                    months, interface, data
                )
                print_history("Prices stats:", Print_Type.resources,
                              begin_month, data,
                              lambda price: f"{price_to_str(price): >6}")

            case "modifiers":
                data = interface.history.growth_modifiers()
                begin_month, data = set_months_of_history(
                    months, interface, data
                )
                title = "Growth modifiers over time (S - starving,"\
                        " F - freezing, P - promoted from, D - demoted from,"\
                        " p - promoted to, d - demoted to):"
                print_history(
                    title, Print_Type.classes, begin_month, data,
                    lambda mods: f"{get_modifiers_from_dict(mods): >8}"
                )

            case "change_population":
                data = interface.history.population_change()
                begin_month, data = set_months_of_history(
                    months, interface, data
                )
                print_history("Population changes stats:", Print_Type.classes,
                              begin_month, data, lambda pop: f"{pop: >8}")

            case "change_resources", target_name:
                target_name = validate_target_name(target_name)

                full_data = interface.history.resources_change()
                begin_month, full_data = set_months_of_history(
                    months, interface, full_data
                )
                print_resources(full_data, target_name, begin_month, True)

            case "total_resources":
                data = interface.history.total_resources()
                begin_month, data = set_months_of_history(
                    months, interface, data
                )
                print_history("Total resources stats:", Print_Type.resources,
                              begin_month, data,
                              lambda res: f"{res_to_str(res): >6}")

            case "employment":
                data = interface.history.employment()
                begin_month, data = set_months_of_history(
                    months, interface, data
                )
                print_history("Employment information:", Print_Type.employment,
                              begin_month, data,
                              lambda info: f"{info[0]: >8} {info[1]: >8}")

            case "happiness":
                data = interface.history.happiness()
                begin_month, data = set_months_of_history(
                    months, interface, data
                )
                print_history("Happiness stats:", Print_Type.classes,
                              begin_month, data, lambda hap: f"{hap: >8}")

            case _:
                raise InvalidArgumentError("invalid number of arguments")

    except InvalidArgumentError as e:
        print(f"Invalid syntax: {e}. See help for proper usage of history"
              " command")


def save(args: list[str], interface: Interface) -> None:
    """
    Saves the game in the directory "saves/{save_name}".
    Args should be: ["save", save_name]
    If save_name is not given, the state's previous save name will be reused.
    """
    try:
        if len(args) == 1:
            if interface.save_name is None:
                raise InvalidArgumentError("save name must be given")
            args.append(interface.save_name)
        check_arg(len(args) == 2, "invalid number of arguments")
        check_arg(
            bool(re.search(r"^\w+$", args[1])),
            "save name can only contain letters, digits and underscores"
        )
        if args[1] == "starting":
            print('Please choose a save name different from "starting"')
            return
        try:
            mkdir(f"saves/{args[1]}")
        except FileExistsError:
            ans = input("This save already exists. Enter 1 to overwrite, "
                        "0 to abort: ").strip()
            while ans not in {'0', '1'}:
                print("Invalid choice")
                ans = input("Enter 1 to overwrite, 0 to abort: ").strip()
            if ans == '0':
                return

        try:
            interface.save_data(f"{args[1]}")
        except SaveAccessError:
            print("Failed to open the save file.")
            return
        print(f"Saved the game state into saves/{args[1]}")
    except InvalidArgumentError as e:
        print(f"Invalid syntax: {e}. See help for proper usage of save"
              " command")


def next(args: list[str], interface: Interface) -> None:
    """
    Advances the game to the next month {amount} times.
    Args should be: ["next", amount]
    If amount is not given, advances by only one month.
    """
    try:
        check_arg(len(args) in {1, 2}, "invalid number of arguments")
        if len(args) > 1:
            check_arg(args[1].isdigit(),
                      "number of months contains a non-digit")
            check_arg(int(args[1]) > 0, "number of months not positive")
        if len(args) == 1:
            interface.next_month()
        else:
            for _ in range(int(args[1])):
                interface.next_month()
        print(f"\nNew month: {interface.state.month} "
              f"{interface.state.year}\n")
    except InvalidArgumentError as e:
        print(f"Invalid syntax: {e}. See help for proper usage of next"
              " command")
    except EveryoneDeadError:
        print("GAME OVER")
        print("There is not a living person left in your country.")
        raise ShutDownCommand
    except RebellionError as e:
        class_name = str(e).title()
        print("GAME OVER")
        print(f"{class_name} have rebelled.")
        raise ShutDownCommand


def get_modifiers_from_class(social_class: Class) -> str:
    """
    Extracts a growth modifiers string from the given class.
    The string begins with the class' name.
    """
    modifiers_string = f"{social_class.class_name: >8}: "
    modifiers_string += "S" if social_class.starving else " "
    modifiers_string += "F" if social_class.freezing else " "
    modifiers_string += "P" if social_class.promoted_from else " "
    modifiers_string += "D" if social_class.demoted_from else " "
    modifiers_string += "p" if social_class.promoted_to else " "
    modifiers_string += "d" if social_class.demoted_to else " "
    return modifiers_string


def state(args: list[str], interface: Interface) -> None:
    """
    Prints information about the current state of the country.
    Args should be: ["state", option]
    """
    try:
        check_arg(len(args) == 2, "invalid number of arguments")

        arguments = {
            "population", "resources", "prices", "total_resources",
            "modifiers", "government", "employment", "happiness", "military"
        }
        arg1s = fill_command(args[1], arguments)
        check_arg(len(arg1s) == 1, "argument 1 ambiguous or invalid")
        args[1] = arg1s[0]

        if args[1] == "population":
            data = [
                round(social_class.population)
                for social_class
                in interface.state.classes.values()
            ]
            print("Current population:")
            for index, class_name in enumerate(CLASS_NAME_STR):
                print(f"{class_name: >8}: {data[index]}")

        elif args[1] == "resources":
            data = {
                social_class.class_name.name:
                round(social_class.real_resources, 1)
                for social_class
                in interface.state.classes.values()
            }
            data["government"] = \
                round(interface.state.government.real_resources, 1)
            print("Current resources:")
            line = " " * 10
            for resource in RESOURCE_STR:
                line += f"{resource: >7}"
            print(line)
            for class_name in data:
                line = f"{class_name.title(): >10}"
                for resource in Resource:
                    line += f"{res_to_str(data[class_name][resource]): >7}"
                print(line)

        elif args[1] == "prices":
            data = {
                resource: price_to_str(price)
                for resource, price
                in interface.state.prices.items()
            }
            print("Current prices:")
            for resource, price in data.items():
                print(f"{resource: >5}: {price}")

        elif args[1] == "total_resources":
            data = Resources()
            for social_class in interface.state.classes.values():
                data += social_class.real_resources
            data += interface.state.government.real_resources
            print("Current total resources:")
            for resource, value in data.items():
                print(f"{resource.name: >5}: {res_to_str(value)}")
        elif args[1] == "modifiers":
            print("Current growth modifiers (S - starving, F - freezing, "
                  "P - promoted from, D - demoted from, p - promoted to, "
                  "d - demoted to):")
            for social_class in interface.state.classes.values():
                print(get_modifiers_from_class(social_class))
        elif args[1] == "government":
            print("Government overview:")
            print("Tradeable resources:")
            print("  Food    Wood   Stone    Iron   Tools    Land")
            line = ""
            govt_res = interface.state.government.resources
            for res in Resource:
                line += f" {res_to_str(govt_res[res]): ^7}"
            print(line)
            print("Secure resources (not to be traded away):")
            print("  Food    Wood   Stone    Iron   Tools    Land")
            line = ""
            govt_res = interface.state.government.secure_resources
            for res in Resource:
                line += f" {res_to_str(govt_res[res]): ^7}"
            print(line)
            print("Optimal resources (to be purchased first when trading):")
            print("  Food    Wood   Stone    Iron   Tools    Land")
            line = ""
            govt_res = interface.state.government.optimal_resources
            for res in Resource:
                line += f" {res_to_str(govt_res[res]): ^7}"
            print(line)
            print("Current tax rates:")
            print(" " * 10 + " Nobles  Artisans Peasants  Others")
            line = "Personal:"
            taxes = interface.state.sm.tax_rates['personal']
            for class_name in Class_Name:
                line += f"  {res_to_str(taxes[class_name]): ^7}"
            print(line)
            line = "Property:"
            taxes = interface.state.sm.tax_rates['property']
            for class_name in Class_Name:
                line += f"  {res_to_str(taxes[class_name]): ^7}"
            print(line)
            line = "Income:  "
            taxes = interface.state.sm.tax_rates['income']
            for class_name in Class_Name:
                line += f"  {res_to_str(taxes[class_name]): ^7}"
            print(line)
            govt_wage = interface.state.government.old_wage
            autoreg = interface.state.government.wage_autoregulation
            line = f"Current wage for government employees: {govt_wage}"
            line += f" (autoregulation {'on' if autoreg else 'off'})"
            print(line)
        elif args[1] == "employment":
            employees = {
                class_name.name: round(social_class.employees)
                for class_name, social_class
                in interface.state.classes.items()
            }
            employees["government"] = \
                round(interface.state.government.employees)

            wages = {
                class_name.name: round(social_class.old_wage, 2)
                for class_name, social_class
                in interface.state.classes.items()
            }
            wages["government"] = \
                round(interface.state.government.old_wage, 2)
            print("Current employment information:")

            line = " " * 10
            for resource in RESOURCE_STR:
                line += f"{resource: >7}"
            print(" " * 10 + "Employees   Wages")
            for class_name in employees:
                line = f"{class_name: >10}"
                line += f" {employees[class_name]: ^9}"
                line += f" {wages[class_name]: ^9}"
                print(line)
        elif args[1] == "happiness":
            data = {
                class_name.name:
                round(interface.state.classes[class_name].happiness, 2)
                for class_name in Class_Name
            }
            print("Current happiness:")
            for class_name in CLASS_NAME_STR:
                print(f"{class_name: >8}: {data[class_name]}")
        elif args[1] == "military":
            data = interface.state.government.soldiers
            if not __debug__:
                data = round(data, 0)
            print("Current state of the military:")
            print(f"Footmen: {data.footmen}")
            print(f"Knights: {data.knights}")
            rev = "" if interface.state.government.soldier_revolt else "not "
            print(f"The soldiers are {rev}revolting.")
            brigands, strength = interface.get_brigands()
            if isinstance(brigands, tuple) and isinstance(strength, tuple):
                print(f"Brigands: {brigands[0]}-{brigands[1]}")
                print(f"Brigand strength: {strength[0]}-{strength[1]}")
            else:
                print(f"Brigands: {brigands}")
                print(f"Brigand strength: {strength}")

    except InvalidArgumentError as e:
        print(f"Invalid syntax: {e}. See help for proper usage of state"
              " command")


def delete_save(args: list[str], interface: Any) -> None:
    """
    Deletes the given save (directory "saves/{save_name}")
    Args should be: ["delete", save_name]
    """
    try:
        check_arg(len(args) == 2, "invalid number of arguments")
        check_arg(
            bool(re.search(r"^\w+$", args[1])),
            "save name can only contain letters, digits and underscores"
        )
        if args[1] == "starting":
            print("Deleting this save is prohibited.")
            return
        if not isdir(f"saves/{args[1]}"):
            print("This save does not exist.")
            return

        ans = input("Are you sure you want to delete this save? Enter 1 to "
                    "delete, 0 to abort: ").strip()
        while ans not in {'0', '1'}:
            print("Invalid choice")
            ans = input("Enter 1 to delete, 0 to abort: ").strip()
        if ans == '0':
            return

        rmtree(f"saves/{args[1]}")
        print(f"Removed the save saves/{args[1]}")
    except InvalidArgumentError as e:
        print(f"Invalid syntax: {e}. See help for proper usage of delete"
              " command")


def exit_game(args: Any, interface: Any) -> None:
    """
    Exits the game after asking the user for confirmation.
    """
    print("Are you sure you want to quit? Unsaved game state will be lost.")
    while True:
        ans = input("Enter 1 to confirm, 0 to abort: ").strip()
        if ans == "1":
            raise ShutDownCommand
        elif ans == "0":
            break
        else:
            print("Invalid choice.")


COMMANDS: dict[str, Callable[[list[str], Interface], None]] = {
    "save": save,
    "exit": exit_game,
    "history": history,
    "next": next,
    "state": state,
    "delete": delete_save,
    "transfer": transfer,
    "secure": secure,
    "optimal": optimal,
    "laws": laws,
    "promote": promote,
    "recruit": recruit,
    "fight": fight,
    "help": help
}
