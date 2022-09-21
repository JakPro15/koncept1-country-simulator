import builtins
from contextlib import contextmanager
from io import StringIO
import json
from typing import Any, Generator

from pytest import raises
from ..sources.auxiliaries.soldiers import Soldiers

from ..sources.abstract_interface.history import History
from ..sources.abstract_interface.interface import (Interface,
                                                    InvalidArgumentError,
                                                    NotEnoughClassPopulation,
                                                    NotEnoughClassResources,
                                                    NotEnoughGovtResources,
                                                    check_arg)
from ..sources.auxiliaries.constants import INBUILT_RESOURCES, RECRUITMENT_COST
from ..sources.auxiliaries.enums import Class_Name, Resource, Soldier
from ..sources.auxiliaries.resources import Resources
from ..sources.auxiliaries.testing import replace
from ..sources.state.state_data import State_Data


def test_check_arg():
    check_arg(True, "abc")
    try:
        check_arg(False, "abc")
    except InvalidArgumentError as e:
        assert str(e) == "abc"


def test_constructor_from_filename():
    loads: list[Any] = []

    def fake_load(self: Interface, *args: Any):
        loads.append(args)

    with replace(Interface, "load_data", fake_load):
        Interface("abcde")
        assert loads == [("abcde",)]
        Interface("hehe xd")
        assert loads == [("abcde",), ("hehe xd",)]


def test_constructor_from_state():
    state = State_Data.generate_empty_state()
    state.nobles.population = 30
    state.peasants.population = 40
    state.peasants.resources = Resources(10)
    state.government.soldiers = Soldiers(5)

    interface = Interface(state)
    assert interface.state is state
    assert interface.history.starting_state_dict == state.to_dict()
    assert interface.history.history_lines == []

    interface = Interface(state, History({}, ["next 2"]))
    assert interface.state is state
    assert interface.history.starting_state_dict == {}
    assert interface.history.history_lines == ["next 2"]


def test_load_data():
    state = State_Data.generate_empty_state()
    state.nobles.population = 30
    state.nobles.resources = Resources()
    state.peasants.population = 40
    state.peasants.resources = Resources(10)
    state.government.soldiers = Soldiers(5)

    opens: list[Any] = []
    state_data_dict = state.to_dict()

    @contextmanager
    def fake_open(filename: str, mode: str = 'r'
                  ) -> Generator[StringIO, None, None]:
        opens.append((filename, mode))
        result = StringIO()
        with replace(result, "read", result.getvalue):
            if "starting_state" in filename:
                json.dump(state_data_dict, result)
                yield result
            elif "history" in filename:
                result.write("next 2")
                yield result
            else:
                raise AssertionError

    with replace(builtins, "open", fake_open):
        interface = Interface()
        interface.load_data("hehe")

        assert interface.history.starting_state_dict == state_data_dict
        assert interface.history.history_lines == ["next 2"]
        state.execute_commands(["next 2"])
        assert interface.state.to_dict() == state.to_dict()

        assert opens == [
            ("saves/hehe/starting_state.json", "r"),
            ("saves/hehe/history.txt", "r")
        ]


def test_save_data():
    state = State_Data.generate_empty_state()
    state.nobles.population = 30
    state.nobles.resources = Resources()
    state.peasants.population = 40
    state.peasants.resources = Resources(10)
    state.government.soldiers = Soldiers(5)
    history = History(state.to_dict(), ["next 2"])

    opens: list[Any] = []
    starting_state = StringIO()
    history_lines = StringIO()

    @contextmanager
    def fake_open(filename: str, mode: str = 'r'
                  ) -> Generator[StringIO, None, None]:
        opens.append((filename, mode))
        if "starting_state" in filename:
            yield starting_state
        elif "history" in filename:
            yield history_lines
        else:
            raise AssertionError

    with replace(builtins, "open", fake_open):
        interface = Interface(state, history)
        interface.save_data("hehe")

        assert json.loads(starting_state.getvalue()) == state.to_dict()
        assert history_lines.getvalue().strip() == "next 2"

        assert opens == [
            ("saves/hehe/starting_state.json", "w"),
            ("saves/hehe/history.txt", "w")
        ]


def test_next_month_first():
    did_month = 0

    def fake_do_month(self: State_Data) -> None:
        nonlocal did_month
        did_month += 1

    with replace(State_Data, "do_month", fake_do_month):
        interface = Interface()
        interface.next_month()

        assert did_month == 1
        assert interface.fought is False
        assert interface.history.history_lines == ["next 1"]


def test_next_month_next() -> None:
    did_month = 0

    def fake_do_month(self: State_Data) -> None:
        nonlocal did_month
        did_month += 1

    with replace(State_Data, "do_month", fake_do_month):
        history = History({}, ["next 6"])

        interface = Interface(State_Data.generate_empty_state(), history)
        interface.fought = True

        interface.next_month()

        assert did_month == 1
        assert interface.fought is False
        assert interface.history.history_lines == ["next 7"]


def test_transfer():
    transfers: list[Any] = []

    def fake_do_transfer(self: State_Data, *args: Any) -> None:
        transfers.append(args)

    with replace(State_Data, "do_transfer", fake_do_transfer):
        state = State_Data.generate_empty_state()
        state.government.resources = Resources(300)
        state.nobles.population = 100
        state.nobles.resources = Resources(100)

        history = History({}, ["next 6"])

        interface = Interface(state, history)

        interface.transfer_resources(Class_Name.nobles, Resource.food, 100)
        with raises(NotEnoughGovtResources):
            interface.transfer_resources(Class_Name.nobles, Resource.food, 350)
        with raises(NotEnoughClassResources):
            interface.transfer_resources(
                Class_Name.nobles, Resource.food, -150
            )

        assert transfers == [(Class_Name.nobles, Resource.food, 100, True)]
        assert history.history_lines == [
            "next 6",
            "transfer nobles food 100"
        ]


def test_secure():
    secures: list[Any] = []

    def fake_do_secure(self: State_Data, *args: Any) -> None:
        secures.append(args)

    with replace(State_Data, "do_secure", fake_do_secure):
        state = State_Data.generate_empty_state()
        state.government.resources = Resources(300)
        state.government.secure_resources = Resources(100)

        history = History({}, ["next 6"])
        interface = Interface(state, history)

        interface.secure_resources(Resource.food, 100)
        with raises(NotEnoughGovtResources):
            interface.secure_resources(Resource.food, 350)
        with raises(NotEnoughGovtResources):
            interface.secure_resources(Resource.food, -150)

        assert secures == [(Resource.food, 100)]
        assert history.history_lines == [
            "next 6",
            "secure food 100"
        ]

        interface.secure_resources(Resource.iron, None)
        assert secures == [
            (Resource.food, 100),
            (Resource.iron, 300)
        ]
        assert history.history_lines == [
            "next 6",
            "secure food 100",
            "secure iron 300"
        ]


def test_optimal():
    optimals: list[Any] = []

    def fake_do_optimal(self: State_Data, *args: Any) -> None:
        optimals.append(args)

    with replace(State_Data, "do_optimal", fake_do_optimal):
        state = State_Data.generate_empty_state()
        history = History({}, ["next 6"])
        interface = Interface(state, history)

        interface.set_govt_optimal(Resource.food, 100)
        with raises(InvalidArgumentError):
            interface.set_govt_optimal(Resource.wood, -100)

        assert optimals == [(Resource.food, 100)]
        assert history.history_lines == [
            "next 6",
            "optimal food 100"
        ]

        interface.set_govt_optimal(Resource.iron, 50)
        assert optimals == [
            (Resource.food, 100),
            (Resource.iron, 50)
        ]
        assert history.history_lines == [
            "next 6",
            "optimal food 100",
            "optimal iron 50"
        ]

        interface.set_govt_optimal(Resource.land, 0)
        assert optimals == [
            (Resource.food, 100),
            (Resource.iron, 50),
            (Resource.land, 0)
        ]
        assert history.history_lines == [
            "next 6",
            "optimal food 100",
            "optimal iron 50",
            "optimal land 0"
        ]


def test_set_law():
    setlaws: list[Any] = []

    def fake_do_set_law(self: State_Data, *args: Any) -> None:
        setlaws.append(args)

    with replace(State_Data, "do_set_law", fake_do_set_law):
        state = State_Data.generate_empty_state()
        history = History({}, ["next 6"])
        interface = Interface(state, history)

        interface.set_law("tax_personal", "nobles", 100)
        with raises(InvalidArgumentError):
            interface.set_law("tax_property", "nobles", 2)
        with raises(InvalidArgumentError):
            interface.set_law("tax_income", "nobles", -0.1)
        with raises(InvalidArgumentError):
            interface.set_law("wage_minimum", None, 1.2)

        assert setlaws == [("tax_personal", "nobles", 100)]
        assert history.history_lines == [
            "next 6",
            "laws set tax_personal nobles 100"
        ]

        interface.set_law("wage_minimum", None, 0.99)
        assert setlaws == [
            ("tax_personal", "nobles", 100),
            ("wage_minimum", None, 0.99)
        ]
        assert history.history_lines == [
            "next 6",
            "laws set tax_personal nobles 100",
            "laws set wage_minimum None 0.99"
        ]

        interface.set_law("tax_income", "artisans", 0.01)
        assert setlaws == [
            ("tax_personal", "nobles", 100),
            ("wage_minimum", None, 0.99),
            ("tax_income", "artisans", 0.01)
        ]
        assert history.history_lines == [
            "next 6",
            "laws set tax_personal nobles 100",
            "laws set wage_minimum None 0.99",
            "laws set tax_income artisans 0.01"
        ]


def test_force_promotion():
    force_promotions: list[Any] = []

    def fake_do_force_promotion(self: State_Data, *args: Any) -> None:
        force_promotions.append(args)

    with replace(State_Data, "do_force_promotion", fake_do_force_promotion):
        state = State_Data.generate_empty_state()
        state.nobles.population = 50
        state.artisans.population = 50
        state.peasants.population = 60
        state.others.population = 200

        state.government.resources = \
            (INBUILT_RESOURCES[Class_Name.peasants] -
             INBUILT_RESOURCES[Class_Name.others]) * 100

        history = History({}, ["next 6"])
        interface = Interface(state, history)

        interface.force_promotion(Class_Name.peasants, 60)
        with raises(InvalidArgumentError):
            interface.force_promotion(Class_Name.peasants, -1)
        with raises(NotEnoughClassPopulation):
            interface.force_promotion(Class_Name.nobles, 61)
        with raises(NotEnoughGovtResources):
            interface.force_promotion(Class_Name.peasants, 101)

        assert force_promotions == [(Class_Name.peasants, 60)]
        assert history.history_lines == [
            "next 6",
            "promote peasants 60"
        ]

        state.government.resources = \
            (INBUILT_RESOURCES[Class_Name.nobles] -
             INBUILT_RESOURCES[Class_Name.peasants]) * 20

        interface.force_promotion(Class_Name.nobles, 20)
        with raises(NotEnoughGovtResources):
            interface.force_promotion(Class_Name.nobles, 21)

        assert force_promotions == [
            (Class_Name.peasants, 60),
            (Class_Name.nobles, 20)
        ]
        assert history.history_lines == [
            "next 6",
            "promote peasants 60",
            "promote nobles 20"
        ]

        state.government.resources = \
            (INBUILT_RESOURCES[Class_Name.artisans] -
             INBUILT_RESOURCES[Class_Name.others]) * 20

        interface.force_promotion(Class_Name.artisans, 20)
        with raises(NotEnoughGovtResources):
            interface.force_promotion(Class_Name.artisans, 21)

        assert force_promotions == [
            (Class_Name.peasants, 60),
            (Class_Name.nobles, 20),
            (Class_Name.artisans, 20)
        ]
        assert history.history_lines == [
            "next 6",
            "promote peasants 60",
            "promote nobles 20",
            "promote artisans 20"
        ]


def test_recruit():
    recruits: list[Any] = []

    def fake_do_recruit(self: State_Data, *args: Any) -> None:
        recruits.append(args)

    with replace(State_Data, "do_recruit", fake_do_recruit):
        state = State_Data.generate_empty_state()
        state.nobles.population = 300
        state.artisans.population = 50
        state.peasants.population = 60
        state.others.population = 200000
        state.government.resources = RECRUITMENT_COST[Soldier.knights] * 40

        history = History({}, ["next 6"])
        interface = Interface(state, history)

        interface.recruit(Class_Name.nobles, 30)
        with raises(InvalidArgumentError):
            interface.recruit(Class_Name.peasants, -1)
        with raises(NotEnoughClassPopulation):
            interface.recruit(Class_Name.peasants, 61)
        with raises(NotEnoughGovtResources):
            interface.recruit(Class_Name.nobles, 101)

        assert recruits == [(Class_Name.nobles, 30)]
        assert history.history_lines == [
            "next 6",
            "recruit nobles 30"
        ]

        interface.recruit(Class_Name.artisans, 40)
        with raises(NotEnoughGovtResources):
            interface.recruit(Class_Name.others, 21000)

        assert recruits == [
            (Class_Name.nobles, 30),
            (Class_Name.artisans, 40)
        ]
        assert history.history_lines == [
            "next 6",
            "recruit nobles 30",
            "recruit artisans 40"
        ]


def test_get_brigands():
    state = State_Data.generate_empty_state()
    state.brigands = 24
    state.brigands_strength = 0.7
    interface = Interface(state)

    brigands, strength = interface.get_brigands(True)
    assert brigands == 24
    assert strength == 0.7

    brigands, strength = interface.get_brigands(False)
    assert brigands == (20, 30)
    assert strength == (0.5, 1)

    state.brigands = 100
    state.brigands_strength = 1.999
    brigands, strength = interface.get_brigands(False)
    assert brigands == (100, 200)
    assert strength == (1.5, 2)

    state.brigands = 6
    state.brigands_strength = 2
    brigands, strength = interface.get_brigands(False)
    assert brigands == (0, 10)
    assert strength == (2, 2.5)

    state.brigands = 0
    state.brigands_strength = 1
    brigands, strength = interface.get_brigands(False)
    assert brigands == (0, 10)
    assert strength == (1, 1.5)


def test_fight():
    fights: list[Any] = []

    def fake_do_fight(self: State_Data, *args: Any) -> None:
        fights.append(args)

    with replace(State_Data, "do_fight", fake_do_fight):
        state = State_Data.generate_empty_state()
        state.government.soldiers = Soldiers(
            {Soldier.knights: 5, Soldier.footmen: 40}
        )

        history = History({}, ["next 6"])

        interface = Interface()
        interface.state = state
        interface.history = history

        interface.fight("plunder")

        random_enemies = fights[0][1]
        assert random_enemies > 10
        assert isinstance(random_enemies, int)

        assert fights == [("plunder", random_enemies)]
        assert history.history_lines == [
            "next 6",
            f"fight plunder {random_enemies}"
        ]

        interface.fight("crime")

        assert fights == [
            ("plunder", random_enemies),
            ("crime", None)
        ]
        assert history.history_lines == [
            "next 6",
            f"fight plunder {random_enemies}",
            "fight crime None"
        ]
