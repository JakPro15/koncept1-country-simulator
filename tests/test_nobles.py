from ..sources.auxiliaries.constants import (
    DEFAULT_PRICES,
    EMPTY_RESOURCES,
    FOOD_CONSUMPTION,
    FOOD_PRODUCTION,
    INBUILT_RESOURCES,
    IRON_PRODUCTION,
    MINER_TOOL_USAGE,
    OPTIMAL_RESOURCES,
    OTHERS_WAGE,
    PEASANT_TOOL_USAGE,
    RESOURCES,
    STONE_PRODUCTION,
    WOOD_CONSUMPTION,
    WOOD_PRODUCTION
)
from ..sources.state.state_data import State_Data
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
        "tools": 100
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

    assert nobles.missing_resources["food"] == 0
    assert nobles.missing_resources["wood"] == 0


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

    assert nobles.missing_resources["food"] == 0
    assert nobles.missing_resources["wood"] == 0


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
        "tools": 100
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
        "tools": 100
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
        "tools": 100
    })
    resources2 = Arithmetic_Dict({
        "food": 150,
        "wood": 10,
        "iron": 11,
        "stone": 12,
        "tools": 100
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
        "tools": 100
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
        "tools": 1000
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
        "tools": 1200
    }
    nobles = Nobles(state, 80, resources)
    opt_res = nobles.optimal_resources
    added_tools = Arithmetic_Dict({"tools": 400})
    assert opt_res == OPTIMAL_RESOURCES["nobles"] * 80 + added_tools


def test_optimal_resources_july():
    state = Fake_State_Data(500, "July")
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200
    }
    nobles = Nobles(state, 80, resources)
    opt_res = nobles.optimal_resources
    added_tools = Arithmetic_Dict({"tools": 2000})
    assert opt_res == OPTIMAL_RESOURCES["nobles"] * 80 + added_tools


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
    nobles = Nobles(state, 80, resources)
    assert nobles.missing_resources == missing


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
        "tools": 1200
    }
    missing_wood = 500
    missing_stone = 20

    nobles = Nobles(state, 80, resources)
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
        "tools": 1200
    }
    missing_wood = 50
    missing_stone = 200

    nobles = Nobles(state, 80, resources)
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
        "tools": 100
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
            "tools": 0
        })
        self.prices = Arithmetic_Dict(prices.copy())

    def get_available_employees(self):
        return self.available_employees


def test_get_employees_from_resources():
    state = Fake_State_Data(1000)
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 900
    }
    nobles = Nobles(state, 80, resources)

    assert nobles._get_employees() == 300


def test_get_employees_from_state():
    state = Fake_State_Data(250)
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200
    }
    nobles = Nobles(state, 80, resources)

    assert nobles._get_employees() == 250


def test_get_ratios_default_prices():
    state = State_Data()
    nobles = Nobles(state, 80)

    ratios = nobles._get_ratios(DEFAULT_PRICES)
    assert ratios["food"] == approx(0.25)
    assert ratios["wood"] == approx(0.25)
    assert ratios["stone"] == approx(0.25)
    assert ratios["iron"] == approx(0.25)


def test_get_ratios_different_prices():
    state = State_Data()
    nobles = Nobles(state, 80)

    prices = Arithmetic_Dict({
        "food": 1.2,
        "wood": 1.5 * DEFAULT_PRICES["wood"],
        "stone": 0.6 * DEFAULT_PRICES["stone"],
        "iron": 0.9 * DEFAULT_PRICES["iron"]
    })

    ratios = nobles._get_ratios(prices)
    assert ratios["food"] == approx(0.286, abs=0.001)
    assert ratios["wood"] == approx(0.357, abs=0.001)
    assert ratios["stone"] == approx(0.143, abs=0.001)
    assert ratios["iron"] == approx(0.214, abs=0.001)


def test_get_ratios_prices_with_zeros():
    state = State_Data()
    nobles = Nobles(state, 80)

    prices = Arithmetic_Dict({
        "food": 1.2,
        "wood": 0,
        "stone": 0.6 * DEFAULT_PRICES["stone"],
        "iron": 0
    })

    ratios = nobles._get_ratios(prices)
    assert ratios["food"] == approx(0.667, abs=0.001)
    assert ratios["wood"] == 0
    assert ratios["stone"] == approx(0.333, abs=0.001)
    assert ratios["iron"] == 0


def test_get_ratioed_employees():
    prices = Arithmetic_Dict({
        "food": 1.2,
        "wood": 1.5 * DEFAULT_PRICES["wood"],
        "stone": 0.6 * DEFAULT_PRICES["stone"],
        "iron": 0.9 * DEFAULT_PRICES["iron"]
    })

    state = Fake_State_Data(100, prices=prices)
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200
    }
    nobles = Nobles(state, 80, resources)

    employees = nobles._get_ratioed_employees()
    assert employees["food"] == approx(28.6, abs=0.1)
    assert employees["wood"] == approx(35.7, abs=0.1)
    assert employees["stone"] == approx(14.3, abs=0.1)
    assert employees["iron"] == approx(21.4, abs=0.1)


def test_get_tools_used():
    prices = Arithmetic_Dict({
        "food": 1.2,
        "wood": 1.5 * DEFAULT_PRICES["wood"],
        "stone": 0.6 * DEFAULT_PRICES["stone"],
        "iron": 0.9 * DEFAULT_PRICES["iron"]
    })

    state = Fake_State_Data(100, "February", prices)
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200
    }
    nobles = Nobles(state, 80, resources)

    assert nobles._get_tools_used(nobles._get_ratioed_employees()) == approx(
        MINER_TOOL_USAGE * 35.7 + PEASANT_TOOL_USAGE * 64.3,
        abs=0.1
    )


def test_produce_february():
    prices = Arithmetic_Dict({
        "food": 1.2,
        "wood": 1.5 * DEFAULT_PRICES["wood"],
        "stone": 0.6 * DEFAULT_PRICES["stone"],
        "iron": 0.9 * DEFAULT_PRICES["iron"]
    })

    state = Fake_State_Data(100, "February", prices)
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200
    }
    nobles = Nobles(state, 80, resources)

    final_res = Arithmetic_Dict({
        "food": FOOD_PRODUCTION["February"] * 28.6,
        "wood": WOOD_PRODUCTION * 35.7,
        "stone": STONE_PRODUCTION * 14.3,
        "iron": IRON_PRODUCTION * 21.4,
        "tools": 0
    })
    payments = final_res * OTHERS_WAGE
    final_res -= payments
    final_res["tools"] = 1200 - (
        MINER_TOOL_USAGE * 35.7 + PEASANT_TOOL_USAGE * 64.3
    )

    nobles.produce()
    for resource in RESOURCES:
        assert nobles._new_resources[resource] == \
            approx(final_res[resource], abs=1)
        assert state.payments[resource] == \
            approx(payments[resource], abs=1)


def test_produce_august():
    prices = Arithmetic_Dict({
        "food": 1.2,
        "wood": 1.5 * DEFAULT_PRICES["wood"],
        "stone": 0.6 * DEFAULT_PRICES["stone"],
        "iron": 0.9 * DEFAULT_PRICES["iron"]
    })

    state = Fake_State_Data(100, "August", prices)
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200
    }
    nobles = Nobles(state, 80, resources)

    final_res = Arithmetic_Dict({
        "food": FOOD_PRODUCTION["August"] * 28.6,
        "wood": WOOD_PRODUCTION * 35.7,
        "stone": STONE_PRODUCTION * 14.3,
        "iron": IRON_PRODUCTION * 21.4,
        "tools": 0
    })
    payments = final_res * OTHERS_WAGE
    final_res -= payments
    final_res["tools"] = 1200 - (
        MINER_TOOL_USAGE * 35.7 + PEASANT_TOOL_USAGE * 64.3
    )

    nobles.produce()
    for resource in RESOURCES:
        assert nobles._new_resources[resource] == \
            approx(final_res[resource], abs=1)
        assert state.payments[resource] == \
            approx(payments[resource], abs=1)


def test_consume():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
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
        "tools": 100
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
        "tools": 100
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
        "tools": 100
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
        "tools": 100
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
        "tools": 100
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
        "tools": 0.0001
    })

    nobles.handle_negative_resources()
    assert nobles.new_resources == {
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
        "tools": 100
    })
    nobles.new_resources = resources
    with raises(AssertionError):
        nobles.flush()
