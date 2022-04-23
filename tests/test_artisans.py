from ..sources.auxiliaries.constants import (
    ARTISAN_IRON_USAGE,
    ARTISAN_TOOL_USAGE,
    ARTISAN_WOOD_USAGE,
    DEFAULT_PRICES,
    EMPTY_RESOURCES,
    FOOD_CONSUMPTION,
    INBUILT_RESOURCES,
    OPTIMAL_RESOURCES,
    RESOURCES,
    TOOLS_PRODUCTION,
    WOOD_CONSUMPTION
)
from ..sources.state.state_data import State_Data
from ..sources.state.social_classes.artisans import Artisans
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


def test_class_name():
    state = State_Data()
    artisans = Artisans(state, 200)
    assert artisans.class_name == "artisans"


def test_grow_population():
    state = State_Data()
    resources = {
        "food": 1000,
        "wood": 200,
        "iron": 0,
        "stone": 100,
        "tools": 100
    }
    artisans = Artisans(state, 80, resources)

    artisans.grow_population(0.25)
    assert artisans._new_population == 100
    assert artisans._new_resources == \
        artisans.resources - INBUILT_RESOURCES["artisans"] * 20


def test_grow_population_not_enough_resources():
    state = State_Data()
    resources = {
        "food": 1000,
        "wood": 20000,
        "iron": 0,
        "stone": 120,
        "tools": 1000
    }
    artisans = Artisans(state, 80, resources)

    artisans.grow_population(0.625)
    assert artisans._new_population == 130
    assert artisans._new_resources == \
        artisans.resources - INBUILT_RESOURCES["artisans"] * 50


def test_optimal_resources():
    state = Fake_State_Data(100)
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200
    }
    artisans = Artisans(state, 80, resources)
    opt_res = artisans.optimal_resources
    assert opt_res == OPTIMAL_RESOURCES["artisans"] * 80


def test_missing_resources_1():
    state = Fake_State_Data(500, "July")
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
    artisans = Artisans(state, 80, resources)
    assert artisans.missing_resources == missing


def test_missing_resources_2():
    state = Fake_State_Data(500, "July")
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
    artisans = Artisans(state, 80)
    artisans.new_resources = resources
    assert artisans.missing_resources == missing


class Fake_Class:
    def __init__(self):
        self.class_name = "others"


def test_class_overpopulation_1():
    state = Fake_State_Data(500, "July")
    resources = {
        "food": 200,
        "wood": -500,
        "stone": 0,
        "iron": -20,
        "tools": 1200
    }
    missing_wood = 500
    missing_iron = 20

    artisans = Artisans(state, 80, resources)
    others = Fake_Class()
    artisans.lower_class = others

    inbuilt_wood = INBUILT_RESOURCES["artisans"]["wood"] - \
        INBUILT_RESOURCES["others"]["wood"]
    inbuilt_iron = INBUILT_RESOURCES["artisans"]["iron"] - \
        INBUILT_RESOURCES["others"]["iron"]

    overpop = max(missing_wood / inbuilt_wood, missing_iron / inbuilt_iron)

    assert artisans.class_overpopulation == overpop


def test_class_overpopulation_2():
    state = Fake_State_Data(500, "July")
    resources = {
        "food": 200,
        "wood": -50,
        "stone": 0,
        "iron": -200,
        "tools": 1200
    }
    missing_wood = 50
    missing_iron = 200

    artisans = Artisans(state, 80, resources)
    others = Fake_Class()
    artisans.lower_class = others

    inbuilt_wood = INBUILT_RESOURCES["artisans"]["wood"] - \
        INBUILT_RESOURCES["others"]["wood"]
    inbuilt_iron = INBUILT_RESOURCES["artisans"]["iron"] - \
        INBUILT_RESOURCES["others"]["iron"]

    overpop = max(missing_wood / inbuilt_wood, missing_iron / inbuilt_iron)

    assert artisans.class_overpopulation == overpop


def test_class_overpopulation_3():
    state = Fake_State_Data(500, "July")
    resources = {
        "food": 200,
        "wood": 500,
        "stone": 20,
        "iron": 0,
        "tools": 100
    }

    artisans = Artisans(state, 80, resources)
    others = Fake_Class()
    artisans.lower_class = others

    assert artisans.class_overpopulation == 0


class Fake_State_Data(State_Data):
    def __init__(
        self, available_employees, month="January", prices=DEFAULT_PRICES
    ):
        self._month = month
        self.available_employees = available_employees
        self.payments = Arithmetic_Dict({
            "food": 0,
            "wood": 0,
            "iron": 0,
            "stone": 0,
            "tools": 0
        })
        self.prices = Arithmetic_Dict(prices.copy())

    def get_available_employees(self):
        return self.available_employees


def test_produce_1():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 0,
        "wood": 400,
        "stone": 0,
        "iron": 400,
        "tools": 1200
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
        "tools": 0
    })
    artisans = Artisans(state, 100, resources)

    final_res = {
        "food": 0,
        "wood": -ARTISAN_WOOD_USAGE * 100,
        "stone": 0,
        "iron": -ARTISAN_IRON_USAGE * 100,
        "tools": (TOOLS_PRODUCTION - ARTISAN_TOOL_USAGE) * 100
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
        "tools": 100
    }
    artisans = Artisans(state, 80, resources)
    artisans.consume()

    consumed = {
        "food": FOOD_CONSUMPTION * 80,
        "wood": WOOD_CONSUMPTION["January"] * 80
    }

    assert artisans._new_resources == artisans.resources - consumed
    assert artisans.missing_resources == EMPTY_RESOURCES
