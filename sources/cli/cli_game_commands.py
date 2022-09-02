# Advanced commands for the state.
# These commands, combined with the basic ones, allow the program to function
# as a game.


from ..abstract_interface.interface import (EmptyClassError, Interface,
                                            InvalidArgumentError,
                                            NotEnoughClassPopulation,
                                            NotEnoughClassResources,
                                            NotEnoughGovtResources,
                                            check_arg)
from ..auxiliaries.enums import (CLASS_NAME_STR, RESOURCE_STR, Class_Name,
                                 Resource)
from .cli_commands import (InvalidCommand, fill_command, price_to_str,
                           res_to_str)


def transfer(args: list[str], interface: Interface) -> None:
    """
    Transfers the given amount of a resource from government to the given
    class. Negative amount signifies a reverse direction of the transfer.
    Args should be: ["transfer", class_name, resource_name, amount]
    """
    try:
        check_arg(len(args) == 4, "invalid number of arguments")

        arg1s = fill_command(args[1], CLASS_NAME_STR)
        check_arg(len(arg1s) == 1, "argument 1 ambiguous or invalid")
        class_name = Class_Name[arg1s[0]]

        arg2s = fill_command(args[2], RESOURCE_STR)
        check_arg(len(arg2s) == 1, "argument 2 ambiguous or invalid")
        resource = Resource[arg2s[0]]

        try:
            amount = float(args[3])
        except ValueError:
            raise InvalidArgumentError("amount of resources not a number")

        try:
            interface.transfer_resources(class_name, resource, amount)
        except NotEnoughGovtResources:
            print("The government does not have enough resources for this"
                  " operation.")
        except NotEnoughClassResources:
            print("The chosen class does not have enough resources for this"
                  " operation.")
        except EmptyClassError:
            print("The chosen class is empty.")
    except InvalidArgumentError as e:
        print(f"Invalid syntax: {e}. See help for proper usage of transfer"
              " command")


def secure(args: list[str], interface: Interface) -> None:
    """
    Makes the given amount of a resource owned by the government untradeable
    (secured). Negative amount signifies making a resource tradeable again.
    Args should be: ["secure", resource, amount]
    """
    try:
        check_arg(len(args) in {2, 3}, "invalid number of arguments")

        arg1s = fill_command(args[1], RESOURCE_STR)
        check_arg(len(arg1s) == 1, "argument 1 ambiguous or invalid")
        resource = Resource[arg1s[0]]

        if len(args) == 3:
            try:
                amount = float(args[2])
            except ValueError:
                raise InvalidArgumentError("amount of resources not a number")
        else:
            amount = None

        try:
            interface.secure_resources(resource, amount)
        except NotEnoughGovtResources:
            print("The government does not have enough resources for this"
                  " operation.")
    except InvalidArgumentError as e:
        print(f"Invalid syntax: {e}. See help for proper usage of secure"
              " command")


def optimal(args: list[str], interface: Interface) -> None:
    """
    Sets government optimal amount of resource to the given value.
    Args should be: ["optimal", resource, amount]
    """
    try:
        check_arg(len(args) == 3, "invalid number of arguments")

        arg1s = fill_command(args[1], RESOURCE_STR)
        check_arg(len(arg1s) == 1, "argument 1 ambiguous or invalid")
        resource = Resource[arg1s[0]]

        try:
            amount = int(args[2])
        except ValueError:
            raise InvalidArgumentError

        interface.set_govt_optimal(resource, amount)
    except InvalidArgumentError as e:
        print(f"Invalid syntax: {e}. See help for proper usage of optimal"
              " command")


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
            line += f" {res_to_str(taxes[class_name]): ^8}"
        print(line)
    elif law == "tax_property":
        print("tax_property")
        print("Property tax rate (what part of the class' total resources will"
              " be taken each month):")
        print(" Nobles  Artisans Peasants  Others")
        taxes = interface.state.sm.tax_rates['property']
        for class_name in Class_Name:
            line += f" {res_to_str(taxes[class_name]): ^8}"
        print(line)
    elif law == "tax_income":
        print("tax_income")
        print("Income tax rate (what part of the class' profits earned this"
              " month will be taken each month):")
        print(" Nobles  Artisans Peasants  Others")
        taxes = interface.state.sm.tax_rates['income']
        for class_name in Class_Name:
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
        print(f"{price_to_str(prices.food): ^7}"
              f" {price_to_str(prices.wood): ^7}"
              f" {price_to_str(prices.stone): ^7}"
              f" {price_to_str(prices.iron): ^7}"
              f" {price_to_str(prices.tools): ^7}"
              f" {price_to_str(prices.land): ^7}")
    else:
        raise InvalidCommand("There is no law with the given name")


def laws(args: list[str], interface: Interface) -> None:
    """
    Sets or views the current laws of the country.
    Args should be: ["laws", "set" | "view", law, argument, value]
    Argument is only needed with some laws, value is only needed when setting.
    See help for more information.
    """
    try:
        check_arg(len(args) >= 2, "too few arguments")
        arg1s = fill_command(args[1], {"view", "set"})
        check_arg(len(arg1s) == 1, "argument 1 ambiguous or invalid")
        args[1] = arg1s[0]

        laws = {
            "tax_personal", "tax_property", "tax_income", "wage_minimum",
            "wage_government", "wage_autoregulation", "max_prices"
        }

        if args[1] == "view":
            check_arg(len(args) in {2, 3}, "invalid number of arguments")
            if len(args) == 2:
                args.append("")

            laws_for_help = fill_command(args[2], laws)
            for law in laws_for_help:
                print_law(law, interface)
        elif args[1] == "set":
            check_arg(len(args) in {4, 5}, "invalid number of arguments")

            arg2s = fill_command(args[2], laws)
            check_arg(len(arg2s) == 1, "argument 2 ambiguous or invalid")
            args[2] = arg2s[0]

            try:
                value = float(args[len(args) - 1])
            except ValueError:
                raise InvalidArgumentError("law value not a number")

            if args[2][:4] in {"tax_", "max_"}:
                check_arg(len(args) == 5, "invalid number of arguments")
                valid_args = CLASS_NAME_STR \
                    if args[2][:4] == "tax_" else RESOURCE_STR
                arg3s = fill_command(args[3], valid_args)
                check_arg(len(arg3s) == 1,
                          "argument 3 ambiguous or invalid")
                args[3] = arg3s[0]

                interface.set_law(args[2], args[3], value)
            else:
                check_arg(len(args) == 4, "invalid number of arguments")
                interface.set_law(args[2], None, value)
        else:
            raise InvalidArgumentError("argument 1 invalid")
    except InvalidArgumentError as e:
        print(f"Invalid syntax: {e}. See help for proper usage of laws"
              " command")


def promote(args: list[str], interface: Interface) -> None:
    """
    Forces a promotion using government resources.
    Args should be: ["promote", class_name, amount]
    Promotes {amount} people to {class_name}.
    """
    try:
        check_arg(len(args) == 3, "invalid number of arguments")

        valid_classes = CLASS_NAME_STR.copy()
        valid_classes.remove("others")
        arg1s = fill_command(args[1], valid_classes)
        check_arg(len(arg1s) == 1, "argument 1 ambiguous or invalid")
        class_name = Class_Name[arg1s[0]]

        try:
            amount = int(args[2])
        except ValueError:
            raise InvalidArgumentError

        try:
            interface.force_promotion(class_name, amount)
        except NotEnoughGovtResources:
            print("The government does not have enough resources for this"
                  " operation.")
        except NotEnoughClassPopulation:
            print("The class from which the promotion was to be done does not"
                  " have enough population.")
    except InvalidArgumentError as e:
        print(f"Invalid syntax: {e}. See help for proper usage of promote"
              " command")


def recruit(args: list[str], interface: Interface) -> None:
    """
    Recruits {amount} soldiers from {class_name}.
    Args should be: ["recruit", class_name, amount]
    """
    try:
        check_arg(len(args) == 3, "invalid number of arguments")

        arg1s = fill_command(args[1], CLASS_NAME_STR)
        check_arg(len(arg1s) == 1, "argument 1 ambiguous or invalid")
        class_name = Class_Name[arg1s[0]]

        try:
            amount = int(args[2])
        except ValueError:
            raise InvalidArgumentError

        try:
            interface.recruit(class_name, amount)
        except NotEnoughGovtResources:
            print("The government does not have enough resources for this"
                  " operation.")
        except NotEnoughClassPopulation:
            print("The class from which the recruitment was to be done does "
                  "not have enough population.")
    except InvalidArgumentError as e:
        print(f"Invalid syntax: {e}. See help for proper usage of promote"
              " command")


def fight(args: list[str], interface: Interface) -> None:
    """
    Sends all soldiers to combat.
    Args should be: ["fight", "crime" | "plunder" | "conquest"]
    """
    try:
        check_arg(len(args) == 2, "invalid number of arguments")

        if interface.state.government.soldiers.number < 1:
            print("The government does not have enough soldiers for this"
                  " operation.")
            return
        if interface.fought:
            print("The government cannot conduct attacks more than once a"
                  " month.")
            return

        targets = {"crime", "plunder", "conquest"}
        arg1s = fill_command(args[1], targets)
        check_arg(len(arg1s) == 1, "argument 1 ambiguous or invalid")
        target = arg1s[0]

        results = interface.fight(target)
        dead_soldiers = results[1] if __debug__ else round(results[1], 0)
        print("The battle has been", "won." if results[0] else "lost.")
        print(dead_soldiers.knights,
              f"knight{'s' if dead_soldiers.knights != 1 else ''} and",
              dead_soldiers.footmen,
              f"footm{'e' if dead_soldiers.footmen != 1 else 'a'}n died.")
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
