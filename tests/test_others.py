from ..sources.auxiliaries.constants import (
    EMPTY_RESOURCES,
    FOOD_CONSUMPTION,
    INBUILT_RESOURCES,
    OPTIMAL_RESOURCES,
    RESOURCES,
    WOOD_CONSUMPTION
)
from ..sources.state.state_data import State_Data
from ..sources.state.social_classes.others import Others
from ..sources.auxiliaries.arithmetic_dict import Arithmetic_Dict
from pytest import approx


def test_constructor():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    others = Others(state, 80, resources)

    assert others.parent == state

    assert others.employable

    assert others.population == 80

    assert others.resources["food"] == 100
    assert others.resources["wood"] == 200
    assert others.resources["iron"] == 0
    assert others.resources["stone"] == 0
    assert others.resources["tools"] == 100

    assert others.missing_resources["food"] == 0
    assert others.missing_resources["wood"] == 0


def test_default_constructor():
    state = State_Data()
    others = Others(state, 200)

    assert others.parent == state

    assert others.employable

    assert others.population == 200

    assert others.resources["food"] == 0
    assert others.resources["wood"] == 0
    assert others.resources["iron"] == 0
    assert others.resources["stone"] == 0
    assert others.resources["tools"] == 0

    assert others.missing_resources["food"] == 0
    assert others.missing_resources["wood"] == 0


def test_class_name():
    state = State_Data()
    others = Others(state, 200)
    assert others.class_name == "others"


def test_grow_population_1():
    state = State_Data()
    resources = {
        "food": 1000,
        "wood": 200,
        "iron": 0,
        "stone": 100,
        "tools": 100
    }
    others = Others(state, 80, resources)

    others.grow_population(0.25)
    assert others._new_population == 100
    assert others._new_resources == \
        others.resources - INBUILT_RESOURCES["others"] * 20


def test_grow_population_2():
    state = State_Data()
    resources = {
        "food": 1000,
        "wood": 20000,
        "iron": 0,
        "stone": 120,
        "tools": 1000
    }
    peasants = Others(state, 80, resources)

    peasants.grow_population(0.625)
    assert peasants._new_population == 130
    assert peasants._new_resources == \
        peasants.resources - INBUILT_RESOURCES["others"] * 50


def test_optimal_resources():
    state = State_Data()
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200
    }
    others = Others(state, 80, resources)
    opt_res = others.optimal_resources
    assert opt_res == OPTIMAL_RESOURCES["others"] * 80


def test_missing_resources_1():
    state = State_Data("July")
    resources = {
        "food": -200,
        "wood": 500,
        "stone": -20,
        "iron": 0,
        "tools": 1200
    }
    missing = {
        "food": 200,
        "wood": 0,
        "stone": 20,
        "iron": 0,
        "tools": 0
    }
    others = Others(state, 80, resources)
    assert others.missing_resources == missing


def test_missing_resources_2():
    state = State_Data("July")
    resources = {
        "food": 200,
        "wood": 500,
        "stone": 20,
        "iron": -1,
        "tools": -300
    }
    missing = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 1,
        "tools": 300
    }
    others = Others(state, 80)
    others.new_resources = resources
    assert others.missing_resources == missing


class Fake_Class:
    def __init__(self):
        self.class_name = "others"


def test_class_overpopulation_1():
    state = State_Data("July")
    resources = {
        "food": 200,
        "wood": -500,
        "stone": 0,
        "iron": 20,
        "tools": -40
    }

    others = Others(state, 80, resources)
    others2 = Fake_Class()
    others.lower_class = others2

    assert others.class_overpopulation == 0


def test_class_overpopulation_2():
    state = State_Data("July")
    resources = {
        "food": 200,
        "wood": 500,
        "stone": 20,
        "iron": 0,
        "tools": 100
    }

    others = Others(state, 80, resources)
    others2 = Fake_Class()
    others.lower_class = others2

    assert others.class_overpopulation == 0


def test_produce_january():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 0,
        "wood": 400,
        "stone": 0,
        "iron": 400,
        "tools": 1200
    })
    others = Others(state, 80, resources)

    final_res = resources.copy()

    others.produce()
    for res in RESOURCES:
        assert others._new_resources[res] == approx(final_res[res])


def test_produce_august():
    state = State_Data("August")
    resources = Arithmetic_Dict({
        "food": 0,
        "wood": 400,
        "stone": 0,
        "iron": 400,
        "tools": 1200
    })
    others = Others(state, 80, resources)

    final_res = resources.copy()

    others.produce()
    for res in RESOURCES:
        assert others._new_resources[res] == approx(final_res[res])


def test_consume():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    others = Others(state, 80, resources)
    others.consume()

    consumed = {
        "food": FOOD_CONSUMPTION * 80,
        "wood": WOOD_CONSUMPTION["January"] * 80
    }

    assert others._new_resources == others.resources - consumed
    assert others.missing_resources == EMPTY_RESOURCES
