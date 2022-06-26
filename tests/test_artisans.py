from ..sources.auxiliaries.constants import (
    ARTISAN_IRON_USAGE,
    ARTISAN_TOOL_USAGE,
    ARTISAN_WOOD_USAGE,
    EMPTY_RESOURCES,
    FOOD_CONSUMPTION,
    INBUILT_RESOURCES,
    RESOURCES,
    TOOLS_PRODUCTION,
    WOOD_CONSUMPTION
)
from ..sources.state.state_data import State_Data
from ..sources.state.social_classes.artisans import Artisans
from ..sources.auxiliaries.arithmetic_dict import Arithmetic_Dict
from pytest import approx, raises


def test_constructor():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100,
        "land": 0
    }
    artisans = Artisans(state, 80, resources)

    assert artisans.parent == state

    assert not artisans.employable

    assert artisans.population == 80

    assert artisans.resources["food"] == 100
    assert artisans.resources["wood"] == 200
    assert artisans.resources["iron"] == 0
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == 100

    assert artisans.missing_resources["food"] == 0
    assert artisans.missing_resources["wood"] == 0

    assert not artisans.is_temp
    assert artisans.temp["population"] == 0
    assert artisans.temp["resources"] == EMPTY_RESOURCES
    assert not artisans.starving
    assert not artisans.freezing


def test_default_constructor():
    state = State_Data()
    artisans = Artisans(state, 200)

    assert artisans.parent == state

    assert not artisans.employable

    assert artisans.population == 200

    assert artisans.resources["food"] == 0
    assert artisans.resources["wood"] == 0
    assert artisans.resources["iron"] == 0
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == 0

    assert artisans.missing_resources["food"] == 0
    assert artisans.missing_resources["wood"] == 0

    assert not artisans.is_temp
    assert artisans.temp["population"] == 0
    assert artisans.temp["resources"] == EMPTY_RESOURCES
    assert not artisans.starving
    assert not artisans.freezing


def test_class_name():
    state = State_Data()
    artisans = Artisans(state, 200)
    assert artisans.class_name == "artisans"


def test_population_1():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100,
        "land": 0
    })
    artisans = Artisans(state, 80, resources)
    artisans.new_population += 20
    assert artisans.resources == resources
    assert artisans.population == 80
    assert artisans.new_resources == \
        resources - INBUILT_RESOURCES["artisans"] * 20
    assert artisans.new_population == 100


def test_population_2():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100,
        "land": 0
    })
    artisans = Artisans(state, 80, resources)
    artisans.new_population -= 20
    assert artisans.resources == resources
    assert artisans.population == 80
    assert artisans.new_resources == \
        resources + INBUILT_RESOURCES["artisans"] * 20
    assert artisans.new_population == 60


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
    artisans = Artisans(state, 80, resources1)
    artisans.new_resources = resources2
    assert artisans.resources == resources1
    assert artisans.new_resources == resources2


def test_grow_population_1():
    state = State_Data()
    resources = {
        "food": 1000,
        "wood": 200,
        "iron": 0,
        "stone": 100,
        "tools": 100,
        "land": 0
    }
    artisans = Artisans(state, 80, resources)

    artisans.grow_population(0.25)
    assert artisans._new_population == 100
    assert artisans._new_resources == \
        artisans.resources - INBUILT_RESOURCES["artisans"] * 20


def test_grow_population_2():
    state = State_Data()
    resources = {
        "food": 1000,
        "wood": 20000,
        "iron": 0,
        "stone": 120,
        "tools": 1000,
        "land": 0
    }
    artisans = Artisans(state, 80, resources)

    artisans.grow_population(0.625)
    assert artisans._new_population == 130
    assert artisans._new_resources == \
        artisans.resources - INBUILT_RESOURCES["artisans"] * 50


def test_optimal_resources():
    state = State_Data()
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200,
        "land": 0
    }
    artisans = Artisans(state, 80, resources)
    opt_res = artisans.optimal_resources
    assert opt_res == state.sm.optimal_resources["artisans"] * 80


def test_missing_resources_1():
    state = State_Data("July")
    missing = {
        "food": 200,
        "wood": 0,
        "stone": 20,
        "iron": 0,
        "tools": 0,
        "land": 0
    }
    artisans = Artisans(state, 80)
    artisans.new_resources = {
        "food": -200,
        "wood": 500,
        "stone": -20,
        "iron": 0,
        "tools": 1200,
        "land": 0
    }
    assert artisans.missing_resources == missing


def test_missing_resources_2():
    state = State_Data("July")
    resources = {
        "food": 200,
        "wood": 500,
        "stone": 20,
        "iron": -1,
        "tools": -300,
        "land": 0
    }
    missing = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 1,
        "tools": 300,
        "land": 0
    }
    artisans = Artisans(state, 80)
    artisans.new_resources = resources
    assert artisans.missing_resources == missing


class Fake_Class:
    def __init__(self):
        self.class_name = "others"


def test_class_overpopulation_1():
    state = State_Data("July")
    resources = {
        "food": 200,
        "wood": -500,
        "stone": 0,
        "iron": -20,
        "tools": 1200,
        "land": 0
    }
    missing_wood = 500
    missing_iron = 20

    artisans = Artisans(state, 80)
    artisans.new_resources = resources
    others = Fake_Class()
    artisans.lower_class = others

    inbuilt_wood = INBUILT_RESOURCES["artisans"]["wood"] - \
        INBUILT_RESOURCES["others"]["wood"]
    inbuilt_iron = INBUILT_RESOURCES["artisans"]["iron"] - \
        INBUILT_RESOURCES["others"]["iron"]

    overpop = max(missing_wood / inbuilt_wood, missing_iron / inbuilt_iron)

    assert artisans.class_overpopulation == overpop


def test_class_overpopulation_2():
    state = State_Data("July")
    resources = {
        "food": 200,
        "wood": -50,
        "stone": 0,
        "iron": -200,
        "tools": 1200,
        "land": 0
    }
    missing_wood = 50
    missing_iron = 200

    artisans = Artisans(state, 80)
    artisans.new_resources = resources
    others = Fake_Class()
    artisans.lower_class = others

    inbuilt_wood = INBUILT_RESOURCES["artisans"]["wood"] - \
        INBUILT_RESOURCES["others"]["wood"]
    inbuilt_iron = INBUILT_RESOURCES["artisans"]["iron"] - \
        INBUILT_RESOURCES["others"]["iron"]

    overpop = max(missing_wood / inbuilt_wood, missing_iron / inbuilt_iron)

    assert artisans.class_overpopulation == overpop


def test_class_overpopulation_3():
    state = State_Data("July")
    resources = {
        "food": 200,
        "wood": 500,
        "stone": 20,
        "iron": 0,
        "tools": 100,
        "land": 0
    }

    artisans = Artisans(state, 80, resources)
    others = Fake_Class()
    artisans.lower_class = others

    assert artisans.class_overpopulation == 0


def test_real_resources():
    state = State_Data()
    resources1 = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100,
        "land": 0
    })
    resources2 = resources1 + INBUILT_RESOURCES["artisans"] * 80
    artisans = Artisans(state, 80, resources1)
    assert artisans.resources == resources1
    assert artisans.real_resources == resources2


def test_net_worth():
    state = State_Data()
    state.prices = {
        "food": 2,
        "wood": 3,
        "stone": 4,
        "iron": 5,
        "tools": 6,
        "land": 7
    }
    resources = {
        "food": 100000,
        "wood": 10000,
        "stone": 1000,
        "iron": 100,
        "tools": 10,
        "land": 1
    }
    inbuilt_worth = sum(
        (INBUILT_RESOURCES["artisans"] * state.prices * 20).values()
    )
    artisans = Artisans(state, 20, resources)
    assert artisans.net_worth == 234567 + inbuilt_worth


def test_produce_1():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 0,
        "wood": 400,
        "stone": 0,
        "iron": 400,
        "tools": 1200,
        "land": 0
    })
    artisans = Artisans(state, 80, resources)

    final_res = resources.copy()
    final_res += {
        "wood": -ARTISAN_WOOD_USAGE * 80,
        "iron": -ARTISAN_IRON_USAGE * 80,
        "tools": (TOOLS_PRODUCTION - ARTISAN_TOOL_USAGE) * 80
    }

    artisans.produce()
    for res in RESOURCES:
        assert artisans._new_resources[res] == approx(final_res[res])


def test_produce_2():
    state = State_Data("August")
    resources = Arithmetic_Dict({
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0,
        "land": 0
    })
    artisans = Artisans(state, 100, resources)

    final_res = {
        "food": 0,
        "wood": -ARTISAN_WOOD_USAGE * 100,
        "stone": 0,
        "iron": -ARTISAN_IRON_USAGE * 100,
        "tools": (TOOLS_PRODUCTION - ARTISAN_TOOL_USAGE) * 100,
        "land": 0
    }

    artisans.produce()
    for res in RESOURCES:
        assert artisans._new_resources[res] == approx(final_res[res])


def test_consume():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100,
        "land": 0
    }
    artisans = Artisans(state, 80, resources)
    artisans.consume()

    consumed = {
        "food": FOOD_CONSUMPTION * 80,
        "wood": WOOD_CONSUMPTION["January"] * 80
    }

    assert artisans._new_resources == artisans.resources - consumed
    assert artisans.missing_resources == EMPTY_RESOURCES


def test_to_dict():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100,
        "land": 0
    })
    artisans = Artisans(state, 80, resources)
    artisans.new_population += 20

    dicted = artisans.to_dict()
    assert dicted["population"] == 80
    assert dicted["resources"] == resources


def test_from_dict():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100,
        "land": 0
    })
    dicted = {
        "population": 80,
        "resources": dict(resources.copy())
    }
    artisans = Artisans.from_dict(state, dicted)

    assert artisans.parent == state
    assert artisans.population == 80
    assert artisans.resources == resources
    assert artisans.new_population == 80
    assert artisans.new_resources == resources


def test_handle_empty_class_emptying():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100,
        "land": 0
    })
    artisans = Artisans(state, 0.3, resources)

    # This is normally done by State_Data when adding classes
    artisans.is_temp = False
    artisans.temp = {"population": 0, "resources": EMPTY_RESOURCES.copy()}

    artisans.handle_empty_class()
    assert artisans.population == 0
    assert artisans.resources == EMPTY_RESOURCES
    assert artisans.is_temp
    assert artisans.temp["population"] == 0.3
    assert artisans.temp["resources"] == resources


def test_handle_empty_class_unemptying():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100,
        "land": 0
    })
    artisans = Artisans(state, 0, EMPTY_RESOURCES)

    artisans.is_temp = True
    artisans.temp = {"population": 0.4, "resources": resources.copy()}
    artisans._new_population = 0.2

    artisans.handle_empty_class()
    assert artisans.population == approx(0.6)
    assert artisans.resources == resources
    assert not artisans.is_temp
    assert artisans.temp["population"] == 0
    assert artisans.temp["resources"] == EMPTY_RESOURCES


def test_handle_empty_class_adding_to_temp():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100,
        "land": 0
    })
    artisans = Artisans(state, 0, EMPTY_RESOURCES)

    artisans.is_temp = True
    artisans.temp = {"population": 0.2, "resources": resources.copy()}
    artisans._new_population = 0.2
    artisans._new_resources = resources.copy()

    artisans.handle_empty_class()
    assert artisans.population == 0
    assert artisans.resources == EMPTY_RESOURCES
    assert artisans.is_temp
    assert artisans.temp["population"] == approx(0.4)
    assert artisans.temp["resources"] == resources * 2


def test_handle_negative_resources():
    state = State_Data()
    artisans = Artisans(state, 5)

    artisans._new_resources = Arithmetic_Dict({
        "food": 100,
        "wood": -100,
        "stone": -0.0001,
        "iron": -0.00099999,
        "tools": 0.0001,
        "land": 0
    })

    artisans.handle_negative_resources()
    assert artisans.new_resources == {
        "food": 100,
        "wood": -100,
        "stone": 0,
        "iron": 0,
        "tools": 0.0001,
        "land": 0
    }


def test_flush_typical():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 200,
        "iron": 100,
        "stone": 0,
        "tools": 100,
        "land": 0
    })
    new_res = resources - INBUILT_RESOURCES["artisans"] * 20
    artisans = Artisans(state, 80, resources)
    artisans.new_population += 20
    artisans.flush()

    assert artisans.resources == new_res
    assert artisans.population == 100
    assert artisans.new_resources == new_res
    assert artisans.new_population == 100


def test_flush_exception():
    state = State_Data()
    artisans = Artisans(state, 80)
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": -200,
        "iron": 0,
        "stone": 100,
        "tools": 100,
        "land": 0
    })
    artisans.new_resources = resources
    with raises(Exception):
        artisans.flush()
