from ..classes.state_data import (
    State_Data, Nobles, Artisans, Peasants, Others
)


def test_constructor():
    state = State_Data("August")
    assert state.month == "August"
    assert state.payments == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }
    assert state.prices == {
        "food": 0,
        "wood": 0,
        "iron": 0,
        "stone": 0,
        "tools": 0
    }


def test_default_constructor():
    state = State_Data()
    assert state.month == "January"
    assert state.payments == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }
    assert state.prices == {
        "food": 0,
        "wood": 0,
        "iron": 0,
        "stone": 0,
        "tools": 0
    }


def test_advance_month():
    state = State_Data("August")
    assert state.month == "August"
    state._advance_month()
    assert state.month == "September"
    state._advance_month()
    assert state.month == "October"
    state._advance_month()
    assert state.month == "November"
    state._advance_month()
    assert state.month == "December"
    state._advance_month()
    assert state.month == "January"


def test_create_market():
    state = State_Data()
    classes = [1, 2, 3]
    state._classes = [1, 2, 3]
    state._create_market()
    assert state._market.classes == classes


def test_from_dict():
    state = State_Data()
    data = {
        "month": "June",
        "classes": {
            "nobles": {
                "population": 20,
                "resources": {
                    "food": 21,
                    "wood": 22,
                    "stone": 23,
                    "iron": 24,
                    "tools": 25
                },
                "land": {
                    "fields": 26,
                    "woods": 27,
                    "stone_mines": 28,
                    "iron_mines": 29
                }
            },
            "artisans": {
                "population": 30,
                "resources": {
                    "food": 31,
                    "wood": 32,
                    "stone": 33,
                    "iron": 34,
                    "tools": 35
                },
                "land": {
                    "fields": 0,
                    "woods": 0,
                    "stone_mines": 0,
                    "iron_mines": 0
                }
            },
            "peasants": {
                "population": 40,
                "resources": {
                    "food": 41,
                    "wood": 42,
                    "stone": 43,
                    "iron": 44,
                    "tools": 45
                },
                "land": {
                    "fields": 46,
                    "woods": 47,
                    "stone_mines": 0,
                    "iron_mines": 0
                }
            },
            "others": {
                "population": 50,
                "resources": {
                    "food": 51,
                    "wood": 52,
                    "stone": 53,
                    "iron": 54,
                    "tools": 55
                },
                "land": {
                    "fields": 0,
                    "woods": 0,
                    "stone_mines": 0,
                    "iron_mines": 0
                }
            }
        },
        "prices": {
            "food": 0.1,
            "wood": 0.2,
            "stone": 0.3,
            "iron": 1.4,
            "tools": 0.5
        }
    }
    state.from_dict(data)
    assert state.month == "June"

    assert isinstance(state.classes[0], Nobles)
    assert state.classes[0].population == 20
    assert state.classes[0].resources == {
        "food": 21,
        "wood": 22,
        "stone": 23,
        "iron": 24,
        "tools": 25
    }
    assert state.classes[0].land == {
        "fields": 26,
        "woods": 27,
        "stone_mines": 28,
        "iron_mines": 29
    }

    assert isinstance(state.classes[1], Artisans)
    assert state.classes[1].population == 30
    assert state.classes[1].resources == {
        "food": 31,
        "wood": 32,
        "stone": 33,
        "iron": 34,
        "tools": 35
    }
    assert state.classes[1].land == {
        "fields": 0,
        "woods": 0,
        "stone_mines": 0,
        "iron_mines": 0
    }

    assert isinstance(state.classes[2], Peasants)
    assert state.classes[2].population == 40
    assert state.classes[2].resources == {
        "food": 41,
        "wood": 42,
        "stone": 43,
        "iron": 44,
        "tools": 45
    }
    assert state.classes[2].land == {
        "fields": 46,
        "woods": 47,
        "stone_mines": 0,
        "iron_mines": 0
    }

    assert isinstance(state.classes[3], Others)
    assert state.classes[3].population == 50
    assert state.classes[3].resources == {
        "food": 51,
        "wood": 52,
        "stone": 53,
        "iron": 54,
        "tools": 55
    }
    assert state.classes[3].land == {
        "fields": 0,
        "woods": 0,
        "stone_mines": 0,
        "iron_mines": 0
    }


def test_to_dict():
    state = State_Data("June")
    data = {
        "month": "June",
        "classes": {
            "nobles": {
                "population": 20,
                "resources": {
                    "food": 21,
                    "wood": 22,
                    "stone": 23,
                    "iron": 24,
                    "tools": 25
                },
                "land": {
                    "fields": 26,
                    "woods": 27,
                    "stone_mines": 28,
                    "iron_mines": 29
                }
            },
            "artisans": {
                "population": 30,
                "resources": {
                    "food": 31,
                    "wood": 32,
                    "stone": 33,
                    "iron": 34,
                    "tools": 35
                },
                "land": {
                    "fields": 0,
                    "woods": 0,
                    "stone_mines": 0,
                    "iron_mines": 0
                }
            },
            "peasants": {
                "population": 40,
                "resources": {
                    "food": 41,
                    "wood": 42,
                    "stone": 43,
                    "iron": 44,
                    "tools": 45
                },
                "land": {
                    "fields": 46,
                    "woods": 47,
                    "stone_mines": 0,
                    "iron_mines": 0
                }
            },
            "others": {
                "population": 50,
                "resources": {
                    "food": 51,
                    "wood": 52,
                    "stone": 53,
                    "iron": 54,
                    "tools": 55
                },
                "land": {
                    "fields": 0,
                    "woods": 0,
                    "stone_mines": 0,
                    "iron_mines": 0
                }
            }
        },
        "prices": {
            "food": 0.1,
            "wood": 0.2,
            "stone": 0.3,
            "iron": 1.4,
            "tools": 0.5
        }
    }

    population = 20
    resources = {
        "food": 21,
        "wood": 22,
        "stone": 23,
        "iron": 24,
        "tools": 25
    }
    land = {
        "fields": 26,
        "woods": 27,
        "stone_mines": 28,
        "iron_mines": 29
    }
    nobles = Nobles(state, population, resources, land)

    population = 30
    resources = {
        "food": 31,
        "wood": 32,
        "stone": 33,
        "iron": 34,
        "tools": 35
    }
    land = {
        "fields": 0,
        "woods": 0,
        "stone_mines": 0,
        "iron_mines": 0
    }
    artisans = Artisans(state, population, resources, land)

    population = 40
    resources = {
        "food": 41,
        "wood": 42,
        "stone": 43,
        "iron": 44,
        "tools": 45
    }
    land = {
        "fields": 46,
        "woods": 47,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, population, resources, land)

    population = 50
    resources = {
        "food": 51,
        "wood": 52,
        "stone": 53,
        "iron": 54,
        "tools": 55
    }
    land = {
        "fields": 0,
        "woods": 0,
        "stone_mines": 0,
        "iron_mines": 0
    }
    others = Others(state, population, resources, land)

    classes = [nobles, artisans, peasants, others]
    state.classes = classes

    state.prices = {
        "food": 0.1,
        "wood": 0.2,
        "stone": 0.3,
        "iron": 1.4,
        "tools": 0.5
    }

    assert state.to_dict() == data
