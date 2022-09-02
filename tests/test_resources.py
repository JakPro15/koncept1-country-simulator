from ..sources.auxiliaries.resources import Resources
from pytest import raises


def test_constructor():
    res_dict = {
        "food": 1,
        "wood": 2,
        "stone": 3,
        "iron": 4,
        "tools": 5,
        "land": 6
    }
    res = Resources(res_dict)
    assert res.food == 1
    assert res.wood == 2
    assert res.stone == 3
    assert res.iron == 4
    assert res.tools == 5
    assert res.land == 6

    res_dict = {
        "food": 1,
        "stone": 3,
        "land": 6
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
    assert res.food == 2.0
    assert res.wood == 0
    assert res.stone == 0
    assert res.iron == 0
    assert res.tools == 0
    assert res.land == 0

    res.wood = 5
    assert res.food == 2.0
    assert res.wood == 5.0
    assert res.stone == 0
    assert res.iron == 0
    assert res.tools == 0
    assert res.land == 0

    res.stone = 8
    assert res.food == 2.0
    assert res.wood == 5.0
    assert res.stone == 8.0
    assert res.iron == 0
    assert res.tools == 0
    assert res.land == 0

    res.iron = 11.1
    assert res.food == 2.0
    assert res.wood == 5.0
    assert res.stone == 8.0
    assert res.iron == 11.1
    assert res.tools == 0
    assert res.land == 0

    res.tools -= 3.4
    assert res.food == 2.0
    assert res.wood == 5.0
    assert res.stone == 8.0
    assert res.iron == 11.1
    assert res.tools == -3.4
    assert res.land == 0

    res.land += 3.34
    assert res.food == 2.0
    assert res.wood == 5.0
    assert res.stone == 8.0
    assert res.iron == 11.1
    assert res.tools == -3.4
    assert res.land == 3.34


def test_dict_get():
    res = Resources()
    assert res["food"] == 0.0
    assert res["wood"] == 0.0
    assert res["stone"] == 0.0
    assert res["iron"] == 0.0
    assert res["tools"] == 0.0
    assert res["land"] == 0.0

    with raises(KeyError):
        res["yeet"]
    with raises(KeyError):
        res["abc"]


def test_dict_set():
    res = Resources()
    res["food"] = 2
    assert res.food == 2.0
    assert res.wood == 0
    assert res.stone == 0
    assert res.iron == 0
    assert res.tools == 0
    assert res.land == 0

    res["wood"] = 5
    assert res.food == 2.0
    assert res.wood == 5.0
    assert res.stone == 0
    assert res.iron == 0
    assert res.tools == 0
    assert res.land == 0

    res["stone"] = 8
    assert res.food == 2.0
    assert res.wood == 5.0
    assert res.stone == 8.0
    assert res.iron == 0
    assert res.tools == 0
    assert res.land == 0

    res["iron"] = 11.1
    assert res.food == 2.0
    assert res.wood == 5.0
    assert res.stone == 8.0
    assert res.iron == 11.1
    assert res.tools == 0
    assert res.land == 0

    res["tools"] -= 3.4
    assert res.food == 2.0
    assert res.wood == 5.0
    assert res.stone == 8.0
    assert res.iron == 11.1
    assert res.tools == -3.4
    assert res.land == 0

    res["land"] += 3.34
    assert res.food == 2.0
    assert res.wood == 5.0
    assert res.stone == 8.0
    assert res.iron == 11.1
    assert res.tools == -3.4
    assert res.land == 3.34

    with raises(KeyError):
        res["abc"] = 2
    with raises(KeyError):
        res["test"] = -1.2


def test_dict_del():
    res_dict = {
        "food": 1,
        "wood": 2,
        "stone": 3,
        "iron": 4,
        "tools": 5,
        "land": 6
    }
    res = Resources(res_dict)

    del res["food"]
    assert res.food == 0
    assert res.wood == 2
    assert res.stone == 3
    assert res.iron == 4
    assert res.tools == 5
    assert res.land == 6

    del res["wood"]
    assert res.food == 0
    assert res.wood == 0
    assert res.stone == 3
    assert res.iron == 4
    assert res.tools == 5
    assert res.land == 6

    del res["stone"]
    assert res.food == 0
    assert res.wood == 0
    assert res.stone == 0
    assert res.iron == 4
    assert res.tools == 5
    assert res.land == 6

    del res["iron"]
    assert res.food == 0
    assert res.wood == 0
    assert res.stone == 0
    assert res.iron == 0
    assert res.tools == 5
    assert res.land == 6

    del res["tools"]
    assert res.food == 0
    assert res.wood == 0
    assert res.stone == 0
    assert res.iron == 0
    assert res.tools == 0
    assert res.land == 6

    del res["land"]
    assert res.food == 0
    assert res.wood == 0
    assert res.stone == 0
    assert res.iron == 0
    assert res.tools == 0
    assert res.land == 0

    with raises(KeyError):
        del res["abc"]
    with raises(KeyError):
        del res["test"]
