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
from pytest import approx, raises


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

    assert not peasants.is_temp
    assert peasants.temp["population"] == 0
    assert peasants.temp["resources"] == EMPTY_RESOURCES
    assert not peasants.starving
    assert not peasants.freezing


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

    assert not peasants.is_temp
    assert peasants.temp["population"] == 0
    assert peasants.temp["resources"] == EMPTY_RESOURCES
    assert not peasants.starving
    assert not peasants.freezing


def test_class_name():
    state = State_Data()
    peasants = Peasants(state, 200)
    assert peasants.class_name == "peasants"


def test_population_1():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    })
    peasants = Peasants(state, 80, resources)
    peasants.new_population += 20
    assert peasants.resources == resources
    assert peasants.population == 80
    assert peasants.new_resources == \
        resources - INBUILT_RESOURCES["peasants"] * 20
    assert peasants.new_population == 100


def test_population_2():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    })
    peasants = Peasants(state, 80, resources)
    peasants.new_population -= 20
    assert peasants.resources == resources
    assert peasants.population == 80
    assert peasants.new_resources == \
        resources + INBUILT_RESOURCES["peasants"] * 20
    assert peasants.new_population == 60


def test_resources():
    state = State_Data()
    resources1 = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    })
    resources2 = Arithmetic_Dict({
        "food": 150,
        "wood": 10,
        "iron": 11,
        "stone": 12,
        "tools": 100
    })
    peasants = Peasants(state, 80, resources1)
    peasants.new_resources = resources2
    assert peasants.resources == resources1
    assert peasants.new_resources == resources2


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


def test_to_dict():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    })
    peasants = Peasants(state, 80, resources)
    peasants.new_population += 20

    dicted = peasants.to_dict()
    assert dicted["population"] == 80
    assert dicted["resources"] == resources


def test_from_dict():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    })
    dicted = {
        "population": 80,
        "resources": dict(resources.copy())
    }
    peasants = Peasants.from_dict(state, dicted)

    assert peasants.parent == state
    assert peasants.population == 80
    assert peasants.resources == resources
    assert peasants.new_population == 80
    assert peasants.new_resources == resources


def test_handle_empty_class_emptying():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    })
    peasants = Peasants(state, 0.3, resources)

    # This is normally done by State_Data when adding classes
    peasants.is_temp = False
    peasants.temp = {"population": 0, "resources": EMPTY_RESOURCES.copy()}

    peasants.handle_empty_class()
    assert peasants.population == 0
    assert peasants.resources == EMPTY_RESOURCES
    assert peasants.is_temp
    assert peasants.temp["population"] == 0.3
    assert peasants.temp["resources"] == resources


def test_handle_empty_class_unemptying():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    })
    peasants = Peasants(state, 0, EMPTY_RESOURCES)

    peasants.is_temp = True
    peasants.temp = {"population": 0.4, "resources": resources.copy()}
    peasants._new_population = 0.2

    peasants.handle_empty_class()
    assert peasants.population == approx(0.6)
    assert peasants.resources == resources
    assert not peasants.is_temp
    assert peasants.temp["population"] == 0
    assert peasants.temp["resources"] == EMPTY_RESOURCES


def test_handle_empty_class_adding_to_temp():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    })
    peasants = Peasants(state, 0, EMPTY_RESOURCES)

    peasants.is_temp = True
    peasants.temp = {"population": 0.2, "resources": resources.copy()}
    peasants._new_population = 0.2
    peasants._new_resources = resources.copy()

    peasants.handle_empty_class()
    assert peasants.population == 0
    assert peasants.resources == EMPTY_RESOURCES
    assert peasants.is_temp
    assert peasants.temp["population"] == approx(0.4)
    assert peasants.temp["resources"] == resources * 2


def test_handle_negative_resources():
    state = State_Data()
    peasants = Peasants(state, 5)

    peasants._new_resources = Arithmetic_Dict({
        "food": 100,
        "wood": -100,
        "stone": -0.0001,
        "iron": -0.00099999,
        "tools": 0.0001
    })

    peasants.handle_negative_resources()
    assert peasants.new_resources == {
        "food": 100,
        "wood": -100,
        "stone": 0,
        "iron": 0,
        "tools": 0.0001
    }


def test_flush_typical():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 100,
        "tools": 100
    })
    new_res = resources - INBUILT_RESOURCES["peasants"] * 20
    peasants = Peasants(state, 80, resources)
    peasants.new_population += 20
    peasants.flush()

    assert peasants.resources == new_res
    assert peasants.population == 100
    assert peasants.new_resources == new_res
    assert peasants.new_population == 100


def test_flush_exception():
    state = State_Data()
    peasants = Peasants(state, 80)
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": -200,
        "iron": 0,
        "stone": 100,
        "tools": 100
    })
    peasants.new_resources = resources
    with raises(AssertionError):
        peasants.flush()
