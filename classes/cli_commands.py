from math import floor, log10
from .constants import MODIFIERS, MONTHS, RESOURCES


def help():
    print("List of available commands:")
    print("exit - shuts down the program")
    print("save <DIR> - saves the game state into saves/<DIR> directory")
    print("next <AMOUNT> - ends the month and advances to the next <AMOUNT> "
          "times - only once if <AMOUNT> not specified")
    print("history <STAT> <MONTHS> - shows the history of the "
          "country")
    print("    <STAT> decides which statistic to show")
    print("    Valid values:")
    print("        population")
    print("        resources")
    print("        prices")
    print("        growth_modifiers")
    print("        grown")
    print("        produced")
    print("        used")
    print("        consumed")
    print("    <MONTHS> decides how many months of history should"
          " be shown - left empty shows entire history")


def set_months_of_history(args, interface, data):
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


def round_resource(amount):
    if amount == 0:
        string = '0.00'
    else:
        digits = floor(log10(abs(amount))) + 1
        if digits < 4:
            rounded = round(float(amount), 2)
            string = str(rounded)
            if len(string.split('.')[1]) == 1:
                string += '0'
        elif digits == 4:
            rounded = round(float(amount), 1)
            string = str(rounded)
        else:
            rounded = round(amount)
            string = str(int(amount))
    return string


def round_price(amount):
    if amount == 0:
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


def history(args, interface):
    try:
        assert len(args) in {2, 3}
        assert args[1] in {
            "population", "resources", "prices",
            "growth_modifiers", "grown", "produced",
            "used", "consumed"
        }
        if len(args) == 3:
            assert args[2].isdigit()
            assert int(args[2]) > 0

        if args[1] == "population":
            data = interface.history.population_stats()
            begin_month, data = set_months_of_history(args, interface, data)
            print("Population stats:")
            print(" " * 14 + "  Nobles Artisans Peasants   Others")
            for index, month_data in enumerate(data):
                print(f"{get_month_string(index + begin_month)}"
                      f"{month_data['nobles']: >9}"
                      f"{month_data['artisans']: >9}"
                      f"{month_data['peasants']: >9}"
                      f"{month_data['others']: >9}")
        elif args[1] == "resources":
            data = interface.history.resources_stats()
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
                        line += f"{round_resource(res): >7}"
                print(line)
        elif args[1] == "prices":
            data = interface.history.prices_stats()
            begin_month, data = set_months_of_history(args, interface, data)
            print("Prices stats:")
            print(" " * 14 + "  Food    Wood   Stone    Iron   Tools")
            for index, month_data in enumerate(data):
                print(f"{get_month_string(index + begin_month)}"
                      f" {round_price(month_data['food']): >7}"
                      f" {round_price(month_data['wood']): >7}"
                      f" {round_price(month_data['stone']): >7}"
                      f" {round_price(month_data['iron']): >7}"
                      f" {round_price(month_data['tools']): >7}")
        elif args[1] == "growth_modifiers":
            data = interface.history.growth_modifiers_stats()
            begin_month, data = set_months_of_history(args, interface, data)
            print("Growth modifiers stats:")

            print(" " * 14 + f"{'Nobles': ^27}{'Artisans': ^27}"
                  f"{'Peasants': ^27}{'Others': ^27}")
            print(" " * 13 + "    Base  Starving Freezing" * 4)
            for index, month_data in enumerate(data):
                line = f"{get_month_string(index + begin_month)}"
                for social_class in month_data:
                    for modifier in MODIFIERS:
                        mod = month_data[social_class].get(modifier, 0)
                        line += f" {round_price(mod): >8}"
                print(line)
        elif args[1] == "grown":
            data = interface.history.growth_stats()
            begin_month, data = set_months_of_history(args, interface, data)
            print("Grown population stats:")
            print(" " * 14 + "  Nobles Artisans Peasants   Others")
            for index, month_data in enumerate(data):
                print(f"{get_month_string(index + begin_month)}"
                      f"{month_data['nobles']: >9}"
                      f"{month_data['artisans']: >9}"
                      f"{month_data['peasants']: >9}"
                      f"{month_data['others']: >9}")
        elif args[1] == "produced":
            data = interface.history.production_stats()
            begin_month, data = set_months_of_history(args, interface, data)
            print("Produced resources stats:")
            print(" " * 14 + f"{'Nobles': ^35}{'Artisans': ^35}"
                  f"{'Peasants': ^35}{'Others': ^35}")
            print(" " * 13 + f" {'food': ^6} {'wood': ^6} {'stone': ^6} "
                  f"{'iron': ^6} {'tools': ^6}" * 4)
            for index, month_data in enumerate(data):
                line = f"{get_month_string(index + begin_month)}"
                for social_class in month_data:
                    for resource in RESOURCES:
                        res = month_data[social_class].get(resource, 0)
                        line += f"{round_resource(res): >7}"
                print(line)
        elif args[1] == "used":
            data = interface.history.usage_stats()
            begin_month, data = set_months_of_history(args, interface, data)
            print("Resources used for production stats:")
            print(" " * 14 + f"{'Nobles': ^35}{'Artisans': ^35}"
                  f"{'Peasants': ^35}{'Others': ^35}")
            print(" " * 13 + f" {'food': ^6} {'wood': ^6} {'stone': ^6} "
                  f"{'iron': ^6} {'tools': ^6}" * 4)
            for index, month_data in enumerate(data):
                line = f"{get_month_string(index + begin_month)}"
                for social_class in month_data:
                    for resource in RESOURCES:
                        res = month_data[social_class].get(resource, 0)
                        line += f"{round_resource(res): >7}"
                print(line)
        elif args[1] == "consumed":
            data = interface.history.consumption_stats()
            begin_month, data = set_months_of_history(args, interface, data)
            print("Consumed resources stats:")
            print(" " * 14 + f"{'Nobles': ^14}{'Artisans': ^14}"
                  f"{'Peasants': ^14}{'Others': ^14}")
            print(" " * 13 + f" {'food': >6} {'wood': >6}" * 4)
            for index, month_data in enumerate(data):
                line = f"{get_month_string(index + begin_month)}"
                for social_class in month_data:
                    for resource in ['food', 'wood']:
                        res = month_data[social_class].get(resource, 0)
                        line += f"{round_resource(res): >7}"
                print(line)
    except AssertionError:
        print("Invalid syntax. See help for proper usage of history command")


def save(args, interface):
    try:
        assert len(args) == 2
        assert args[1].isalpha()
        interface.save_data(f"saves/{args[1]}.json")
        print(f"Saved the game state into saves/{args[1]}.json")
    except AssertionError:
        print("Invalid syntax. See help for proper usage of save command")


def next(args, interface):
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
    except Exception:
        print("Invalid syntax. See help for proper usage of next command")
