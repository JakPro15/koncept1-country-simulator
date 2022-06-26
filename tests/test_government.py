from ..sources.state.government import Government
from ..sources.state.state_data import State_Data
from ..sources.auxiliaries.arithmetic_dict import Arithmetic_Dict
from pytest import raises


def test_constructor():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100,
        "land": 0
    })
    govt = Government(state, resources, resources / 2)

    assert govt.parent == state

    assert govt.resources["food"] == 100
    assert govt.resources["wood"] == 200
    assert govt.resources["iron"] == 0
    assert govt.resources["stone"] == 0
    assert govt.resources["tools"] == 100
    assert govt.resources["land"] == 0

    assert govt._new_resources["food"] == 100
    assert govt._new_resources["wood"] == 200
    assert govt._new_resources["iron"] == 0
    assert govt._new_resources["stone"] == 0
    assert govt._new_resources["tools"] == 100
    assert govt._new_resources["land"] == 0

    assert govt._secure_resources["food"] == 0
    assert govt._secure_resources["wood"] == 0
    assert govt._secure_resources["iron"] == 0
    assert govt._secure_resources["stone"] == 0
    assert govt._secure_resources["tools"] == 0
    assert govt._secure_resources["land"] == 0

    assert govt.optimal_resources["food"] == 50
    assert govt.optimal_resources["wood"] == 100
    assert govt.optimal_resources["iron"] == 0
    assert govt.optimal_resources["stone"] == 0
    assert govt.optimal_resources["tools"] == 50
    assert govt.optimal_resources["land"] == 0


def test_default_constructor():
    state = State_Data()
    govt = Government(state)

    assert govt.parent == state

    assert govt.resources["food"] == 0
    assert govt.resources["wood"] == 0
    assert govt.resources["iron"] == 0
    assert govt.resources["stone"] == 0
    assert govt.resources["tools"] == 0
    assert govt.resources["land"] == 0

    assert govt._new_resources["food"] == 0
    assert govt._new_resources["wood"] == 0
    assert govt._new_resources["iron"] == 0
    assert govt._new_resources["stone"] == 0
    assert govt._new_resources["tools"] == 0
    assert govt._new_resources["land"] == 0

    assert govt._secure_resources["food"] == 0
    assert govt._secure_resources["wood"] == 0
    assert govt._secure_resources["iron"] == 0
    assert govt._secure_resources["stone"] == 0
    assert govt._secure_resources["tools"] == 0
    assert govt._secure_resources["land"] == 0

    assert govt.optimal_resources["food"] == 0
    assert govt.optimal_resources["wood"] == 0
    assert govt.optimal_resources["iron"] == 0
    assert govt.optimal_resources["stone"] == 0
    assert govt.optimal_resources["tools"] == 0
    assert govt.optimal_resources["land"] == 0


def test_resources():
    state = State_Data()
    resources1 = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100,
        "land": 0
    })
    resources2 = Arithmetic_Dict({
        "food": 150,
        "wood": 10,
        "iron": 11,
        "stone": 12,
        "tools": 100,
        "land": 0
    })
    govt = Government(state, resources1)
    govt.new_resources = resources2
    assert govt.resources == resources1
    assert govt.new_resources == resources2


def test_secure_resources():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100,
        "land": 0
    })
    govt = Government(state, resources, resources / 2)
    secure_res = {
        "food": 1000,
        "wood": 2000,
        "iron": 3000,
        "stone": 4000,
        "tools": 5000,
        "land": 6000
    }
    govt.secure_resources = secure_res
    assert govt.real_resources == {
        "food": 1100,
        "wood": 2200,
        "iron": 3000,
        "stone": 4000,
        "tools": 5100,
        "land": 6000
    }
    assert govt.secure_resources == {
        "food": 1000,
        "wood": 2000,
        "iron": 3000,
        "stone": 4000,
        "tools": 5000,
        "land": 6000
    }
    govt.new_resources = {
        "food": -100,
        "wood": 0,
        "iron": 300,
        "stone": 400,
        "tools": -5000,
        "land": -5000
    }
    govt.flush()
    assert govt.resources == {
        "food": 0,
        "wood": 0,
        "iron": 300,
        "stone": 400,
        "tools": 0,
        "land": 0
    }
    assert govt.secure_resources == {
        "food": 900,
        "wood": 2000,
        "iron": 3000,
        "stone": 4000,
        "tools": 0,
        "land": 1000
    }
    assert govt.real_resources == {
        "food": 900,
        "wood": 2000,
        "iron": 3300,
        "stone": 4400,
        "tools": 0,
        "land": 1000
    }


def test_to_dict():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100,
        "land": 0
    }
    optimal_resources = {
        "food": 10,
        "wood": 20,
        "iron": 0,
        "stone": 0,
        "tools": 10,
        "land": 0
    }
    govt = Government(state, resources, optimal_resources)

    dicted = govt.to_dict()
    assert dicted["resources"] == resources
    assert dicted["optimal_resources"] == optimal_resources


def test_from_dict():
    state = State_Data()
    dicted = {
        "resources": {
            "food": 100,
            "wood": 200,
            "iron": 0,
            "stone": 0,
            "tools": 100,
            "land": 0
        },
        "optimal_resources": {
            "food": 10,
            "wood": 20,
            "iron": 30,
            "stone": 40,
            "tools": 100,
            "land": 50
        },
    }
    govt = Government.from_dict(state, dicted)

    assert govt.parent == state
    assert govt.resources == dicted["resources"]
    assert govt.new_resources == dicted["resources"]
    assert govt.optimal_resources == dicted["optimal_resources"]


def test_handle_negative_resources():
    state = State_Data()
    govt = Government(state)

    govt._new_resources = Arithmetic_Dict({
        "food": 100,
        "wood": -100,
        "stone": -0.0001,
        "iron": -0.00099999,
        "tools": 0.0001,
        "land": 0
    })

    govt.handle_negative_resources()
    assert govt.new_resources == {
        "food": 100,
        "wood": -100,
        "stone": 0,
        "iron": 0,
        "tools": 0.0001,
        "land": 0
    }


def test_flush_typical():
    state = State_Data()
    resources1 = {
        "food": 1000,
        "wood": 2000,
        "iron": 0,
        "stone": 1000,
        "tools": 1000,
        "land": 10000
    }
    resources2 = {
        "food": 10000,
        "wood": 20000,
        "iron": 10,
        "stone": 10000,
        "tools": 10000,
        "land": 100000
    }
    govt = Government(state, resources1)
    govt._new_resources = resources2

    assert govt.resources == resources1
    assert govt.new_resources == resources2

    govt.flush()

    assert govt.resources == resources2
    assert govt.new_resources == resources2


def test_flush_exception():
    state = State_Data()
    govt = Government(state)
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": -200,
        "iron": 0,
        "stone": 100,
        "tools": 100,
        "land": 0
    })
    govt.new_resources = resources
    with raises(Exception):
        govt.flush()
