from ..sources.auxiliaries.constants import (
    DEFAULT_PRICES,
    EMPTY_RESOURCES,
    FOOD_CONSUMPTION,
    INBUILT_RESOURCES,
    WOOD_CONSUMPTION
)
from ..sources.state.state_data import State_Data, State_Modifiers
from ..sources.state.social_classes.nobles import Nobles
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
    nobles = Nobles(state, 80, resources)

    assert nobles.parent == state

    assert not nobles.employable

    assert nobles.population == 80

    assert nobles.resources["food"] == 100
    assert nobles.resources["wood"] == 200
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == 0
    assert nobles.resources["tools"] == 100
    assert nobles.resources["land"] == 0

    assert nobles.missing_resources["food"] == 0
    assert nobles.missing_resources["wood"] == 0

    assert not nobles.is_temp
    assert nobles.temp["population"] == 0
    assert nobles.temp["resources"] == EMPTY_RESOURCES
    assert not nobles.starving
    assert not nobles.freezing


def test_default_constructor():
    state = State_Data()
    nobles = Nobles(state, 200)

    assert nobles.parent == state

    assert not nobles.employable

    assert nobles.population == 200

    assert nobles.resources["food"] == 0
    assert nobles.resources["wood"] == 0
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == 0
    assert nobles.resources["tools"] == 0
    assert nobles.resources["land"] == 0

    assert nobles.missing_resources["food"] == 0
    assert nobles.missing_resources["wood"] == 0

    assert not nobles.is_temp
    assert nobles.temp["population"] == 0
    assert nobles.temp["resources"] == EMPTY_RESOURCES
    assert not nobles.starving
    assert not nobles.freezing


def test_class_name():
    state = State_Data()
    nobles = Nobles(state, 200)
    assert nobles.class_name == "nobles"


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
    nobles = Nobles(state, 80, resources)
    nobles.new_population += 20
    assert nobles.resources == resources
    assert nobles.population == 80
    assert nobles.new_resources == resources - INBUILT_RESOURCES["nobles"] * 20
    assert nobles.new_population == 100


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
    nobles = Nobles(state, 80, resources)
    nobles.new_population -= 20
    assert nobles.resources == resources
    assert nobles.population == 80
    assert nobles.new_resources == resources + INBUILT_RESOURCES["nobles"] * 20
    assert nobles.new_population == 60


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
    nobles = Nobles(state, 80, resources1)
    nobles.new_resources = resources2
    assert nobles.resources == resources1
    assert nobles.new_resources == resources2


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
    nobles = Nobles(state, 80, resources)

    nobles.grow_population(0.25)
    assert nobles._new_population == 100
    assert nobles._new_resources == \
        nobles.resources - INBUILT_RESOURCES["nobles"] * 20


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
    nobles = Nobles(state, 80, resources)

    nobles.grow_population(0.625)
    assert nobles._new_population == 130
    assert nobles._new_resources == \
        nobles.resources - INBUILT_RESOURCES["nobles"] * 50


def test_optimal_resources_january():
    state = Fake_State_Data(100, "January")
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200,
        "land": 0
    }
    nobles = Nobles(state, 100, resources)
    state._classes = [nobles]
    opt_res = nobles.optimal_resources
    assert opt_res == state.sm.optimal_resources["nobles"] * 100


def test_optimal_resources_july():
    state = Fake_State_Data(500, "July")
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200,
        "land": 0
    }
    nobles = Nobles(state, 80, resources)
    state._classes = [nobles]
    opt_res = nobles.optimal_resources
    assert opt_res == state.sm.optimal_resources["nobles"] * 80


def test_missing_resources_1():
    state = Fake_State_Data(500, "July")
    resources = {
        "food": -200,
        "wood": 500,
        "stone": -20,
        "iron": 0,
        "tools": 1200,
        "land": 0
    }
    missing = {
        "food": 200,
        "wood": 0,
        "stone": 20,
        "iron": 0,
        "tools": 0,
        "land": 0
    }
    nobles = Nobles(state, 80)
    nobles.new_resources = resources
    assert nobles.missing_resources == missing


def test_missing_resources_2():
    state = Fake_State_Data(500, "July")
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
    nobles = Nobles(state, 80)
    nobles.new_resources = resources
    assert nobles.missing_resources == missing


class Fake_Class:
    def __init__(self):
        self.class_name = "peasants"


def test_class_overpopulation_1():
    state = Fake_State_Data(500, "July")
    resources = {
        "food": 200,
        "wood": -500,
        "stone": -20,
        "iron": 0,
        "tools": 1200,
        "land": 0
    }
    missing_wood = 500
    missing_stone = 20

    nobles = Nobles(state, 80)
    nobles.new_resources = resources
    peasants = Fake_Class()
    nobles.lower_class = peasants

    inbuilt_wood = INBUILT_RESOURCES["nobles"]["wood"] - \
        INBUILT_RESOURCES["peasants"]["wood"]
    inbuilt_stone = INBUILT_RESOURCES["nobles"]["stone"] - \
        INBUILT_RESOURCES["peasants"]["stone"]

    overpop = max(missing_wood / inbuilt_wood, missing_stone / inbuilt_stone)

    assert nobles.class_overpopulation == overpop


def test_class_overpopulation_2():
    state = Fake_State_Data(500, "July")
    resources = {
        "food": 200,
        "wood": -50,
        "stone": -200,
        "iron": 0,
        "tools": 1200,
        "land": 0
    }
    missing_wood = 50
    missing_stone = 200

    nobles = Nobles(state, 80)
    nobles.new_resources = resources
    peasants = Fake_Class()
    nobles.lower_class = peasants

    inbuilt_wood = INBUILT_RESOURCES["nobles"]["wood"] - \
        INBUILT_RESOURCES["peasants"]["wood"]
    inbuilt_stone = INBUILT_RESOURCES["nobles"]["stone"] - \
        INBUILT_RESOURCES["peasants"]["stone"]

    overpop = max(missing_wood / inbuilt_wood, missing_stone / inbuilt_stone)

    assert nobles.class_overpopulation == overpop


def test_class_overpopulation_3():
    state = Fake_State_Data(500, "July")
    resources = {
        "food": 200,
        "wood": 500,
        "stone": 20,
        "iron": 0,
        "tools": 100,
        "land": 0
    }

    nobles = Nobles(state, 80, resources)
    peasants = Fake_Class()
    nobles.lower_class = peasants

    assert nobles.class_overpopulation == 0


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
            "tools": 0,
            "land": 0
        })
        self.prices = Arithmetic_Dict(prices.copy())
        self.sm = State_Modifiers(self)

    def get_available_employees(self):
        return self.available_employees


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
    resources2 = resources1 + INBUILT_RESOURCES["nobles"] * 80
    nobles = Nobles(state, 80, resources1)
    assert nobles.resources == resources1
    assert nobles.real_resources == resources2


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
        (INBUILT_RESOURCES["nobles"] * state.prices * 20).values()
    )
    nobles = Nobles(state, 20, resources)
    assert nobles.net_worth == 234567 + inbuilt_worth


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
    nobles = Nobles(state, 80, resources)
    nobles.consume()

    consumed = {
        "food": FOOD_CONSUMPTION * 80,
        "wood": WOOD_CONSUMPTION["January"] * 80
    }

    assert nobles._new_resources == nobles.resources - consumed
    assert nobles.missing_resources == EMPTY_RESOURCES


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
    nobles = Nobles(state, 80, resources)
    nobles.new_population += 20

    dicted = nobles.to_dict()
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
    nobles = Nobles.from_dict(state, dicted)

    assert nobles.parent == state
    assert nobles.population == 80
    assert nobles.resources == resources
    assert nobles.new_population == 80
    assert nobles.new_resources == resources


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
    nobles = Nobles(state, 0.3, resources)

    # This is normally done by State_Data when adding classes
    nobles.is_temp = False
    nobles.temp = {"population": 0, "resources": EMPTY_RESOURCES.copy()}

    nobles.handle_empty_class()
    assert nobles.population == 0
    assert nobles.resources == EMPTY_RESOURCES
    assert nobles.is_temp
    assert nobles.temp["population"] == 0.3
    assert nobles.temp["resources"] == resources


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
    nobles = Nobles(state, 0, EMPTY_RESOURCES)

    nobles.is_temp = True
    nobles.temp = {"population": 0.4, "resources": resources.copy()}
    nobles._new_population = 0.2

    nobles.handle_empty_class()
    assert nobles.population == approx(0.6)
    assert nobles.resources == resources
    assert not nobles.is_temp
    assert nobles.temp["population"] == 0
    assert nobles.temp["resources"] == EMPTY_RESOURCES


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
    nobles = Nobles(state, 0, EMPTY_RESOURCES)

    nobles.is_temp = True
    nobles.temp = {"population": 0.2, "resources": resources.copy()}
    nobles._new_population = 0.2
    nobles._new_resources = resources.copy()

    nobles.handle_empty_class()
    assert nobles.population == 0
    assert nobles.resources == EMPTY_RESOURCES
    assert nobles.is_temp
    assert nobles.temp["population"] == approx(0.4)
    assert nobles.temp["resources"] == resources * 2


def test_handle_negative_resources():
    state = State_Data()
    nobles = Nobles(state, 5)

    nobles._new_resources = Arithmetic_Dict({
        "food": 100,
        "wood": -100,
        "stone": -0.0001,
        "iron": -0.00099999,
        "tools": 0.0001,
        "land": 0
    })

    nobles.handle_negative_resources()
    assert nobles.new_resources == {
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
        "food": 1000,
        "wood": 2000,
        "iron": 0,
        "stone": 1000,
        "tools": 1000,
        "land": 10000
    })
    new_res = resources - INBUILT_RESOURCES["nobles"] * 20
    nobles = Nobles(state, 80, resources)
    nobles.new_population += 20
    nobles.flush()

    assert nobles.resources == new_res
    assert nobles.population == 100
    assert nobles.new_resources == new_res
    assert nobles.new_population == 100


def test_flush_exception():
    state = State_Data()
    nobles = Nobles(state, 80)
    resources = Arithmetic_Dict({
        "food": 100,
        "wood": -200,
        "iron": 0,
        "stone": 100,
        "tools": 100,
        "land": 0
    })
    nobles.new_resources = resources
    with raises(Exception):
        nobles.flush()
