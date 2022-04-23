from ..sources.auxiliaries.constants import (
    DEFAULT_PRICES,
    EMPTY_RESOURCES,
    FOOD_CONSUMPTION,
    FOOD_PRODUCTION,
    INBUILT_RESOURCES,
    OPTIMAL_RESOURCES,
    PEASANT_TOOL_USAGE,
    RESOURCES,
    WOOD_CONSUMPTION,
    WOOD_PRODUCTION
)
from ..sources.state.state_data import State_Data
from ..sources.state.social_classes.peasants import Peasants
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
    peasants = Peasants(state, 80, resources)

    assert peasants.parent == state

    assert not peasants.employable

    assert peasants.population == 80

    assert peasants.resources["food"] == 100
    assert peasants.resources["wood"] == 200
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 100

    assert peasants.missing_resources["food"] == 0
    assert peasants.missing_resources["wood"] == 0


def test_default_constructor():
    state = State_Data()
    peasants = Peasants(state, 200)

    assert peasants.parent == state

    assert not peasants.employable

    assert peasants.population == 200

    assert peasants.resources["food"] == 0
    assert peasants.resources["wood"] == 0
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 0

    assert peasants.missing_resources["food"] == 0
    assert peasants.missing_resources["wood"] == 0


def test_class_name():
    state = State_Data()
    peasants = Peasants(state, 200)
    assert peasants.class_name == "peasants"


def test_grow_population_1():
    state = State_Data()
    resources = {
        "food": 1000,
        "wood": 200,
        "iron": 0,
        "stone": 100,
        "tools": 100
    }
    peasants = Peasants(state, 80, resources)

    peasants.grow_population(0.25)
    assert peasants._new_population == 100
    assert peasants._new_resources == \
        peasants.resources - INBUILT_RESOURCES["peasants"] * 20


def test_grow_population_2():
    state = State_Data()
    resources = {
        "food": 1000,
        "wood": 20000,
        "iron": 0,
        "stone": 120,
        "tools": 1000
    }
    peasants = Peasants(state, 80, resources)

    peasants.grow_population(0.625)
    assert peasants._new_population == 130
    assert peasants._new_resources == \
        peasants.resources - INBUILT_RESOURCES["peasants"] * 50


def test_optimal_resources():
    state = State_Data()
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200
    }
    peasants = Peasants(state, 80, resources)
    opt_res = peasants.optimal_resources
    assert opt_res == OPTIMAL_RESOURCES["peasants"] * 80


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
    peasants = Peasants(state, 80, resources)
    assert peasants.missing_resources == missing


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
    peasants = Peasants(state, 80)
    peasants.new_resources = resources
    assert peasants.missing_resources == missing


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
    missing_wood = 500
    missing_tools = 40

    peasants = Peasants(state, 80, resources)
    others = Fake_Class()
    peasants.lower_class = others

    inbuilt_wood = INBUILT_RESOURCES["peasants"]["wood"] - \
        INBUILT_RESOURCES["others"]["wood"]
    inbuilt_tools = INBUILT_RESOURCES["peasants"]["tools"] - \
        INBUILT_RESOURCES["others"]["tools"]

    overpop = max(missing_wood / inbuilt_wood, missing_tools / inbuilt_tools)

    assert peasants.class_overpopulation == overpop


def test_class_overpopulation_2():
    state = State_Data("July")
    resources = {
        "food": 200,
        "wood": -50,
        "stone": 0,
        "iron": 20,
        "tools": -400
    }
    missing_wood = 50
    missing_tools = 400

    peasants = Peasants(state, 80, resources)
    others = Fake_Class()
    peasants.lower_class = others

    inbuilt_wood = INBUILT_RESOURCES["peasants"]["wood"] - \
        INBUILT_RESOURCES["others"]["wood"]
    inbuilt_tools = INBUILT_RESOURCES["peasants"]["tools"] - \
        INBUILT_RESOURCES["others"]["tools"]

    overpop = max(missing_wood / inbuilt_wood, missing_tools / inbuilt_tools)

    assert peasants.class_overpopulation == overpop


def test_class_overpopulation_3():
    state = State_Data("July")
    resources = {
        "food": 200,
        "wood": 500,
        "stone": 20,
        "iron": 0,
        "tools": 100
    }

    peasants = Peasants(state, 80, resources)
    others = Fake_Class()
    peasants.lower_class = others

    assert peasants.class_overpopulation == 0


def test_produce_january():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 0,
        "wood": 400,
        "stone": 0,
        "iron": 400,
        "tools": 1200
    })
    peasants = Peasants(state, 80, resources)

    final_res = resources.copy()
    final_res += {
        "food": FOOD_PRODUCTION["January"] * 40,
        "wood": WOOD_PRODUCTION * 40,
        "tools": -PEASANT_TOOL_USAGE * 80
    }

    peasants.produce()
    for res in RESOURCES:
        assert peasants._new_resources[res] == approx(final_res[res])


def test_produce_august():
    state = State_Data("August")
    resources = Arithmetic_Dict({
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    })
    peasants = Peasants(state, 100, resources)

    final_res = {
        "food": FOOD_PRODUCTION["August"] * 50,
        "wood": WOOD_PRODUCTION * 50,
        "stone": 0,
        "iron": 0,
        "tools": -PEASANT_TOOL_USAGE * 100
    }

    peasants.produce()
    for res in RESOURCES:
        assert peasants._new_resources[res] == approx(final_res[res])


def test_produce_different_prices():
    prices = DEFAULT_PRICES.copy()
    prices["food"] *= 2
    prices["wood"] /= 2

    state = State_Data("August")
    state.prices = prices
    resources = Arithmetic_Dict({
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    })
    peasants = Peasants(state, 100, resources)

    final_res = {
        "food": FOOD_PRODUCTION["August"] * 80,
        "wood": WOOD_PRODUCTION * 20,
        "stone": 0,
        "iron": 0,
        "tools": -PEASANT_TOOL_USAGE * 100
    }

    peasants.produce()
    for res in RESOURCES:
        assert peasants._new_resources[res] == approx(final_res[res])


def test_consume():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    peasants = Peasants(state, 80, resources)
    peasants.consume()

    consumed = {
        "food": FOOD_CONSUMPTION * 80,
        "wood": WOOD_CONSUMPTION["January"] * 80
    }

    assert peasants._new_resources == peasants.resources - consumed
    assert peasants.missing_resources == EMPTY_RESOURCES
