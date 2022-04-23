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


def test_population_1():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    })
    others = Others(state, 80, resources)
    others.new_population += 20
    assert others.resources == resources
    assert others.population == 80
    assert others.new_resources == resources - INBUILT_RESOURCES["others"] * 20
    assert others.new_population == 100


def test_population_2():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    })
    others = Others(state, 80, resources)
    others.new_population -= 20
    assert others.resources == resources
    assert others.population == 80
    assert others.new_resources == resources + INBUILT_RESOURCES["others"] * 20
    assert others.new_population == 60


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
    others = Others(state, 80, resources1)
    others.new_resources = resources2
    assert others.resources == resources1
    assert others.new_resources == resources2


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


def test_to_dict():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    })
    others = Others(state, 80, resources)
    others.new_population += 20

    dicted = others.to_dict()
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
    others = Others.from_dict(state, dicted)

    assert others.parent == state
    assert others.population == 80
    assert others.resources == resources
    assert others.new_population == 80
    assert others.new_resources == resources


def test_handle_empty_class_emptying():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    })
    others = Others(state, 0.3, resources)

    # This is normally done by State_Data when adding classes
    others.is_temp = False
    others.temp = {"population": 0, "resources": EMPTY_RESOURCES.copy()}

    others.handle_empty_class()
    assert others.population == 0
    assert others.resources == EMPTY_RESOURCES
    assert others.is_temp
    assert others.temp["population"] == 0.3
    assert others.temp["resources"] == resources


def test_handle_empty_class_unemptying():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    })
    others = Others(state, 0, EMPTY_RESOURCES)

    others.is_temp = True
    others.temp = {"population": 0.4, "resources": resources.copy()}
    others._new_population = 0.2

    others.handle_empty_class()
    assert others.population == approx(0.6)
    assert others.resources == resources
    assert not others.is_temp
    assert others.temp["population"] == 0
    assert others.temp["resources"] == EMPTY_RESOURCES


def test_handle_empty_class_adding_to_temp():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    })
    others = Others(state, 0, EMPTY_RESOURCES)

    others.is_temp = True
    others.temp = {"population": 0.2, "resources": resources.copy()}
    others._new_population = 0.2
    others._new_resources = resources.copy()

    others.handle_empty_class()
    assert others.population == 0
    assert others.resources == EMPTY_RESOURCES
    assert others.is_temp
    assert others.temp["population"] == approx(0.4)
    assert others.temp["resources"] == resources * 2


def test_handle_negative_resources():
    state = State_Data()
    others = Others(state, 5)

    others._new_resources = Arithmetic_Dict({
        "food": 100,
        "wood": -100,
        "stone": -0.0001,
        "iron": -0.00099999,
        "tools": 0.0001
    })

    others.handle_negative_resources()
    assert others.new_resources == {
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
    new_res = resources - INBUILT_RESOURCES["others"] * 20
    others = Others(state, 80, resources)
    others.new_population += 20
    others.flush()

    assert others.resources == new_res
    assert others.population == 100
    assert others.new_resources == new_res
    assert others.new_population == 100


def test_flush_exception():
    state = State_Data()
    others = Others(state, 80)
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": -200,
        "iron": 0,
        "stone": 100,
        "tools": 100
    })
    others.new_resources = resources
    with raises(AssertionError):
        others.flush()
