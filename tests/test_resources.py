from math import inf

from ..sources.auxiliaries.enums import Resource
from ..sources.auxiliaries.resources import Resources


def test_constructor():
    res_dict = {
        Resource.food: 1,
        Resource.wood: 2,
        Resource.stone: 3,
        Resource.iron: 4,
        Resource.tools: 5,
        Resource.land: 6
    }
    res = Resources(res_dict)
    assert res.food == 1
    assert res.wood == 2
    assert res.stone == 3
    assert res.iron == 4
    assert res.tools == 5
    assert res.land == 6

    res_dict = {
        Resource.food: 1,
        Resource.stone: 3,
        Resource.land: 6
    }
    res = Resources(res_dict)
    assert res.food == 1
    assert res.wood == 0
    assert res.stone == 3
    assert res.iron == 0
    assert res.tools == 0
    assert res.land == 6

    res = Resources()
    assert res.food == 0
    assert res.wood == 0
    assert res.stone == 0
    assert res.iron == 0
    assert res.tools == 0
    assert res.land == 0


def test_setters():
    res = Resources()
    res.food = 2
    assert res.food == 2
    assert res.wood == 0
    assert res.stone == 0
    assert res.iron == 0
    assert res.tools == 0
    assert res.land == 0

    res.wood = 5
    assert res.food == 2
    assert res.wood == 5
    assert res.stone == 0
    assert res.iron == 0
    assert res.tools == 0
    assert res.land == 0

    res.stone = 8
    assert res.food == 2
    assert res.wood == 5
    assert res.stone == 8
    assert res.iron == 0
    assert res.tools == 0
    assert res.land == 0

    res.iron = 11.1
    assert res.food == 2
    assert res.wood == 5
    assert res.stone == 8
    assert res.iron == 11.1
    assert res.tools == 0
    assert res.land == 0

    res.tools -= 3.4
    assert res.food == 2
    assert res.wood == 5
    assert res.stone == 8
    assert res.iron == 11.1
    assert res.tools == -3.4
    assert res.land == 0

    res.land += 3.34
    assert res.food == 2
    assert res.wood == 5
    assert res.stone == 8
    assert res.iron == 11.1
    assert res.tools == -3.4
    assert res.land == 3.34


def test_dict_get():
    res = Resources()
    assert res[Resource.food] == 0
    assert res[Resource.wood] == 0
    assert res[Resource.stone] == 0
    assert res[Resource.iron] == 0
    assert res[Resource.tools] == 0
    assert res[Resource.land] == 0


def test_dict_set():
    res = Resources()
    res[Resource.food] = 2
    assert res.food == 2
    assert res.wood == 0
    assert res.stone == 0
    assert res.iron == 0
    assert res.tools == 0
    assert res.land == 0

    res[Resource.wood] = 5
    assert res.food == 2
    assert res.wood == 5
    assert res.stone == 0
    assert res.iron == 0
    assert res.tools == 0
    assert res.land == 0

    res[Resource.stone] = 8
    assert res.food == 2
    assert res.wood == 5
    assert res.stone == 8
    assert res.iron == 0
    assert res.tools == 0
    assert res.land == 0

    res[Resource.iron] = 11.1
    assert res.food == 2
    assert res.wood == 5
    assert res.stone == 8
    assert res.iron == 11.1
    assert res.tools == 0
    assert res.land == 0

    res[Resource.tools] -= 3.4
    assert res.food == 2
    assert res.wood == 5
    assert res.stone == 8
    assert res.iron == 11.1
    assert res.tools == -3.4
    assert res.land == 0

    res[Resource.land] += 3.34
    assert res.food == 2
    assert res.wood == 5
    assert res.stone == 8
    assert res.iron == 11.1
    assert res.tools == -3.4
    assert res.land == 3.34


def test_dict_del():
    res_dict = {
        Resource.food: 1,
        Resource.wood: 2,
        Resource.stone: 3,
        Resource.iron: 4,
        Resource.tools: 5,
        Resource.land: 6
    }
    res = Resources(res_dict)

    del res[Resource.food]
    assert res.food == 0
    assert res.wood == 2
    assert res.stone == 3
    assert res.iron == 4
    assert res.tools == 5
    assert res.land == 6

    del res[Resource.wood]
    assert res.food == 0
    assert res.wood == 0
    assert res.stone == 3
    assert res.iron == 4
    assert res.tools == 5
    assert res.land == 6

    del res[Resource.stone]
    assert res.food == 0
    assert res.wood == 0
    assert res.stone == 0
    assert res.iron == 4
    assert res.tools == 5
    assert res.land == 6

    del res[Resource.iron]
    assert res.food == 0
    assert res.wood == 0
    assert res.stone == 0
    assert res.iron == 0
    assert res.tools == 5
    assert res.land == 6

    del res[Resource.tools]
    assert res.food == 0
    assert res.wood == 0
    assert res.stone == 0
    assert res.iron == 0
    assert res.tools == 0
    assert res.land == 6

    del res[Resource.land]
    assert res.food == 0
    assert res.wood == 0
    assert res.stone == 0
    assert res.iron == 0
    assert res.tools == 0
    assert res.land == 0


def test_inherited_arithmetic():
    a = Resources({
        Resource.food: 234,
        Resource.wood: 123,
        Resource.land: 10
    })
    b = Resources({
        Resource.food: 66,
        Resource.wood: 123,
        Resource.stone: 100
    })
    assert a + b == {
        Resource.food: 300,
        Resource.wood: 246,
        Resource.stone: 100,
        Resource.land: 10
    }
    assert a - b == {
        Resource.food: 168,
        Resource.stone: -100,
        Resource.land: 10
    }
    assert a * b == {
        Resource.food: 234 * 66,
        Resource.wood: 123 ** 2
    }
    assert a / b == {
        Resource.food: 234 / 66,
        Resource.wood: 1,
        Resource.land: inf
    }
    assert a // b == {
        Resource.food: 234 // 66,
        Resource.wood: 1,
        Resource.land: inf
    }
    assert a < b
    assert a < 11
    assert not a < 0


def test_worth():
    a = Resources({
        Resource.food: 234,
        Resource.wood: 123,
        Resource.land: 10,
        Resource.stone: 2
    })
    b = {
        Resource.food: 2,
        Resource.wood: 3,
        Resource.stone: 3,
        Resource.iron: 4,
        Resource.tools: 45,
        Resource.land: 0.5
    }
    assert a.worth(b) == sum((a * b).values())
    assert Resources(b).worth(a) == sum((a * b).values())


def test_to_raw_dict():
    a = Resources({
        Resource.food: 234,
        Resource.wood: 123,
        Resource.land: 10,
        Resource.stone: 2
    })
    a_raw = a.to_raw_dict()
    assert isinstance(a_raw, dict)
    assert a_raw == {
        "food": 234,
        "wood": 123,
        "stone": 2,
        "iron": 0,
        "tools": 0,
        "land": 10
    }
