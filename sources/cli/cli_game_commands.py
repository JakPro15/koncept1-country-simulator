# Advanced commands for the state.
# These commands, combined with the basic ones, allow the program to function
# as a game.


from ..abstract_interface.interface import (
    Interface,
    NotEnoughClassPopulation,
    NotEnoughClassResources,
    NotEnoughGovtResources,
    check_input,
    InvalidArgumentError
)
from .cli_commands import (
    InvalidCommand,
    fill_command,
    res_to_str,
    price_to_str
)
from ..auxiliaries.constants import CLASSES, RESOURCES


def transfer(args: list[str], interface: Interface):
    """
    Transfers the given amount of a resource from government to the given
    class. Negative amount signifies a reverse direction of the transfer.
    """
    try:
        check_input(len(args) == 4, "invalid number of arguments")

        args[1] = fill_command(args[1], CLASSES)
        check_input(len(args[1]) == 1, "argument 1 ambiguous or invalid")
        args[1] = args[1][0]

        args[2] = fill_command(args[2], RESOURCES)
        check_input(len(args[2]) == 1, "argument 2 ambiguous or invalid")
        args[2] = args[2][0]

        try:
            args[3] = float(args[3])
        except ValueError:
            raise InvalidArgumentError("amount of resources not a number")

        try:
            interface.transfer_resources(args[1], args[2], args[3])
        except NotEnoughGovtResources:
            print("The government does not have enough resources for this"
                  " operation.")
        except NotEnoughClassResources:
            print("The chosen class does not have enough resources for this"
                  " operation.")
    except InvalidArgumentError as e:
        print(f"Invalid syntax: {e}. See help for proper usage of transfer"
              " command")


def secure(args: list[str], interface: Interface):
    """
    Makes the given amount of a resource owned by the government untradeable
    (secured). Negative amount signifies making a resource tradeable again.
    """
    try:
        check_input(len(args) in {2, 3}, "invalid number of arguments")

        args[1] = fill_command(args[1], RESOURCES)
        check_input(len(args[1]) == 1, "argument 1 ambiguous or invalid")
        args[1] = args[1][0]

        if len(args) == 3:
            try:
                args[2] = float(args[2])
            except ValueError:
                raise InvalidArgumentError("amount of resources not a number")
        else:
            args.append(None)

        try:
            interface.secure_resources(args[1], args[2])
        except NotEnoughGovtResources:
            print("The government does not have enough resources for this"
                  " operation.")
    except InvalidArgumentError as e:
        print(f"Invalid syntax: {e}. See help for proper usage of secure"
              " command")


def optimal(args: list[str], interface: Interface):
    """
    Sets government optimal amount of resource to the given value.
    """
    try:
        check_input(len(args) == 3, "invalid number of arguments")

        args[1] = fill_command(args[1], RESOURCES)
        check_input(len(args[1]) == 1, "argument 1 ambiguous or invalid")
        args[1] = args[1][0]

        try:
            args[2] = int(args[2])
        except ValueError:
            raise InvalidArgumentError

        interface.set_govt_optimal(args[1], args[2])
    except InvalidArgumentError as e:
        print(f"Invalid syntax: {e}. See help for proper usage of optimal"
              " command")


def print_law(law: str, interface: Interface):
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
        for class_name in CLASSES:
            line += f" {res_to_str(taxes[class_name]): ^8}"
        print(line)
    elif law == "tax_property":
        print("tax_property")
        print("Property tax rate (what part of the class' total resources will"
              " be taken each month):")
        print(" Nobles  Artisans Peasants  Others")
        taxes = interface.state.sm.tax_rates['property']
        for class_name in CLASSES:
            line += f" {res_to_str(taxes[class_name]): ^8}"
        print(line)
    elif law == "tax_income":
        print("tax_income")
        print("Income tax rate (what part of the class' profits earned this"
              " month will be taken each month):")
        print(" Nobles  Artisans Peasants  Others")
        taxes = interface.state.sm.tax_rates['income']
        for class_name in CLASSES:
            line += f" {res_to_str(taxes[class_name]): ^8}"
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
        print(f"{price_to_str(prices['food']): ^7}"
              f" {price_to_str(prices['wood']): ^7}"
              f" {price_to_str(prices['stone']): ^7}"
              f" {price_to_str(prices['iron']): ^7}"
              f" {price_to_str(prices['tools']): ^7}"
              f" {price_to_str(prices['land']): ^7}")
    else:
        raise InvalidCommand


def laws(args: list[str], interface: Interface):
    """
    Sets or views the current laws of the country.
    """
    try:
        check_input(len(args) >= 2, "too few arguments")
        args[1] = fill_command(args[1], {"view", "set"})
        check_input(len(args[1]) == 1, "argument 1 ambiguous or invalid")
        args[1] = args[1][0]

        laws = {
            "tax_personal", "tax_property", "tax_income", "wage_minimum",
            "wage_government", "wage_autoregulation", "max_prices"
        }

        if args[1] == "view":
            check_input(len(args) in {2, 3}, "invalid number of arguments")
            if len(args) == 2:
                args.append("")

            args[2] = fill_command(args[2], laws)
            for law in args[2]:
                print_law(law, interface)
        elif args[1] == "set":
            check_input(len(args) in {4, 5}, "invalid number of arguments")

            args[2] = fill_command(args[2], laws)
            check_input(len(args[2]) == 1, "argument 2 ambiguous or invalid")
            args[2] = args[2][0]

            try:
                args[len(args) - 1] = float(args[len(args) - 1])
            except ValueError:
                raise InvalidArgumentError("law value not a number")

            if args[2][:4] in {"tax_", "max_"}:
                check_input(len(args) == 5, "invalid number of arguments")
                valid_args = CLASSES if args[2][:4] == "tax_" else RESOURCES
                args[3] = fill_command(args[3], valid_args)
                check_input(len(args[3]) == 1,
                            "argument 3 ambiguous or invalid")
                args[3] = args[3][0]

                interface.set_law(args[2], args[3], args[4])
            else:
                check_input(len(args) == 4, "invalid number of arguments")
                interface.set_law(args[2], None, args[3])
        else:
            raise InvalidArgumentError("argument 1 invalid")
    except InvalidArgumentError as e:
        print(f"Invalid syntax: {e}. See help for proper usage of laws"
              " command")


def promote(args: list[str], interface: Interface):
    """
    Forces a promotion using government resources.
    """
    try:
        check_input(len(args) == 3, "invalid number of arguments")

        valid_classes = CLASSES.copy()
        valid_classes.remove("others")
        args[1] = fill_command(args[1], valid_classes)
        check_input(len(args[1]) == 1, "argument 1 ambiguous or invalid")
        args[1] = args[1][0]

        try:
            args[2] = int(args[2])
        except ValueError:
            raise InvalidArgumentError

        try:
            interface.force_promotion(args[1], args[2])
        except NotEnoughGovtResources:
            print("The government does not have enough resources for this"
                  " operation.")
        except NotEnoughClassPopulation:
            print("The class from which the promotion was to be done does not"
                  " have enough population.")
    except InvalidArgumentError as e:
        print(f"Invalid syntax: {e}. See help for proper usage of promote"
              " command")


def recruit(args: list[str], interface: Interface):
    """
    Recruits soldiers.
    """
    try:
        check_input(len(args) == 3, "invalid number of arguments")

        args[1] = fill_command(args[1], CLASSES)
        check_input(len(args[1]) == 1, "argument 1 ambiguous or invalid")
        args[1] = args[1][0]

        try:
            args[2] = int(args[2])
        except ValueError:
            raise InvalidArgumentError

        try:
            interface.recruit(args[1], args[2])
        except NotEnoughGovtResources:
            print("The government does not have enough resources for this"
                  " operation.")
        except NotEnoughClassPopulation:
            print("The class from which the recruitment was to be done does "
                  "not have enough population.")
    except InvalidArgumentError as e:
        print(f"Invalid syntax: {e}. See help for proper usage of promote"
              " command")


def fight(args: list[str], interface: Interface):
    """
    Sends all soldiers to combat.
    """
    try:
        check_input(len(args) == 2, "invalid number of arguments")

        if interface.state.government.soldiers_population < 1:
            print("The government does not have enough soldiers for this"
                  " operation.")
            return
        if interface.state.fought:
            print("The government cannot conduct attacks more than once a"
                  " month.")
            return

        arguments = {"crime", "plunder", "conquest"}
        args[1] = fill_command(args[1], arguments)
        check_input(len(args[1]) == 1, "argument 1 ambiguous or invalid")
        args[1] = args[1][0]

        results = interface.fight(args[1])
        dead_soldiers = results[1] if __debug__ else round(results[1])
        print("The battle has been", "won." if results[0] else "lost.")
        print(dead_soldiers["knights"],
              f"knight{'s' if dead_soldiers['knights'] != 1 else ''} and",
              dead_soldiers["footmen"],
              f"footm{'e' if dead_soldiers['footmen'] != 1 else 'a'}n died.")
        if args[1] == "crime":
            dead_brigands = results[2] if __debug__ else round(results[2])
            print(dead_brigands,
                  f"brigand{'s' if dead_brigands != 1 else ''} died.")
        elif args[1] == "conquest":
            print("Conquered", round(results[2], 2), "land.")
        elif args[1] == "plunder":
            print("Plundered", round(results[2], 2),
                  "food, wood, stone, iron and tools.")
    except InvalidArgumentError as e:
        print(f"Invalid syntax: {e}. See help for proper usage of promote"
              " command")
