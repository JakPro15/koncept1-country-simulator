from typing import Any
from ..sources.auxiliaries.constants import (KNIGHT_FIGHTING_STRENGTH,
                                             KNIGHT_FOOD_CONSUMPTION)
from ..sources.auxiliaries.enums import Soldier
from ..sources.auxiliaries.soldiers import Soldiers


def test_constructor():
    sol_dict = {
        Soldier.knights: 1,
        Soldier.footmen: 2
    }
    sol = Soldiers(sol_dict)
    assert sol.knights == 1
    assert sol.footmen == 2

    sol_dict = {
        Soldier.footmen: 3
    }
    sol = Soldiers(sol_dict)
    assert sol.knights == 0
    assert sol.footmen == 3

    sol = Soldiers()
    assert sol.knights == 0
    assert sol.footmen == 0


def test_setters():
    sol = Soldiers()
    sol.knights = 2
    assert sol.knights == 2
    assert sol.footmen == 0

    sol.footmen = 5
    assert sol.knights == 2
    assert sol.footmen == 5


def test_deleters():
    sol_dict = {
        Soldier.knights: 1,
        Soldier.footmen: 2
    }
    sol = Soldiers(sol_dict)

    del sol.knights
    assert sol.knights == 0
    assert sol.footmen == 2

    del sol.footmen
    assert sol.knights == 0
    assert sol.footmen == 0


def test_dict_get():
    sol = Soldiers()
    assert sol[Soldier.knights] == 0
    assert sol[Soldier.footmen] == 0


def test_dict_set():
    sol = Soldiers()
    sol[Soldier.knights] = 2
    assert sol.knights == 2
    assert sol.footmen == 0

    sol[Soldier.footmen] = 6
    assert sol.knights == 2
    assert sol.footmen == 6


def test_dict_del():
    sol_dict = {
        Soldier.knights: 1,
        Soldier.footmen: 2
    }
    sol = Soldiers(sol_dict)

    del sol[Soldier.knights]
    assert sol.knights == 0
    assert sol.footmen == 2

    del sol[Soldier.footmen]
    assert sol.knights == 0
    assert sol.footmen == 0


def test_inherited_arithmetic():
    a = Soldiers({
        Soldier.knights: 234
    })
    b = Soldiers({
        Soldier.knights: 66,
        Soldier.footmen: 123
    })
    assert a + b == {
        Soldier.knights: 300,
        Soldier.footmen: 123
    }
    assert a - b == {
        Soldier.knights: 168,
        Soldier.footmen: -123
    }
    assert a * b == {
        Soldier.knights: 234 * 66
    }
    assert a / b == {
        Soldier.knights: 234 / 66
    }
    assert a // b == {
        Soldier.knights: 234 // 66
    }
    assert a < b
    assert b < a
    assert b < 67
    assert not b < 66


def test_strength():
    a = Soldiers({
        Soldier.knights: 234
    })
    assert a.strength == 234 * KNIGHT_FIGHTING_STRENGTH

    b = Soldiers({
        Soldier.knights: 66,
        Soldier.footmen: 123
    })
    assert b.strength == 66 * KNIGHT_FIGHTING_STRENGTH + 123


def test_number():
    a = Soldiers({
        Soldier.knights: 234
    })
    assert a.number == 234

    b = Soldiers({
        Soldier.knights: 66,
        Soldier.footmen: 123
    })
    assert b.number == 66 + 123


def test_food_consumption():
    a = Soldiers({
        Soldier.knights: 234
    })
    assert a.food_consumption == 234 * KNIGHT_FOOD_CONSUMPTION

    b = Soldiers({
        Soldier.knights: 66,
        Soldier.footmen: 123
    })
    assert b.food_consumption == 66 * KNIGHT_FOOD_CONSUMPTION + 123


def test_to_raw_dict():
    a = Soldiers({
        Soldier.knights: 234,
        Soldier.footmen: 123
    })
    a_raw = a.to_raw_dict()
    assert isinstance(a_raw, dict)
    assert a_raw == {
        "knights": 234,
        "footmen": 123
    }


def test_from_raw_dict_strings():
    a_raw: dict[str, float] = {
        "knights": 234,
        "footmen": 123,
        "abc": 10
    }
    a = Soldiers({
        Soldier.knights: 234,
        Soldier.footmen: 123
    })
    a = Soldiers.from_raw_dict(a_raw)
    assert isinstance(a, Soldiers)
    assert a == {
        Soldier.knights: 234,
        Soldier.footmen: 123
    }


def test_from_raw_dict_any():
    a_raw: dict[Any, float] = {
        "knights": 234.5,
        Soldier.footmen: 123,
        "abc": 10,
        "ąbć": 10.1,
        2345: 5432
    }
    a = Soldiers({
        Soldier.knights: 234.5,
        Soldier.footmen: 123
    })
    a = Soldiers.from_raw_dict(a_raw)
    assert isinstance(a, Soldiers)
    assert a == {
        Soldier.knights: 234.5,
        Soldier.footmen: 123
    }
