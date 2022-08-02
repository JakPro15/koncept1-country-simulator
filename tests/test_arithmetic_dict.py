from ..sources.auxiliaries.arithmetic_dict import Arithmetic_Dict
from math import inf
from pytest import approx


def test_addition():
    resources1 = Arithmetic_Dict({
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources2 = Arithmetic_Dict({
        "food": 5,
        "wood": 4,
        "stone": 3,
        "iron": 1,
        "tools": 2
    })
    resources3 = resources1 + resources2
    assert resources3 == {
        "food": 5,
        "wood": 5,
        "stone": 5,
        "iron": 4,
        "tools": 6
    }


def test_assignment_addition():
    resources1 = Arithmetic_Dict({
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources2 = Arithmetic_Dict({
        "food": 5,
        "wood": 4,
        "stone": 3,
        "iron": 1,
        "tools": 2
    })
    resources1 += resources2
    assert resources1 == {
        "food": 5,
        "wood": 5,
        "stone": 5,
        "iron": 4,
        "tools": 6
    }


def test_subtraction():
    resources1 = Arithmetic_Dict({
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources2 = Arithmetic_Dict({
        "food": 5,
        "wood": 4,
        "stone": 3,
        "iron": 1,
        "tools": 2
    })
    resources3 = resources1 - resources2
    assert resources3 == {
        "food": -5,
        "wood": -3,
        "stone": -1,
        "iron": 2,
        "tools": 2
    }


def test_assignment_subtraction():
    resources1 = Arithmetic_Dict({
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources2 = Arithmetic_Dict({
        "food": 5,
        "wood": 4,
        "stone": 3,
        "iron": 1,
        "tools": 2
    })
    resources1 -= resources2
    assert resources1 == {
        "food": -5,
        "wood": -3,
        "stone": -1,
        "iron": 2,
        "tools": 2
    }


def test_multiplication_by_dict():
    resources1 = Arithmetic_Dict({
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources2 = Arithmetic_Dict({
        "food": inf,
        "wood": 4,
        "stone": 3,
        "iron": 1,
        "tools": 2
    })
    resources3 = resources1 * resources2
    assert resources3 == {
        "food": 0,
        "wood": 4,
        "stone": 6,
        "iron": 3,
        "tools": 8
    }


def test_assignment_multiplication_by_dict():
    resources1 = Arithmetic_Dict({
        "wood": 1,
        "stone": 2,
        "iron": inf,
        "tools": 4
    })
    resources2 = Arithmetic_Dict({
        "food": 5,
        "wood": 4,
        "stone": 3,
        "tools": 2
    })
    resources1 *= resources2
    assert resources1 == {
        "food": 0,
        "wood": 4,
        "stone": 6,
        "iron": 0,
        "tools": 8
    }


def test_multiplication_by_factor():
    resources1 = Arithmetic_Dict({
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources3 = resources1 * 4
    assert resources3 == {
        "wood": 4,
        "stone": 8,
        "iron": 12,
        "tools": 16
    }


def test_multiplication_by_inf():
    resources1 = Arithmetic_Dict({
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources3 = resources1 * inf
    assert resources3 == {
        "wood": inf,
        "stone": inf,
        "iron": inf,
        "tools": inf
    }


def test_assignment_multiplication_by_factor():
    resources1 = Arithmetic_Dict({
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources1 *= 4
    assert resources1 == {
        "wood": 4,
        "stone": 8,
        "iron": 12,
        "tools": 16
    }


def test_assignment_multiplication_by_zero():
    resources1 = Arithmetic_Dict({
        "food": -inf,
        "wood": 1,
        "stone": inf,
        "iron": 3,
        "tools": 4
    })
    resources1 *= 0
    assert resources1 == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }


def test_division_by_dict():
    resources1 = Arithmetic_Dict({
        "food": 2,
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources2 = Arithmetic_Dict({
        "food": inf,
        "wood": 4,
        "iron": 1,
        "tools": 2
    })
    resources3 = resources1 / resources2
    assert resources3 == {
        "food": 0,
        "wood": approx(0.25),
        "stone": inf,
        "iron": 3,
        "tools": 2
    }


def test_assignment_division_by_dict():
    resources1 = Arithmetic_Dict({
        "food": 2,
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources2 = Arithmetic_Dict({
        "food": inf,
        "wood": 4,
        "stone": 3,
        "tools": 2
    })
    resources1 /= resources2
    assert resources1 == {
        "food": 0,
        "wood": approx(0.25),
        "stone": approx(0.667, abs=0.001),
        "iron": inf,
        "tools": 2
    }


def test_division_by_factor():
    resources1 = Arithmetic_Dict({
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources3 = resources1 / 4
    assert resources3 == {
        "wood": approx(0.25),
        "stone": approx(0.5),
        "iron": approx(0.75),
        "tools": 1
    }


def test_division_by_zero():
    resources1 = Arithmetic_Dict({
        "food": 0,
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources3 = resources1 / 0
    assert resources3 == {
        "food": 0,
        "wood": inf,
        "stone": inf,
        "iron": inf,
        "tools": inf
    }


def test_assignment_division_by_factor():
    resources1 = Arithmetic_Dict({
        "food": 0,
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources1 /= 4
    assert resources1 == {
        "food": 0,
        "wood": approx(0.25),
        "stone": approx(0.5),
        "iron": approx(0.75),
        "tools": 1
    }


def test_assignment_division_by_zero():
    resources1 = Arithmetic_Dict({
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources1 /= 0
    assert resources1 == {
        "wood": inf,
        "stone": inf,
        "iron": inf,
        "tools": inf
    }


def test_floor_division_by_dict():
    resources1 = Arithmetic_Dict({
        "food": 2,
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources2 = Arithmetic_Dict({
        "food": inf,
        "wood": 4,
        "iron": 1,
        "tools": 2
    })
    resources3 = resources1 // resources2
    assert resources3 == {
        "food": 0,
        "wood": 0,
        "stone": inf,
        "iron": 3,
        "tools": 2
    }


def test_assignment_floor_division_by_dict():
    resources1 = Arithmetic_Dict({
        "food": 2,
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources2 = Arithmetic_Dict({
        "food": inf,
        "wood": 4,
        "stone": 3,
        "iron": 0,
        "tools": 2
    })
    resources1 //= resources2
    assert resources1 == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": inf,
        "tools": 2
    }


def test_floor_division_by_factor():
    resources1 = Arithmetic_Dict({
        "food": 0,
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources3 = resources1 // 4
    assert resources3 == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1
    }


def test_floor_division_by_zero():
    resources1 = Arithmetic_Dict({
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources3 = resources1 // 0
    assert resources3 == {
        "wood": inf,
        "stone": inf,
        "iron": inf,
        "tools": inf
    }


def test_assignment_floor_division_by_factor():
    resources1 = Arithmetic_Dict({
        "food": 0,
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources1 //= 4
    assert resources1 == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1
    }


def test_assignment_floor_division_by_zero():
    resources1 = Arithmetic_Dict({
        "food": 0,
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources1 //= 0
    assert resources1 == {
        "food": 0,
        "wood": inf,
        "stone": inf,
        "iron": inf,
        "tools": inf
    }


def test_lesser_than_operator_on_dicts_both_ways():
    resources1 = Arithmetic_Dict({
        "food": 0,
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources2 = Arithmetic_Dict({
        "food": 4,
        "wood": 3,
        "stone": 2,
        "iron": 1,
        "tools": 0
    })
    assert resources1 < resources2
    assert resources2 < resources1

    resources2 = dict(resources2)
    assert resources1 < resources2


def test_lesser_than_operator_on_dicts_strictly_lesser():
    resources1 = Arithmetic_Dict({
        "food": 0,
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources2 = Arithmetic_Dict({
        "food": 1,
        "wood": 2,
        "stone": 3,
        "iron": 4,
        "tools": 5
    })
    assert resources1 < resources2
    assert not resources2 < resources1

    resources2 = dict(resources2)
    assert resources1 < resources2


def test_lesser_than_operator_on_dicts_equals():
    resources1 = Arithmetic_Dict({
        "food": 0,
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    assert not resources1 < resources1

    resources2 = dict(resources1)
    assert not resources1 < resources2


def test_lesser_than_operator_with_number_various_values():
    resources1 = Arithmetic_Dict({
        "food": 0,
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    assert resources1 < 4
    assert resources1 < 1
    assert not resources1 < 0
    assert not resources1 < -1.5


def test_lesser_than_operator_with_number_equals():
    resources1 = Arithmetic_Dict({
        "stone": 4,
        "iron": 4,
        "tools": 4
    })
    assert not resources1 < 4
    assert resources1 < 4.5
    assert not resources1 < 3.5


def test_copy():
    resources1 = Arithmetic_Dict({
        "food": 0,
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    })
    resources2 = resources1.copy()
    assert isinstance(resources2, Arithmetic_Dict)
    assert resources2 == {
        "food": 0,
        "wood": 1,
        "stone": 2,
        "iron": 3,
        "tools": 4
    }


def test_int():
    res = Arithmetic_Dict({
        "a": 2.3,
        "b": 5.0,
        "c": -1.2
    })
    assert res.int() == {
        "a": 2,
        "b": 5,
        "c": -1
    }

    res = Arithmetic_Dict({
        "a": 2.333333,
        "b": 5,
        "c": "23",
        "d": Arithmetic_Dict({
            "e": -3.01,
            "f": 0.0
        })
    })
    assert res.int() == {
        "a": 2,
        "b": 5,
        "c": 23,
        "d": {
            "e": -3,
            "f": 0
        }
    }


def test_float():
    res = Arithmetic_Dict({
        "a": 2.3,
        "b": 5,
        "c": -1.2
    })
    res = res.float()
    assert res == {
        "a": 2.3,
        "b": 5.0,
        "c": -1.2
    }
    assert isinstance(res["a"], float)
    assert isinstance(res["b"], float)
    assert isinstance(res["c"], float)

    res = Arithmetic_Dict({
        "a": 2.333333,
        "b": 5,
        "c": "2.3",
        "d": Arithmetic_Dict({
            "e": -3.01,
            "f": 0,
            "g": "-1"
        })
    })
    res = res.float()
    assert res == {
        "a": 2.333333,
        "b": 5,
        "c": 2.3,
        "d": {
            "e": -3.01,
            "f": 0.0,
            "g": -1.0
        }
    }
    assert isinstance(res["a"], float)
    assert isinstance(res["b"], float)
    assert isinstance(res["c"], float)
    assert isinstance(res["d"]["e"], float)
    assert isinstance(res["d"]["f"], float)
    assert isinstance(res["d"]["g"], float)


def test_round():
    resources1 = Arithmetic_Dict({
        "food": 0,
        "wood": 1.1111,
        "stone": 2,
        "iron": 37.3456,
        "tools": 14.2
    })

    resources2 = round(resources1)
    assert isinstance(resources2, Arithmetic_Dict)
    assert resources2 == {
        "food": 0,
        "wood": 1,
        "stone": 2,
        "iron": 37,
        "tools": 14
    }

    resources2 = round(resources1, 2)
    assert isinstance(resources2, Arithmetic_Dict)
    assert resources2 == {
        "food": 0,
        "wood": 1.11,
        "stone": 2,
        "iron": 37.35,
        "tools": 14.2
    }

    resources2 = round(resources1, -1)
    assert isinstance(resources2, Arithmetic_Dict)
    assert resources2 == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 40,
        "tools": 10
    }
