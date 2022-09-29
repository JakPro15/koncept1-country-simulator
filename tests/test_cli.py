import os
import os.path
import re
import shutil
from math import inf, nan
from random import randint
from typing import Any, Callable, Type, TypeVar

from pytest import raises
from sources.state.social_classes.class_file import Class
from sources.state.state_data import State_Data

from ..sources.abstract_interface.interface import Interface, SaveAccessError
from ..sources.auxiliaries.enums import Class_Name, Month, Resource
from ..sources.auxiliaries.soldiers import Soldiers
from ..sources.auxiliaries.testing import (capture_standard_output, replace,
                                           set_standard_input)
from ..sources.cli import cli_commands, cli_game_commands
from ..sources.cli.cli_commands import (COMMANDS, Print_Type, ShutDownCommand,
                                        delete_save, exit_game,
                                        get_modifiers_from_class,
                                        get_modifiers_from_dict,
                                        get_month_string, help_, help_command,
                                        history, next_command, print_resources,
                                        save, set_months_of_history, state,
                                        validate_target_name)
from ..sources.cli.cli_game_commands import (LAWS, InternalCommandError,
                                             InvalidArgumentError, fight,
                                             fill_command, format_iterable,
                                             laws, optimal, promote, recruit,
                                             round_format, secure, transfer)
from ..sources.state.social_classes.artisans import Artisans
from ..sources.state.social_classes.nobles import Nobles
from ..sources.state.social_classes.others import Others
from ..sources.state.social_classes.peasants import Peasants


def test_fill_command():
    cmds = {"abcde", "abcd", "hehe xd", "aaaaa", "bcd"}
    assert fill_command("", cmds) == cmds
    assert fill_command("a", cmds) == {"abcde", "abcd", "aaaaa"}
    assert fill_command("abcd", cmds) == {"abcde", "abcd"}
    assert fill_command("bcd", cmds) == {"bcd"}


def test_round_format_zero_extension():
    assert round_format(2, 1, 4) == "2.0"
    assert round_format(2.1, 3, 8) == "2.100"
    assert round_format(2.1, 4, 4) == "2.10"
    assert round_format(-2.1, 5, 5) == "-2.10"


def test_round_format_rounding():
    assert round_format(2.145, 2, 8) == "2.15"
    assert round_format(2.144, 2, 8) == "2.14"
    assert round_format(2.145, 8, 4) == "2.15"
    assert round_format(2.144, 8, 4) == "2.14"
    assert round_format(-2.145, 8, 5) == "-2.15"
    assert round_format(-2.144, 8, 5) == "-2.14"


def test_round_format_rounding_to_integer():
    # round(214.5) evaluates to 214 - nice IEEE754
    assert round_format(214.51, 0, 8) == "215"
    assert round_format(214.4, 0, 8) == "214"
    assert round_format(214.51, 8, 4) == "215"
    assert round_format(214.4, 8, 4) == "214"
    assert round_format(-214.51, 8, 5) == "-215"
    assert round_format(-214.4, 8, 5) == "-214"
    assert round_format(-214.51, 8, 4) == "-215"
    assert round_format(-214.4, 8, 4) == "-214"


def test_round_format_exceeding_max_chars():
    assert round_format(214.4, 0, 2) == "214"
    assert round_format(214.4, 4, 1) == "214"


def test_round_format_exceptions_and_special_cases():
    with raises(ValueError):
        round_format(214.5, -1, 4)
    with raises(ValueError):
        round_format(214.5, 0, 0)
    with raises(ValueError):
        round_format(214.5, 1, -1)
    assert round_format(inf, 2, 5) == "∞"
    assert round_format(-inf, 2, 5) == "-∞"
    assert round_format(nan, 2, 5) == "nan"
    assert round_format(0, 2, 5) == "0.00"
    assert round_format(0, 2, 2) == "0"


def test_format_iterable():
    assert format_iterable(["a", "b", "ab"]) == '"a", "b", "ab"'
    assert format_iterable({2, 1}) in {'"1", "2"', '"2", "1"'}
    assert format_iterable([]) == ""
    assert format_iterable([{"a": 2}]) == "\"{'a': 2}\""


def test_transfer():
    with raises(InvalidArgumentError):
        transfer(["transfer"], Interface())
    with raises(InvalidArgumentError):
        transfer(["transfer", "nobles"], Interface())
    with raises(InvalidArgumentError):
        transfer(["transfer", "nobles", "wood"], Interface())
    with raises(InvalidArgumentError):
        transfer(["transfer", "nobles", "wood", "2", "yeet"], Interface())
    with raises(InvalidArgumentError):
        transfer(["transfer", "government", "wood", "20"], Interface())
    with raises(InvalidArgumentError):
        transfer(["transfer", "nobles", "beka z typa", "20"], Interface())
    with raises(InvalidArgumentError):
        transfer(["transfer", "nobles", "wood", "hehe xd"], Interface())

    calls: list[Any] = []

    def fake_transfer(self: Interface, *args: Any) -> None:
        calls.append(args)

    with replace(Interface, "transfer_resources", fake_transfer), \
         capture_standard_output() as stdout:
        transfer(["transfer", "no", "wood", "2"], Interface())
        transfer(["se", "p", "s", "-100"], Interface())
        transfer(["transf", "othe", "la", "20.05"], Interface())

        assert stdout.getvalue() == ""

    assert calls == [
        (Class_Name.nobles, Resource.wood, 2),
        (Class_Name.peasants, Resource.stone, -100),
        (Class_Name.others, Resource.land, 20.05)
    ]


def test_secure():
    with raises(InvalidArgumentError):
        secure(["secure"], Interface())
    with raises(InvalidArgumentError):
        secure(["secure", "wood", "23", "bonk"], Interface())
    with raises(InvalidArgumentError):
        secure(["secure", "stone", "-34", "2", "yeet"], Interface())
    with raises(InvalidArgumentError):
        secure(["secure", "beka", "23"], Interface())
    with raises(InvalidArgumentError):
        secure(["secure", "wood", "z typa"], Interface())

    calls: list[Any] = []

    def fake_secure(self: Interface, *args: Any) -> None:
        calls.append(args)

    with replace(Interface, "secure_resources", fake_secure), \
         capture_standard_output() as stdout:
        secure(["secure", "wood", "2"], Interface())
        secure(["tra", "stone", "-100"], Interface())
        secure(["secure", "land", "200"], Interface())

        assert stdout.getvalue() == ""

    assert calls == [
        (Resource.wood, 2),
        (Resource.stone, -100),
        (Resource.land, 200)
    ]


def test_optimal():
    with raises(InvalidArgumentError):
        optimal(["optimal"], Interface())
    with raises(InvalidArgumentError):
        optimal(["optimal", "wood", "23", "bonk"], Interface())
    with raises(InvalidArgumentError):
        optimal(["optimal", "stone", "-34", "2", "yeet"], Interface())
    with raises(InvalidArgumentError):
        optimal(["optimal", "beka", "23"], Interface())
    with raises(InvalidArgumentError):
        optimal(["optimal", "wood", "z typa"], Interface())

    calls: list[Any] = []

    def fake_optimal(self: Interface, *args: Any) -> None:
        calls.append(args)

    with replace(Interface, "set_govt_optimal", fake_optimal), \
         capture_standard_output() as stdout:
        optimal(["optimal", "wood", "2"], Interface())
        optimal(["tra", "stone", "-100"], Interface())
        optimal(["optimal", "land", "200"], Interface())

        assert stdout.getvalue() == ""

    assert calls == [
        (Resource.wood, 2),
        (Resource.stone, -100),
        (Resource.land, 200)
    ]


def test_laws_view():
    with raises(InvalidArgumentError):
        laws(["laws"], Interface())

    with raises(InvalidArgumentError):
        laws(["laws", "abc"], Interface())

    with raises(InvalidArgumentError):
        laws(["laws", "view", "h"], Interface())

    with raises(InvalidArgumentError):
        laws(["laws", "view", "tax_property", "nobles"], Interface())

    with raises(InvalidArgumentError):
        laws(["laws", "view", "tax_property", "nobles", "abc"], Interface())

    interface = Interface()
    calls: set[str] = set()
    calls_number = 0

    def fake_print_law(law: str, interf: Interface) -> None:
        calls.add(law)
        nonlocal calls_number
        calls_number += 1
        assert interf == interface

    with replace(cli_game_commands, "print_law", fake_print_law), \
         capture_standard_output():
        laws(["laws", "view", "tax_property"], interface)
        assert calls == {"tax_property"}
        assert calls_number == 1

        laws(["laws", "view", "tax_"], interface)
        assert calls == {"tax_property", "tax_personal", "tax_income"}
        assert calls_number == 4

        laws(["laws", "view", "max_pri"], interface)
        assert calls == {"tax_property", "tax_personal",
                         "tax_income", "max_prices"}
        assert calls_number == 5

        laws(["laws", "view"], interface)
        assert calls == LAWS
        assert calls_number == len(LAWS) + 5


def test_laws_set():
    with raises(InvalidArgumentError):
        laws(["laws", "set"], Interface())

    with raises(InvalidArgumentError):
        laws(["laws", "set", "tax_property"], Interface())

    with raises(InvalidArgumentError):
        laws(["laws", "set", "tax_property", "2"], Interface())

    with raises(InvalidArgumentError):
        laws(["laws", "set", "tax_property", "government", "0.9"], Interface())

    with raises(InvalidArgumentError):
        laws(["laws", "set", "tax_property", "nobles", "abc"], Interface())

    with raises(InvalidArgumentError):
        laws(["laws", "set", "tax_", "nobles", "0.9"], Interface())

    with raises(InvalidArgumentError):
        laws(["laws", "set", "max_prices", "dood", "9"], Interface())

    with raises(InvalidArgumentError):
        laws(["laws", "set", "tax_proper", "nobles", "2", "abc"], Interface())

    calls: list[Any] = []

    def fake_set_law(self: Interface, *args: Any) -> None:
        calls.append(args)

    with replace(Interface, "set_law", fake_set_law), \
         capture_standard_output() as stdout:
        laws(["laws", "set", "tax_property", "nobles", "0.9"], Interface())
        assert stdout.getvalue() == ""
        laws(["laws", "set", "max_pri", "food", "4"], Interface())
        assert stdout.getvalue() == ""
        laws(["laws", "set", "wage_mi", "0.4"], Interface())
        assert stdout.getvalue() == ""

    assert calls == [
        ("tax_property", "nobles", 0.9),
        ("max_prices", "food", 4),
        ("wage_minimum", None, 0.4)
    ]


def test_promote():
    with raises(InvalidArgumentError):
        promote(["promote"], Interface())
    with raises(InvalidArgumentError):
        promote(["promote", "peasants", "23", "bonk"], Interface())
    with raises(InvalidArgumentError):
        promote(["promote", "artisans", "-34", "2", "yeet"], Interface())
    with raises(InvalidArgumentError):
        promote(["promote", "beka", "23"], Interface())
    with raises(InvalidArgumentError):
        promote(["promote", "peasants", "z typa"], Interface())

    calls: list[Any] = []

    def fake_promote(self: Interface, *args: Any) -> None:
        calls.append(args)

    with replace(Interface, "force_promotion", fake_promote), \
         capture_standard_output() as stdout:
        promote(["promote", "peasants", "2"], Interface())
        promote(["pro", "arti", "50"], Interface())
        promote(["promote", "n", "200"], Interface())

        assert stdout.getvalue() == ""

    assert calls == [
        (Class_Name.peasants, 2),
        (Class_Name.artisans, 50),
        (Class_Name.nobles, 200)
    ]


def test_recruit():
    with raises(InvalidArgumentError):
        recruit(["recruit"], Interface())
    with raises(InvalidArgumentError):
        recruit(["recruit", "peasants", "23", "bonk"], Interface())
    with raises(InvalidArgumentError):
        recruit(["recruit", "artisans", "-34", "2", "yeet"], Interface())
    with raises(InvalidArgumentError):
        recruit(["recruit", "beka", "23"], Interface())
    with raises(InvalidArgumentError):
        recruit(["recruit", "peasants", "z typa"], Interface())

    calls: list[Any] = []

    def fake_recruit(self: Interface, *args: Any) -> None:
        calls.append(args)

    with replace(Interface, "recruit", fake_recruit), \
         capture_standard_output() as stdout:
        recruit(["recruit", "peasants", "2"], Interface())
        recruit(["rec", "arti", "50"], Interface())
        recruit(["recruit", "n", "200"], Interface())

        assert stdout.getvalue() == ""

    assert calls == [
        (Class_Name.peasants, 2),
        (Class_Name.artisans, 50),
        (Class_Name.nobles, 200)
    ]


def test_fight():
    # Does not test result printing.
    interface = Interface()
    interface.state.government.soldiers = Soldiers(2)

    with raises(InvalidArgumentError):
        fight(["fight"], interface)
    with raises(InvalidArgumentError):
        fight(["fight", "c"], interface)
    with raises(InvalidArgumentError):
        fight(["fight", "abc"], interface)
    with raises(InvalidArgumentError):
        fight(["fight", "conquest", "200"], interface)
    with raises(InvalidArgumentError):
        fight(["fight", "crime", "beka z typa"], interface)

    calls: list[Any] = []

    def fake_fight(self: Interface, *args: Any
                   ) -> tuple[bool, Soldiers, float]:
        calls.append(args)
        return True, Soldiers(2), 20

    with replace(Interface, "fight", fake_fight), \
         capture_standard_output() as stdout:
        fight(["fight", "crime"], interface)
        fight(["fig", "p"], interface)
        fight(["fight", "conq"], interface)

        assert stdout.getvalue() != ""

    assert calls == [
        ("crime",),
        ("plunder",),
        ("conquest",)
    ]


def test_help_command():
    for command in set(COMMANDS) | {"laws set", "laws view"}:
        if command == "laws":
            continue
        with capture_standard_output() as stdout:
            help_command(command)
            assert stdout.getvalue() != ""

    with raises(InternalCommandError):
        help_command("laws")
    with raises(InternalCommandError):
        help_command("abc")
    with raises(InternalCommandError):
        help_command("histo")


def test_help():
    calls: set[str] = set()

    def fake_help_command(command: str) -> None:
        calls.add(command)

    def fake_help_default() -> None:
        calls.add("default")

    with replace(cli_commands, "help_command", fake_help_command), \
         replace(cli_commands, "help_default", fake_help_default):
        help_(["help"], ...)
        assert calls == {"default"}

        calls = set()
        help_(["help", "laws"], ...)
        assert calls == {"laws set", "laws view"}

        calls = set()
        help_(["help", "s", "abc"], ...)
        assert calls == {"state", "save", "secure"}

        calls = set()
        help_(["help", "tra", "abc", "def"], ...)
        assert calls == {"transfer"}


def test_set_months_of_history():
    interface = Interface()

    def set_month_and_year(month: Month, year: int) -> list[int]:
        interface.state.month = month
        interface.state.year = year
        length = year * 12 + month.value
        return list(range(length))

    assert set_months_of_history(None, interface, []) == (0, [])

    data = set_month_and_year(Month.April, 0)
    assert set_months_of_history(None, interface, data) == (0, [0, 1, 2])
    assert set_months_of_history(2, interface, data) == (1, [1, 2])

    data = set_month_and_year(Month.June, 11)
    assert set_months_of_history(None, interface, data) == \
        (0, list(range(11 * 12 + 5)))
    assert set_months_of_history(5, interface, data) == \
        (11 * 12, list(range(11 * 12, 11 * 12 + 5)))


def test_get_month_string():
    for i in range(1000, ):
        string = get_month_string(i)
        assert re.match(rf"^\s*{Month(i % 12).name}\s+{i // 12}\s*$", string)
        assert len(string) == 13


def test_get_modifiers_from_dict():
    keys = ["starving", "freezing", "promoted_from",
            "demoted_from", "promoted_to", "demoted_to"]

    def create_dict(content: str) -> dict[str, bool]:
        result: dict[str, bool] = {}
        for key, val in zip(keys, content):
            result[key] = (val == '1')
        return result

    assert get_modifiers_from_dict(create_dict("110100")) == "SF D  "
    assert get_modifiers_from_dict(create_dict("000000")) == "      "
    assert get_modifiers_from_dict(create_dict("111111")) == "SFPDpd"
    assert get_modifiers_from_dict(create_dict("010101")) == " F D d"
    assert get_modifiers_from_dict(create_dict("101010")) == "S P p "


def test_validate_target_name():
    with raises(InvalidArgumentError):
        validate_target_name("")
    with raises(InvalidArgumentError):
        validate_target_name("abc")
    with raises(InvalidArgumentError):
        validate_target_name("nogles")

    assert validate_target_name("n") == "nobles"
    assert validate_target_name("a") == "artisans"
    assert validate_target_name("p") == "peasants"
    assert validate_target_name("o") == "others"
    assert validate_target_name("g") == "government"
    assert validate_target_name("nobles") == "nobles"
    assert validate_target_name("peas") == "peasants"


def test_print_resources():
    last_print_his_call: Any = ()

    # print_history args:
    # title: str, type: Print_Type, begin_month: int, data: list[dict[str, V]],
    # transform: Callable[[V], str]
    def fake_print_history(*args: Any) -> None:
        nonlocal last_print_his_call
        last_print_his_call = args

    with replace(cli_commands, "print_history", fake_print_history):
        data: list[dict[str, dict[str, float]]] = [
            {"nobles": {"a": 1},
             "artisans": {"b": 2},
             "peasants": {"c": 3}},
            {"nobles": {"c": 4},
             "artisans": {"b": 5},
             "peasants": {"a": 6}}
        ]
        print_resources(data, "nobles", 4, False)
        assert "esources" in last_print_his_call[0]
        assert "changes" not in last_print_his_call[0]
        assert last_print_his_call[1] == Print_Type.resources
        assert last_print_his_call[2] == 4
        assert last_print_his_call[3] == [
            {"a": 1},
            {"c": 4}
        ]

        print_resources(data, "artisans", 6, True)
        assert "esources" in last_print_his_call[0]
        assert "changes" in last_print_his_call[0]
        assert last_print_his_call[1] == Print_Type.resources
        assert last_print_his_call[2] == 6
        assert last_print_his_call[3] == [
            {"b": 2},
            {"b": 5}
        ]


def test_history_valid_args():
    interface = Interface()
    last_data_call: str = ""
    last_month_arg: int = -1
    data = list(range(10))
    last_print_res_call: tuple[str, bool] = ("", False)
    last_print_his_call: tuple[str, Print_Type] = ("", Print_Type.classes)

    def fake_data(arg: str) -> list[int]:
        nonlocal last_data_call
        last_data_call = arg
        return data

    def fake_set_months(months: int, interf: Interface, dat: list[int]
                        ) -> tuple[int, list[int]]:
        nonlocal last_month_arg
        last_month_arg = months
        assert dat is data
        assert interf is interface
        return 2, dat

    def fake_print_resources(full_data: list[dict[str, dict[str, float]]],
                             target_name: str, begin_month: int, changes: bool
                             ) -> None:
        assert begin_month == 2
        assert full_data == data
        nonlocal last_print_res_call
        last_print_res_call = (target_name, changes)

    V = TypeVar("V")

    def fake_print_history(
        title: str, type: Print_Type, begin_month: int,
        dat: list[dict[str, V]], transform: Callable[[V], str]
    ) -> None:
        assert begin_month == 2
        assert dat == data
        nonlocal last_print_his_call
        last_print_his_call = (title, type)

    def reset():
        nonlocal last_data_call
        last_data_call = ""
        nonlocal last_month_arg
        last_month_arg = -1
        nonlocal last_print_res_call
        last_print_res_call = ("", False)
        nonlocal last_print_his_call
        last_print_his_call = ("", Print_Type.classes)

    with replace(cli_commands, "print_resources", fake_print_resources), \
         replace(cli_commands, "print_history", fake_print_history), \
         replace(cli_commands, "set_months_of_history", fake_set_months):
        with replace(interface.history, "population",
                     lambda: fake_data("population")):
            history(["history", "pop", "6"], interface)
            assert last_data_call == "population"
            assert last_month_arg == 6
            assert last_print_res_call == ("", False)
            assert "opulation" in last_print_his_call[0]
            assert last_print_his_call[1] == Print_Type.classes

        reset()
        with replace(interface.history, "resources",
                     lambda: fake_data("resources")):
            history(["history", "resources", "nobles", "6"], interface)
            assert last_data_call == "resources"
            assert last_month_arg == 6
            assert last_print_res_call == ("nobles", False)
            assert last_print_his_call == ("", Print_Type.classes)

        reset()
        with replace(interface.history, "prices",
                     lambda: fake_data("prices")):
            history(["history", "prices", "6"], interface)
            assert last_data_call == "prices"
            assert last_month_arg == 6
            assert last_print_res_call == ("", False)
            assert "rices" in last_print_his_call[0]
            assert last_print_his_call[1] == Print_Type.resources

        reset()
        with replace(interface.history, "growth_modifiers",
                     lambda: fake_data("modifiers")):
            history(["history", "modifie", "6"], interface)
            assert last_data_call == "modifiers"
            assert last_month_arg == 6
            assert last_print_res_call == ("", False)
            assert "rowth" in last_print_his_call[0]
            assert "odifiers" in last_print_his_call[0]
            assert last_print_his_call[1] == Print_Type.classes

        reset()
        with replace(interface.history, "population_change",
                     lambda: fake_data("change_population")):
            history(["history", "change_population", "6"], interface)
            assert last_data_call == "change_population"
            assert last_month_arg == 6
            assert last_print_res_call == ("", False)
            assert "opulation" in last_print_his_call[0]
            assert "hange" in last_print_his_call[0]
            assert last_print_his_call[1] == Print_Type.classes

        reset()
        with replace(interface.history, "resources_change",
                     lambda: fake_data("change_resources")):
            history(["history", "change_res", "nobles", "6"], interface)
            assert last_data_call == "change_resources"
            assert last_month_arg == 6
            assert last_print_res_call == ("nobles", True)
            assert last_print_his_call == ("", Print_Type.classes)

        reset()
        with replace(interface.history, "total_resources",
                     lambda: fake_data("total_resources")):
            history(["history", "total_r", "6"], interface)
            assert last_data_call == "total_resources"
            assert last_month_arg == 6
            assert last_print_res_call == ("", False)
            assert "otal" in last_print_his_call[0]
            assert "esources" in last_print_his_call[0]
            assert last_print_his_call[1] == Print_Type.resources

        reset()
        with replace(interface.history, "employment",
                     lambda: fake_data("employment")):
            history(["history", "employment", "6"], interface)
            assert last_data_call == "employment"
            assert last_month_arg == 6
            assert last_print_res_call == ("", False)
            assert "mployment" in last_print_his_call[0]
            assert last_print_his_call[1] == Print_Type.employment

        reset()
        with replace(interface.history, "happiness",
                     lambda: fake_data("happiness")):
            history(["history", "happi", "6"], interface)
            assert last_data_call == "happiness"
            assert last_month_arg == 6
            assert last_print_res_call == ("", False)
            assert "appiness" in last_print_his_call[0]
            assert last_print_his_call[1] == Print_Type.classes


def test_history_invalid_args():
    def check(args: list[str]):
        with raises(InvalidArgumentError):
            history(["history"] + args, Interface())

    check(["chan", "abc"])
    check([])

    check(["population", "abc"])
    check(["population", "2", "abc"])

    check(["change_population", "abc"])
    check(["change_population", "2", "abc"])

    check(["resources"])
    check(["resources", "2"])
    check(["resources", "abc", "2"])
    check(["resources", "nobles", "abc"])
    check(["resources", "nobles", "2", "abc"])

    check(["change_resources"])
    check(["change_resources", "2"])
    check(["change_resources", "abc", "2"])
    check(["change_resources", "nobles", "abc"])
    check(["change_resources", "nobles", "2", "abc"])

    check(["prices", "abc"])
    check(["prices", "2", "abc"])

    check(["modifiers", "abc"])
    check(["modifiers", "2", "abc"])

    check(["total_resources", "abc"])
    check(["total_resources", "2", "abc"])

    check(["employment", "abc"])
    check(["employment", "2", "abc"])

    check(["happiness", "abc"])
    check(["happiness", "2", "abc"])


def test_save():
    calls: list[Any] = []

    def fake_save(self: Interface, *args: Any) -> None:
        calls.append(args)

    def error_mkdir(*args: Any) -> None:
        raise AssertionError("mkdir called when it wasn't expected")

    # Guarding against this test creating files
    with replace(Interface, "save_data", fake_save), \
         replace(os, "mkdir", error_mkdir):

        with raises(InvalidArgumentError):
            save(["save"], Interface())

        with capture_standard_output() as stdout:
            save(["save", "starting"], Interface())
            assert stdout.getvalue() != ""

        with raises(InvalidArgumentError):
            save(["save", "abc", "h"], Interface())

        with raises(InvalidArgumentError):
            save(["save", "ab3 c"], Interface())

        with raises(InvalidArgumentError):
            save(["save", "ab3/c"], Interface())

        with raises(InvalidArgumentError):
            save(["save", "$c"], Interface())

        with raises(InvalidArgumentError):
            save(["save", ".."], Interface())

        with raises(InvalidArgumentError):
            interface = Interface()
            interface.save_name = "ab3.c"
            save(["save"], interface)

        with capture_standard_output() as stdout:
            interface = Interface()
            interface.save_name = "starting"
            save(["save"], interface)
            assert stdout.getvalue() != ""

        def mkdir_raise(*args: Any, **kwargs: Any) -> None:
            raise FileExistsError

        with replace(os, "mkdir", mkdir_raise), \
             set_standard_input("0") as stdin, \
             capture_standard_output() as stdout:
            save(["save", "abc"], Interface())
            assert stdin.tell() == 1  # reading from stdin done
            assert stdout.getvalue() != ""

        with replace(os, "mkdir", mkdir_raise), \
             set_standard_input("ab\nc\n0") as stdin, \
             capture_standard_output() as stdout:
            save(["save", "abc"], Interface())
            assert stdin.tell() == 6  # reading from stdin done
            assert stdout.getvalue() != ""

        assert calls == []

        with replace(os, "mkdir", lambda *args: None), \
             set_standard_input("abc") as stdin, \
             capture_standard_output() as stdout:
            save(["save", "abc"], Interface())
            assert stdin.tell() == 0  # no reading from stdin
            assert stdout.getvalue() != ""
            assert calls == [("abc",)]

        with replace(os, "mkdir", mkdir_raise), \
             set_standard_input("1") as stdin, \
             capture_standard_output() as stdout:
            save(["save", "abcd"], Interface())
            assert stdin.tell() == 1  # reading from stdin done
            assert stdout.getvalue() != ""
            assert calls == [("abc",),
                             ("abcd",)]

        def save_data_raise(self: Interface, filename: str) -> None:
            raise SaveAccessError

        with replace(os, "mkdir", mkdir_raise), \
             set_standard_input("ab\ncc\n1\nab") as stdin, \
             capture_standard_output() as stdout, \
             replace(Interface, "save_data", save_data_raise):
            save(["save", "abcd"], Interface())
            assert stdin.tell() == 8  # reading from stdin done
            assert stdout.getvalue() != ""
            assert calls == [("abc",),
                             ("abcd",)]


def test_next_command():
    with raises(InvalidArgumentError):
        next_command(["next", "abc"], Interface())

    with raises(InvalidArgumentError):
        next_command(["next", "2", "abc"], Interface())

    with raises(InvalidArgumentError):
        next_command(["next", "0"], Interface())

    with raises(InvalidArgumentError):
        next_command(["next", "-2"], Interface())

    calls = 0

    def fake_next_month(self: Interface) -> None:
        nonlocal calls
        calls += 1

    with replace(Interface, "next_month", fake_next_month):
        with capture_standard_output() as stdout:
            next_command(["next"], Interface())
            assert stdout.getvalue() != ""
            assert calls == 1

        with capture_standard_output() as stdout:
            next_command(["next", "1"], Interface())
            assert stdout.getvalue() != ""
            assert calls == 2

        with capture_standard_output() as stdout:
            next_command(["next", "4"], Interface())
            assert stdout.getvalue() != ""
            assert calls == 6


def test_get_modifiers_from_class():
    state = State_Data()

    keys = ["starving", "freezing", "promoted_from",
            "demoted_from", "promoted_to", "demoted_to"]

    def create_class(class_: Type[Class], content: str) -> Class:
        class_obj = class_(state)
        for key, val in zip(keys, content):
            setattr(class_obj, key, val == '1')
        return class_obj

    assert get_modifiers_from_class(
        create_class(Nobles, "001011")) == "  nobles:   P pd"
    assert get_modifiers_from_class(
        create_class(Artisans, "111111")) == "artisans: SFPDpd"
    assert get_modifiers_from_class(
        create_class(Peasants, "000000")) == "peasants:       "
    assert get_modifiers_from_class(
        create_class(Others, "101010")) == "  others: S P p "
    assert get_modifiers_from_class(
        create_class(Peasants, "010101")) == "peasants:  F D d"


def test_state():
    def check_state(arg: str) -> None:
        with capture_standard_output() as stdout:
            state(["state", arg], Interface())
            assert stdout.getvalue() != ""

    with raises(InvalidArgumentError):
        state(["state"], Interface())

    with raises(InvalidArgumentError):
        state(["state", "population", "2"], Interface())

    with raises(InvalidArgumentError):
        state(["state", "p"], Interface())

    with raises(InvalidArgumentError):
        state(["state", "military", "abc"], Interface())

    arguments = {
        "population", "resources", "prices", "total_resources",
        "modifiers", "government", "employment", "happiness", "military"
    }
    for arg in arguments:
        end = randint(2, len(arg))
        check_state(arg[:end])

    check_state("h")
    check_state("g")
    check_state("e")


def test_delete_save():
    rmtree_calls: list[str] = []

    def fake_rmtree(path: str) -> None:
        rmtree_calls.append(path)

    isdir_calls: list[Any] = []
    isdir_result: bool = False

    def fake_isdir(path: str) -> bool:
        isdir_calls.append(path)
        return isdir_result

    # Guarding against this test removing files
    with replace(shutil, "rmtree", fake_rmtree), \
         replace(os.path, "isdir", fake_isdir):
        with raises(InvalidArgumentError):
            delete_save(["delete"], None)

        with raises(InvalidArgumentError):
            delete_save(["delete", "abc", "def"], None)

        with raises(InvalidArgumentError):
            delete_save(["delete"], None)

        with capture_standard_output() as stdout:
            delete_save(["delete", "starting"], None)
            assert stdout.getvalue() != ""

        assert isdir_calls == []

        with capture_standard_output() as stdout:
            delete_save(["delete", "abc"], None)
            assert isdir_calls == ["saves/abc"]
            assert stdout.getvalue() != ""

        isdir_result = True
        with capture_standard_output() as stdout, \
                set_standard_input('0') as stdin:
            delete_save(["delete", "abcd"], None)
            assert isdir_calls == ["saves/abc", "saves/abcd"]
            assert stdout.getvalue() != ""
            assert stdin.tell() == 1

        with capture_standard_output() as stdout, \
                set_standard_input('ab\ncd\n0\nh\n') as stdin:
            delete_save(["delete", "abcde"], None)
            assert isdir_calls == ["saves/abc", "saves/abcd",
                                   "saves/abcde"]
            assert stdout.getvalue() != ""
            assert stdin.tell() == 8

        assert rmtree_calls == []
        with capture_standard_output() as stdout, \
                set_standard_input('2\n1') as stdin:
            delete_save(["delete", "test"], None)
            assert isdir_calls == ["saves/abc", "saves/abcd",
                                   "saves/abcde", "saves/test"]
            assert stdout.getvalue() != ""
            assert stdin.tell() == 3
            assert rmtree_calls == ["saves/test"]


def test_exit_game():
    with capture_standard_output() as stdout, \
         set_standard_input("0") as stdin:
        exit_game(None, None)
        assert stdout.getvalue() != ""
        assert stdin.tell() == 1

    with capture_standard_output() as stdout, \
         set_standard_input("ab\n0\ncd\n") as stdin:
        exit_game(None, None)
        assert stdout.getvalue() != ""
        assert stdin.tell() == 5

    with capture_standard_output() as stdout, \
         set_standard_input("ab\n1\ncd\n") as stdin:
        with raises(ShutDownCommand):
            exit_game(None, None)
        assert stdout.getvalue() != ""
        assert stdin.tell() == 5
