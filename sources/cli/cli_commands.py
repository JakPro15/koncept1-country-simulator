from sources.state.state_data import EveryoneDeadError
from ..auxiliaries.constants import EMPTY_RESOURCES, MONTHS, RESOURCES, CLASSES
from ..abstract_interface.history import History
from ..abstract_interface.interface import Interface
from math import floor, inf, log10
from os import mkdir
from os.path import isdir
from shutil import rmtree


class ShutDownCommand(Exception):
    pass


def help():
    print("List of available commands:")
    print("exit, e - shuts down the program")
    print("save <DIR>, sv <DIR> - saves the game state into saves/<DIR>"
          " directory")
    print("del <DIR>, d <DIR> - deletes the game state from saves/<DIR>"
          " directory")
    print("next <AMOUNT>, n <AMOUNT> - ends the month and advances to the "
          "next <AMOUNT> times - only once if <AMOUNT> not specified")
    print("history <STAT> <MONTHS>, h <STAT> <MONTHS> - shows the history of "
          "the country")
    print("    <STAT> decides which statistic to show")
    print("    Valid values:")
    print("        population (p)")
    print("        resources (r)")
    print("        total_resources (tr)")
    print("        population_change (pc)")
    print("        resources_change (rc)")
    print("        prices (pr)")
    print("    <MONTHS> decides how many months of history should"
          "be shown - left empty shows entire history")
    print("state <STAT>, s <STAT> - shows the current state of the country")
    print("    <STAT> decides which statistic to show")
    print("    Valid values:")
    print("        population (p)")
    print("        resources (r)")
    print("        total_resources (tr)")
    print("        prices (pr)")


def set_months_of_history(args: list[str], interface: Interface, data):
    current_month = MONTHS.index(interface.state.month) + \
        interface.state.year * 12
    if len(args) > 2:
        args[2] = int(args[2])
        if args[2] < 0:
            raise ValueError
        begin_month = max(0, current_month - args[2])
    else:
        begin_month = 0
    return begin_month, data[begin_month:]


def get_month_string(month_int):
    month = MONTHS[month_int % 12]
    year = month_int // 12
    return f"{month: >9} {year: >3}"


def res_to_str(amount):
    string = str(amount)
    if len(string) > 6:
        string = str(int(amount))
    return string


def price_to_str(amount):
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


def history(args: list[str], interface: Interface):
    try:
        assert len(args) in {2, 3}
        assert args[1] in {
            "population", "resources", "prices",
            "population_change", "resources_change", "total_resources",
            "p", "r", "pr", "pc", "rc", "tr"
        }
        if len(args) == 3:
            assert args[2].isdigit()
            assert int(args[2]) > 0

        if args[1] in {"population", "p"}:
            data = interface.history.population()
            begin_month, data = set_months_of_history(args, interface, data)
            print("Population stats:")
            print(" " * 14 + "  Nobles Artisans Peasants   Others")
            for index, month_data in enumerate(data):
                print(f"{get_month_string(index + begin_month)}"
                      f"{month_data['nobles']: >9}"
                      f"{month_data['artisans']: >9}"
                      f"{month_data['peasants']: >9}"
                      f"{month_data['others']: >9}")
        elif args[1] in {"resources", "r"}:
            data = interface.history.resources()
            begin_month, data = set_months_of_history(args, interface, data)
            print("Resources stats:")
            print(" " * 14 + f"{'Nobles': ^35}{'Artisans': ^35}"
                  f"{'Peasants': ^35}{'Others': ^35}")
            print(" " * 13 + f" {'food': ^6} {'wood': ^6} {'stone': ^6} "
                  f"{'iron': ^6} {'tools': ^6}" * 4)
            for index, month_data in enumerate(data):
                line = f"{get_month_string(index + begin_month)}"
                for social_class in month_data:
                    for resource in RESOURCES:
                        res = month_data[social_class].get(resource, 0)
                        line += f"{res_to_str(res): >7}"
                print(line)
        elif args[1] in {"prices", "pr"}:
            data = interface.history.prices()
            begin_month, data = set_months_of_history(args, interface, data)
            print("Prices stats:")
            print(" " * 14 + "  Food    Wood   Stone    Iron   Tools")
            for index, month_data in enumerate(data):
                print(f"{get_month_string(index + begin_month)}"
                      f" {price_to_str(month_data['food']): >7}"
                      f" {price_to_str(month_data['wood']): >7}"
                      f" {price_to_str(month_data['stone']): >7}"
                      f" {price_to_str(month_data['iron']): >7}"
                      f" {price_to_str(month_data['tools']): >7}")
        if args[1] in {"population_change", "pc"}:
            data = interface.history.population_change()
            begin_month, data = set_months_of_history(args, interface, data)
            print("Population changes stats:")
            print(" " * 14 + "  Nobles Artisans Peasants   Others")
            for index, month_data in enumerate(data):
                print(f"{get_month_string(index + begin_month)}"
                      f"{month_data['nobles']: >9}"
                      f"{month_data['artisans']: >9}"
                      f"{month_data['peasants']: >9}"
                      f"{month_data['others']: >9}")
        elif args[1] in {"resources_change", "rc"}:
            data = interface.history.resources_change()
            begin_month, data = set_months_of_history(args, interface, data)
            print("Resources changes stats:")
            print(" " * 14 + f"{'Nobles': ^35}{'Artisans': ^35}"
                  f"{'Peasants': ^35}{'Others': ^35}")
            print(" " * 13 + f" {'food': ^6} {'wood': ^6} {'stone': ^6} "
                  f"{'iron': ^6} {'tools': ^6}" * 4)
            for index, month_data in enumerate(data):
                line = f"{get_month_string(index + begin_month)}"
                for social_class in month_data:
                    for resource in RESOURCES:
                        res = month_data[social_class].get(resource, 0)
                        line += f"{res_to_str(res): >7}"
                print(line)
        if args[1] in {"total_resources", "tr"}:
            data = interface.history.total_resources()
            begin_month, data = set_months_of_history(args, interface, data)
            print("Total resources stats:")
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
        assert len(args) == 2
        assert args[1].isalpha()
        if args[1] == "starting":
            print("This save name is prohibited. Please choose another one")
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
        interface.save_data(f"{args[1]}")
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


def state(args: list[str], interface: Interface):
    try:
        assert len(args) in {2, 3}
        assert args[1] in {
            "population", "resources", "prices", "total_resources",
            "p", "r", "pr", "tr"
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
                social_class.class_name: History.round_dict_values(
                    social_class.resources, 1
                )
                for social_class
                in interface.state.classes
            }
            print("Current resources:")
            line = " " * 8
            for resource in RESOURCES:
                line += f"{resource: >7}"
            print(line)
            for class_name in CLASSES:
                line = f"{class_name: >8}"
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
                data += social_class.resources
            print("Current total resources:")
            for resource, value in data.items():
                print(f"{resource: >5}: {res_to_str(value)}")
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
        print("Invalid syntax. See help for proper usage of save command")
