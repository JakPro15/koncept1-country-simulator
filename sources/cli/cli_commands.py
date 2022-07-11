# Basic commands for the state.
# These commands allow the program to function as a simulation
# of a country.


from sources.auxiliaries.arithmetic_dict import Arithmetic_Dict
from sources.state.state_data import EveryoneDeadError, RebellionError
from ..auxiliaries.constants import EMPTY_RESOURCES, MONTHS, RESOURCES, CLASSES
from ..abstract_interface.interface import Interface, SaveAccessError
from math import floor, inf, log10
from os import mkdir
from os.path import isdir
from shutil import rmtree


class ShutDownCommand(Exception):
    pass


class InvalidCommand(Exception):
    pass


def fill_command(string, commands):
    """
    Finds all commands fitting the given string. Returns a list of them.
    """
    results = []
    for command in commands:
        if string == command[0:len(string)]:
            results.append(command)
    return results


def help_default():
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


def help_command(command: str):
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
        print("        population (p)")
        print("        resources (r)")
        print("        total_resources (tr)")
        print("        population_change (pc)")
        print("        resources_change (rc)")
        print("        prices (pr)")
        print("        employment (e)")
        print("        happiness (h)")
        print("    <CLASS> decides which class' statistics to show - it should"
              " only be given when <STAT> is resources or resources_change.")
        print("    Valid values:")
        print("        nobles (n)")
        print("        artisans (a)")
        print("        peasants (p)")
        print("        others (o)")
        print("        government (g)")
        print("    <MONTHS> decides how many months of history, counting back "
              "from the current month, should be shown - if omitted entire "
              "history is shown.")
    elif command == "state":
        print("state <STAT>")
        print("Shows the current state of the country.")
        print("    <STAT> decides which statistic to show")
        print("    Valid values:")
        print("        population (p)")
        print("        resources (r)")
        print("        total_resources (tr)")
        print("        prices (pr)")
        print("        modifiers (m)")
        print("        government (g)")
        print("        employment (e)")
        print("        happiness (h)")
    elif command == "transfer":
        print("transfer <TARGET> <RESOURCE> <AMOUNT>")
        print("Transfers <AMOUNT> of <RESOURCE> from the government to "
              "<TARGET> social class. Negative <AMOUNT> signifies seizing "
              "resources from the social class to the government.")
        print("Valid values for <TARGET>:")
        print("    nobles (n)")
        print("    artisans (a)")
        print("    peasants (p)")
        print("    others (o)")
        print("Valid values for <RESOURCE>:")
        print("    food (f)")
        print("    wood (w)")
        print("    stone (s)")
        print("    iron (i)")
        print("    tools (t)")
        print("    land (l)")
    elif command == "secure":
        print("secure <RESOURCE> [<AMOUNT>]")
        print("Makes <AMOUNT> of tradeable <RESOURCE> from the government "
              "untradeable. Negative value of <AMOUNT> signifies making "
              "untradeable (secured) resources tradeable again. If <AMOUNT> is"
              " omitted, all of the resource will be made secure.")
        print("Valid values for <RESOURCE>:")
        print("    food (f)")
        print("    wood (w)")
        print("    stone (s)")
        print("    iron (i)")
        print("    tools (t)")
        print("    land (l)")
    elif command == "optimal":
        print("optimal <RESOURCE> <AMOUNT>")
        print("Sets the optimal amount of <RESOURCE> owned by the government"
              " to <AMOUNT>. When trading, the government will try to obtain "
              "this much of the resource. Secure resources do not count "
              "towards this amount - the government will aim to purchase this"
              " amount of tradeable resources.")
        print("Valid values for <RESOURCE>:")
        print("    food (f)")
        print("    wood (w)")
        print("    stone (s)")
        print("    iron (i)")
        print("    tools (t)")
        print("    land (l)")
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
        print("    nobles (n)")
        print("    artisans (a)")
        print("    peasants (p)")
        print("    others (o)")
        print("Valid values for <RESOURCE>:")
        print("    food (f)")
        print("    wood (w)")
        print("    stone (s)")
        print("    iron (i)")
        print("    tools (t)")
        print("    land (l)")
        print("promote <CLASS> <VALUE> - force promotion to a social class")
        print("Spends government resources to promote <VALUE> people to "
              "<CLASS>.")
        print("Valid values for <CLASS>:")
        print("    nobles (n) - promotion from peasants")
        print("    artisans (a) - promotion from others")
        print("    peasants (p) - promotion from others")
        print("<VALUE> must be nonnegative.")
    else:
        raise InvalidCommand


def help(args: list[str], commands: set):
    if len(args) >= 2:
        args[1] = fill_command(args[1], commands)
        if "laws" in args[1]:
            if len(args) < 3:
                args.append("")
            args[2] = fill_command(args[2], {"view", "set"})
            if args[2] == []:
                args[2] = ["view", "set"]

            args[1].remove("laws")
            for arg in args[2]:
                args[1].append(f"laws {arg}")
        if len(args[1]) == 0:
            help_default()
        else:
            for command in args[1]:
                help_command(command)
    else:
        help_default()


def set_months_of_history(months: int | None, interface: Interface, data):
    """
    Cuts the given history data to <months> most recent months. Also returns
    the number of the first month not cut.
    """
    current_month = MONTHS.index(interface.state.month) + \
        interface.state.year * 12
    if months is not None:
        begin_month = max(0, current_month - months)
    else:
        begin_month = 0
    return begin_month, data[begin_month:]


def get_month_string(month_int):
    """
    Returns a 13-characters long string representing the given month.
    """
    month = MONTHS[month_int % 12]
    year = month_int // 12
    return f"{month: >9} {year: >3}"


def res_to_str(amount: float | int):
    """
    Returns a string representing the given amount of a resource.
    """
    if isinstance(amount, float):
        if amount.is_integer():
            amount = int(amount)
    string = str(amount)
    if len(string) > 6:
        string = str(int(amount))
    return string


def price_to_str(amount: float):
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


def get_modifiers_from_dict(data):
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


def history(args: list[str], interface: Interface):
    try:
        assert len(args) > 1
        assert args[1] in {
            "population", "resources", "prices", "modifiers",
            "population_change", "resources_change", "total_resources",
            "employment", "happiness",
            "p", "r", "pr", "pc", "rc", "tr", "m", "e", "h"
        }

        if args[1] in {"resources", "r", "resources_change", "rc"}:
            assert len(args) in {3, 4}

            options = {
                "nobles", "artisans", "peasants", "others", "government"
            }
            args[2] = fill_command(args[2], options)
            assert len(args[2]) == 1
            args[2] = args[2][0]
            official_class = args[2].title()

            if len(args) == 4:
                assert args[3].isdigit()
                args[3] = int(args[3])
                assert args[3] > 0
            else:
                args.append(None)

            if args[1] in {"resources", "r"}:
                data = interface.history.resources()
                begin_month, data = set_months_of_history(
                    args[3], interface, data
                )
                print(f"{official_class} resources stats:")
                print(" " * 13 + f" {'food': ^6} {'wood': ^6} {'stone': ^6} "
                      f"{'iron': ^6} {'tools': ^6} {'land': ^6}")
                for index, month_data in enumerate(data):
                    line = f"{get_month_string(index + begin_month)}"
                    for resource in RESOURCES:
                        res = month_data[args[2]].get(resource, 0)
                        line += f"{res_to_str(res): >7}"
                    print(line)
            else:
                data = interface.history.resources_change()
                begin_month, data = set_months_of_history(
                    args[3], interface, data
                )
                print(f"{official_class} resources changes stats:")
                print(" " * 13 + f" {'food': ^6} {'wood': ^6} {'stone': ^6} "
                      f"{'iron': ^6} {'tools': ^6} {'land': ^6}")
                for index, month_data in enumerate(data):
                    line = f"{get_month_string(index + begin_month)}"
                    for resource in RESOURCES:
                        res = month_data[args[2]].get(resource, 0)
                        line += f"{res_to_str(res): >7}"
                    print(line)
        else:
            assert len(args) in {2, 3}

            if len(args) == 3:
                assert args[2].isdigit()
                args[2] = int(args[2])
                assert args[2] > 0
            else:
                args.append(None)

            if args[1] in {"population", "p"}:
                data = interface.history.population()
                begin_month, data = set_months_of_history(
                    args[2], interface, data
                )
                print("Population stats:")
                print(" " * 14 + "  Nobles Artisans Peasants   Others")
                for index, month_data in enumerate(data):
                    print(f"{get_month_string(index + begin_month)}"
                          f"{month_data['nobles']: >9}"
                          f"{month_data['artisans']: >9}"
                          f"{month_data['peasants']: >9}"
                          f"{month_data['others']: >9}")
            elif args[1] in {"prices", "pr"}:
                data = interface.history.prices()
                begin_month, data = set_months_of_history(
                    args[2], interface, data
                )
                print("Prices stats:")
                print(" " * 14 +
                      "  Food    Wood   Stone    Iron   Tools    Land")
                for index, month_data in enumerate(data):
                    print(f"{get_month_string(index + begin_month)}"
                          f" {price_to_str(month_data['food']): >7}"
                          f" {price_to_str(month_data['wood']): >7}"
                          f" {price_to_str(month_data['stone']): >7}"
                          f" {price_to_str(month_data['iron']): >7}"
                          f" {price_to_str(month_data['tools']): >7}"
                          f" {price_to_str(month_data['land']): >7}")
            elif args[1] in {"population_change", "pc"}:
                data = interface.history.population_change()
                begin_month, data = set_months_of_history(
                    args[2], interface, data
                )
                print("Population changes stats:")
                print(" " * 14 + "  Nobles Artisans Peasants   Others")
                for index, month_data in enumerate(data):
                    print(f"{get_month_string(index + begin_month)}"
                          f"{month_data['nobles']: >9}"
                          f"{month_data['artisans']: >9}"
                          f"{month_data['peasants']: >9}"
                          f"{month_data['others']: >9}")
            elif args[1] in {"total_resources", "tr"}:
                data = interface.history.total_resources()
                begin_month, data = set_months_of_history(
                    args[2], interface, data
                )
                print("Total resources stats:")
                print(" " * 14 +
                      "  Food    Wood   Stone    Iron   Tools    Land")
                for index, month_data in enumerate(data):
                    print(f"{get_month_string(index + begin_month)}"
                          f" {res_to_str(month_data['food']): >7}"
                          f" {res_to_str(month_data['wood']): >7}"
                          f" {res_to_str(month_data['stone']): >7}"
                          f" {res_to_str(month_data['iron']): >7}"
                          f" {res_to_str(month_data['tools']): >7}"
                          f" {res_to_str(month_data['land']): >7}")
            elif args[1] in {"modifiers", "m"}:
                data = interface.history.growth_modifiers()
                begin_month, data = set_months_of_history(
                    args[2], interface, data
                )
                print("Growth modifiers over time (S - starving, F - freezing,"
                      " P - promoted from, D - demoted from, p - promoted to, "
                      "d - demoted to):")
                print(" " * 14 + "  Nobles Artisans Peasants   Others")
                for index, month_data in enumerate(data):
                    print(
                     f"{get_month_string(index + begin_month)}"
                     f"{get_modifiers_from_dict(month_data['nobles']): >9}"
                     f"{get_modifiers_from_dict(month_data['artisans']): >9}"
                     f"{get_modifiers_from_dict(month_data['peasants']): >9}"
                     f"{get_modifiers_from_dict(month_data['others']): >9}"
                    )
            elif args[1] in {"employment", "e"}:
                data = interface.history.employment()
                employees = data["employees"]
                wages = data["wages"]
                begin_month, employees = set_months_of_history(
                    args[2], interface, employees
                )
                begin_month, wages = set_months_of_history(
                    args[2], interface, wages
                )
                print("Employment information:")

                line2, line3 = " " * 13, " " * 13
                for class_name in CLASSES:
                    line2 += f" {class_name: ^19}"
                    line3 += " Employees   Wages  "
                line2 += f" {'government': ^19}"
                line3 += " Employees   Wages  "
                print(line2)
                print(line3)

                for index, month_data in enumerate(
                     zip(employees, wages)):
                    month_emps, month_wags = month_data
                    line = f"{get_month_string(index + begin_month)}"
                    for employer in month_emps:
                        line += f" {month_emps[employer]: ^9}"
                        line += f" {month_wags[employer]: ^9}"
                    print(line)
            elif args[1] in {"happiness", "h"}:
                data = interface.history.happiness()
                begin_month, data = set_months_of_history(
                    args[2], interface, data
                )
                print("Happiness stats:")
                print(" " * 14 + "  Nobles Artisans Peasants   Others")
                for index, month_data in enumerate(data):
                    print(f"{get_month_string(index + begin_month)}"
                          f"{month_data['nobles']: >9}"
                          f"{month_data['artisans']: >9}"
                          f"{month_data['peasants']: >9}"
                          f"{month_data['others']: >9}")
    except AssertionError:
        print("Invalid syntax. See help for proper usage of history command")


def save(args: list[str], interface: Interface):
    try:
        if len(args) == 1:
            args.append(interface.save_name)
        assert len(args) == 2
        assert args[1].isalpha()
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
    except AssertionError:
        print("Invalid syntax. See help for proper usage of save command")


def next(args: list[str], interface: Interface):
    try:
        assert len(args) in {1, 2}
        if len(args) > 1:
            assert args[1].isdigit()
            assert int(args[1]) > 0
        if len(args) == 1:
            interface.next_month()
        else:
            for _ in range(int(args[1])):
                interface.next_month()
        print(f"\nNew month: {interface.state.month} "
              f"{interface.state.year}\n")
    except AssertionError:
        print("Invalid syntax. See help for proper usage of next command")
    except EveryoneDeadError:
        print("GAME OVER")
        print("There is not a living person left in your country.")
        raise ShutDownCommand
    except RebellionError as e:
        class_name = str(e).title()
        print("GAME OVER")
        print(f"{class_name} have rebelled.")
        raise ShutDownCommand


def get_modifiers_string(social_class):
    modifiers_string = f"{social_class.class_name: >8}: "
    modifiers_string += "S" if social_class.starving else " "
    modifiers_string += "F" if social_class.freezing else " "
    modifiers_string += "P" if social_class.promoted_from else " "
    modifiers_string += "D" if social_class.demoted_from else " "
    modifiers_string += "p" if social_class.promoted_to else " "
    modifiers_string += "d" if social_class.demoted_to else " "
    return modifiers_string


def state(args: list[str], interface: Interface):
    try:
        assert len(args) in {2, 3}
        assert args[1] in {
            "population", "resources", "prices", "total_resources",
            "modifiers", "government", "employment", "happiness",
            "p", "r", "pr", "tr", "m", "g", "e", "h"
        }
        if len(args) == 3:
            assert args[2].isdigit()
            assert int(args[2]) > 0

        if args[1] in {"population", "p"}:
            data = [
                round(social_class.population)
                for social_class
                in interface.state.classes
            ]
            print("Current population:")
            for index, class_name in enumerate(CLASSES):
                print(f"{class_name: >8}: {data[index]}")
        elif args[1] in {"resources", "r"}:
            data = {
                social_class.class_name: social_class.real_resources.round(1)
                for social_class
                in interface.state.classes
            }
            data["government"] = \
                interface.state.government.real_resources.round(1)
            print("Current resources:")
            line = " " * 10
            for resource in RESOURCES:
                line += f"{resource: >7}"
            print(line)
            for class_name in data:
                line = f"{class_name: >10}"
                for resource in RESOURCES:
                    line += f"{res_to_str(data[class_name][resource]): >7}"
                print(line)
        elif args[1] in {"prices", "pr"}:
            data = {
                resource: price_to_str(price)
                for resource, price
                in interface.state.prices.items()
            }
            print("Current prices:")
            for resource, price in data.items():
                print(f"{resource: >5}: {price}")
        elif args[1] in {"total_resources", "tr"}:
            data = EMPTY_RESOURCES.copy()
            for social_class in interface.state.classes:
                data += social_class.real_resources
            data += interface.state.government.real_resources
            print("Current total resources:")
            for resource, value in data.items():
                print(f"{resource: >5}: {res_to_str(value)}")
        elif args[1] in {"modifiers", "m"}:
            print("Current growth modifiers (S - starving, F - freezing, "
                  "P - promoted from, D - demoted from, p - promoted to, "
                  "d - demoted to):")
            for social_class in interface.state.classes:
                print(get_modifiers_string(social_class))
        elif args[1] in {"government", "g"}:
            print("Government overview:")
            print("Tradeable resources:")
            print("  Food    Wood   Stone    Iron   Tools    Land")
            line = ""
            govt_res = interface.state.government.resources
            for res in RESOURCES:
                line += f" {res_to_str(govt_res[res]): ^7}"
            print(line)
            print("Secure resources (not to be traded away):")
            print("  Food    Wood   Stone    Iron   Tools    Land")
            line = ""
            govt_res = interface.state.government.secure_resources
            for res in RESOURCES:
                line += f" {res_to_str(govt_res[res]): ^7}"
            print(line)
            print("Optimal resources (to be purchased first when trading):")
            print("  Food    Wood   Stone    Iron   Tools    Land")
            line = ""
            govt_res = interface.state.government.optimal_resources
            for res in RESOURCES:
                line += f" {res_to_str(govt_res[res]): ^7}"
            print(line)
            print("Current tax rates:")
            print(" " * 10 + " Nobles  Artisans Peasants  Others")
            line = "Personal:"
            taxes = interface.state.sm.tax_rates['personal']
            for class_name in CLASSES:
                line += f"  {res_to_str(taxes[class_name]): ^7}"
            print(line)
            line = "Property:"
            taxes = interface.state.sm.tax_rates['property']
            for class_name in CLASSES:
                line += f"  {res_to_str(taxes[class_name]): ^7}"
            print(line)
            line = "Income:  "
            taxes = interface.state.sm.tax_rates['income']
            for class_name in CLASSES:
                line += f"  {res_to_str(taxes[class_name]): ^7}"
            print(line)
            govt_wage = getattr(interface.state.government, "old_wage",
                                interface.state.sm.others_minimum_wage)
            autoreg = interface.state.government.wage_autoregulation
            line = f"Current wage for government employees: {govt_wage}"
            line += f" (autoregulation {'on' if autoreg else 'off'})"
            print(line)
        elif args[1] in {"employment", "e"}:
            employees = Arithmetic_Dict({
                "nobles": getattr(interface.state.classes[0], "employees",
                                  0),
                "artisans": getattr(interface.state.classes[1], "employees",
                                    0),
                "peasants": getattr(interface.state.classes[2], "employees",
                                    0),
                "others": getattr(interface.state.classes[3], "employees",
                                  0),
                "government": getattr(interface.state.government, "employees",
                                      0)
            }).round(0)
            wages = Arithmetic_Dict({
                "nobles": getattr(interface.state.classes[0], "old_wage",
                                  interface.state.sm.others_minimum_wage),
                "artisans": getattr(interface.state.classes[1], "old_wage",
                                    interface.state.sm.others_minimum_wage),
                "peasants": getattr(interface.state.classes[2], "old_wage",
                                    interface.state.sm.others_minimum_wage),
                "others": getattr(interface.state.classes[3], "old_wage",
                                  interface.state.sm.others_minimum_wage),
                "government": getattr(interface.state.government, "old_wage",
                                      interface.state.sm.others_minimum_wage),
            }).round(2)
            print("Current employment information:")
            line = " " * 10
            for resource in RESOURCES:
                line += f"{resource: >7}"
            print(" " * 10 + "Employees   Wages")
            for class_name in employees:
                line = f"{class_name: >10}"
                line += f" {employees[class_name]: ^9}"
                line += f" {wages[class_name]: ^9}"
                print(line)
        elif args[1] in {"happiness", "h"}:
            data = [
                round(social_class.happiness, 2)
                for social_class
                in interface.state.classes
            ]
            print("Current happiness:")
            for index, class_name in enumerate(CLASSES):
                print(f"{class_name: >8}: {data[index]}")
    except AssertionError:
        print("Invalid syntax. See help for proper usage of state command")


def delete_save(args: list[str]):
    try:
        assert len(args) == 2
        assert args[1].isalpha()
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
    except AssertionError:
        print("Invalid syntax. See help for proper usage of delete command")
