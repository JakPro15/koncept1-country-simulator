from ..sources.auxiliaries.constants import (
    DEFAULT_PRICES,
    FOOD_PRODUCTION,
    IRON_PRODUCTION,
    MINER_TOOL_USAGE,
    OTHERS_WAGE,
    PEASANT_TOOL_USAGE,
    STONE_PRODUCTION,
    WOOD_CONSUMPTION,
    WOOD_PRODUCTION
)
from ..sources.state.state_data import State_Data
from ..sources.state.social_classes.nobles import Nobles
from ..sources.auxiliaries.arithmetic_dict import Arithmetic_Dict
from pytest import approx
from math import ceil


def test_constructor():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    land = {
        "fields": 1500,
        "woods": 900,
        "stone_mines": 5,
        "iron_mines": 2
    }
    nobles = Nobles(state, 80, resources, land)

    assert nobles.parent == state

    assert not nobles.employable

    assert nobles.population == 80

    assert nobles.resources["food"] == 100
    assert nobles.resources["wood"] == 200
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == 0
    assert nobles.resources["tools"] == 100

    assert nobles.land["fields"] == 1500
    assert nobles.land["woods"] == 900
    assert nobles.land["stone_mines"] == 5
    assert nobles.land["iron_mines"] == 2

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

    assert nobles.land["fields"] == 0
    assert nobles.land["woods"] == 0
    assert nobles.land["stone_mines"] == 0
    assert nobles.land["iron_mines"] == 0

    assert nobles.missing_resources["food"] == 0
    assert nobles.missing_resources["wood"] == 0

    assert nobles.class_overpopulation == 200


def test_add_population_enough_resources():
    state = State_Data()
    resources = {
        "food": 1000,
        "wood": 200,
        "iron": 0,
        "stone": 100,
        "tools": 100
    }
    land = {
        "fields": 10000,
        "woods": 1000,
        "stone_mines": 0,
        "iron_mines": 0
    }
    nobles = Nobles(state, 80, resources, land)

    nobles._add_population(20)
    assert nobles.resources["food"] == 1000
    assert nobles.resources["wood"] == 0
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == 20
    assert nobles.resources["tools"] == 20

    assert nobles.class_overpopulation == 0


def test_add_population_not_enough_tools():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 20000,
        "iron": 0,
        "stone": 1000,
        "tools": 120
    }
    land = {
        "fields": 10000,
        "woods": 5000,
        "stone_mines": 0,
        "iron_mines": 0
    }
    nobles = Nobles(state, 80, resources, land)

    nobles._add_population(50)
    assert nobles.resources["food"] == 100
    assert nobles.resources["wood"] == 19500
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == 800
    assert nobles.resources["tools"] == -80

    assert nobles.class_overpopulation == 80


def test_add_population_not_enough_stone():
    state = State_Data()
    resources = {
        "food": 1000,
        "wood": 20000,
        "iron": 0,
        "stone": 120,
        "tools": 1000
    }
    land = {
        "fields": 10000,
        "woods": 5000,
        "stone_mines": 0,
        "iron_mines": 0
    }
    nobles = Nobles(state, 80, resources, land)

    nobles._add_population(50)
    assert nobles.resources["food"] == 1000
    assert nobles.resources["wood"] == 19500
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == -80
    assert nobles.resources["tools"] == 800

    assert nobles.class_overpopulation == 20


def test_add_population_not_enough_wood():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 120,
        "iron": 0,
        "stone": 10000,
        "tools": 20000
    }
    land = {
        "fields": 10000,
        "woods": 5000,
        "stone_mines": 0,
        "iron_mines": 0
    }
    nobles = Nobles(state, 80, resources, land)

    nobles._add_population(50)
    assert nobles.resources["food"] == 100
    assert nobles.resources["wood"] == -380
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == 9800
    assert nobles.resources["tools"] == 19800

    assert ceil(nobles.class_overpopulation) == 55


def test_add_population_not_enough_all():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 120,
        "iron": 0,
        "stone": 8,
        "tools": 180
    }
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    nobles = Nobles(state, 80, resources, land)

    nobles._add_population(50)
    assert nobles.resources["food"] == 100
    assert nobles.resources["wood"] == -380
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == -192
    assert nobles.resources["tools"] == -20

    assert ceil(nobles.class_overpopulation) == 55


def test_grow_population():
    state = State_Data()
    resources = {
        "food": 1000,
        "wood": 200,
        "iron": 0,
        "stone": 100,
        "tools": 100
    }
    land = {
        "fields": 10000,
        "woods": 5000,
        "stone_mines": 0,
        "iron_mines": 0
    }
    nobles = Nobles(state, 80, resources, land)

    nobles.grow_population(0.25)
    assert nobles.resources["food"] == 1000
    assert nobles.resources["wood"] == 0
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == 20
    assert nobles.resources["tools"] == 20

    assert nobles.class_overpopulation == 0


def test_grow_population_not_enough_resources():
    state = State_Data()
    resources = {
        "food": 1000,
        "wood": 20000,
        "iron": 0,
        "stone": 120,
        "tools": 1000
    }
    land = {
        "fields": 10000,
        "woods": 5000,
        "stone_mines": 0,
        "iron_mines": 0
    }
    nobles = Nobles(state, 80, resources, land)

    nobles.grow_population(0.625)
    assert nobles.resources["food"] == 1000
    assert nobles.resources["wood"] == 19500
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == -80
    assert nobles.resources["tools"] == 800

    assert nobles.class_overpopulation == 20


def test_optimal_resources_per_capita_january():
    state = Fake_State_Data(100, "January")
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200
    }
    land = {
        "fields": 2500,
        "woods": 1500,
        "stone_mines": 2,
        "iron_mines": 1
    }
    nobles = Nobles(state, 80, resources, land)
    opt_res = nobles.optimal_resources_per_capita()
    assert opt_res["food"] == 12
    assert opt_res["wood"] == 4.6 + sum(WOOD_CONSUMPTION.values())
    assert opt_res["iron"] == 0
    assert opt_res["stone"] == 8
    assert opt_res["tools"] == approx(7.75)


def test_optimal_resources_per_capita_july():
    state = Fake_State_Data(500, "July")
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200
    }
    land = {
        "fields": 2500,
        "woods": 1500,
        "stone_mines": 2,
        "iron_mines": 1
    }
    nobles = Nobles(state, 80, resources, land)
    opt_res = nobles.optimal_resources_per_capita()
    assert opt_res["food"] == 12
    assert opt_res["wood"] == 4.6 + sum(WOOD_CONSUMPTION.values())
    assert opt_res["iron"] == 0
    assert opt_res["stone"] == 8
    assert opt_res["tools"] == approx(22.75)


def test_calculate_optimal_resources():
    state = Fake_State_Data(600, "July")
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200
    }
    land = {
        "fields": 2500,
        "woods": 1500,
        "stone_mines": 2,
        "iron_mines": 1
    }
    nobles = Nobles(state, 200, resources, land)
    opt_res = nobles.optimal_resources
    assert opt_res["food"] == 2400
    assert opt_res["wood"] == (4.6 + sum(WOOD_CONSUMPTION.values())) * 200
    assert opt_res["iron"] == 0
    assert opt_res["stone"] == 1600
    assert opt_res["tools"] == 2300


def test_get_total_land_for_produce():
    state = State_Data()
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 2,
        "iron_mines": 1
    }
    nobles = Nobles(state, 80, land=land)

    assert nobles._get_total_land_for_produce() == 7500


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
        self.prices = prices.copy()

    def get_available_employees(self):
        return self.available_employees


def test_get_employees_from_land():
    state = Fake_State_Data(1000)
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200
    }
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 2,
        "iron_mines": 1
    }
    nobles = Nobles(state, 80, resources, land)

    assert nobles._get_employees() == 375


def test_get_employees_from_resources():
    state = Fake_State_Data(1000)
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 900
    }
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 2,
        "iron_mines": 1
    }
    nobles = Nobles(state, 80, resources, land)

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
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 2,
        "iron_mines": 1
    }
    nobles = Nobles(state, 80, resources, land)

    assert nobles._get_employees() == 250


def test_get_ratios_default_prices():
    state = State_Data()
    land = {
        "fields": 2500,
        "woods": 1500,
        "stone_mines": 2,
        "iron_mines": 1
    }
    nobles = Nobles(state, 80, land=land)

    ratios = nobles._get_ratios(DEFAULT_PRICES)
    assert ratios["food"] == approx(0.25)
    assert ratios["wood"] == approx(0.25)
    assert ratios["stone"] == approx(0.25)
    assert ratios["iron"] == approx(0.25)


def test_get_ratios_different_prices():
    state = State_Data()
    land = {
        "fields": 2500,
        "woods": 1500,
        "stone_mines": 2,
        "iron_mines": 1
    }
    nobles = Nobles(state, 80, land=land)

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
    land = {
        "fields": 2500,
        "woods": 1500,
        "stone_mines": 2,
        "iron_mines": 1
    }
    nobles = Nobles(state, 80, land=land)

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


def test_get_ratioed_employees_enough_land():
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
    land = {
        "fields": 25000,
        "woods": 15000,
        "stone_mines": 20,
        "iron_mines": 10
    }
    nobles = Nobles(state, 80, resources, land)

    employees = nobles._get_ratioed_employees()
    assert employees["food"] == approx(28.6, abs=0.1)
    assert employees["wood"] == approx(35.7, abs=0.1)
    assert employees["stone"] == approx(14.3, abs=0.1)
    assert employees["iron"] == approx(21.4, abs=0.1)


def test_get_ratioed_employees_not_enough_land_1():
    prices = Arithmetic_Dict({
        "food": 1.2,
        "wood": 1.5 * DEFAULT_PRICES["wood"],
        "stone": 0.6 * DEFAULT_PRICES["stone"],
        "iron": 0.9 * DEFAULT_PRICES["iron"]
    })

    state = Fake_State_Data(120, prices=prices)
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200
    }
    land = {
        "fields": 25000,
        "woods": 400,
        "stone_mines": 20,
        "iron_mines": 10
    }
    nobles = Nobles(state, 100, resources, land)

    employees = nobles._get_ratioed_employees()
    assert employees["food"] == approx(44.4, abs=0.1)
    assert employees["wood"] == 20
    assert employees["stone"] == approx(22.2, abs=0.1)
    assert employees["iron"] == approx(33.3, abs=0.1)


def test_get_ratioed_employees_not_enough_land_2():
    prices = Arithmetic_Dict({
        "food": 1.2,
        "wood": 1.5 * DEFAULT_PRICES["wood"],
        "stone": 0.6 * DEFAULT_PRICES["stone"],
        "iron": 0.9 * DEFAULT_PRICES["iron"]
    })

    state = Fake_State_Data(120, prices=prices)
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200
    }
    land = {
        "fields": 25000,
        "woods": 400,
        "stone_mines": 20,
        "iron_mines": 0
    }
    nobles = Nobles(state, 100, resources, land)

    employees = nobles._get_ratioed_employees()
    assert employees["food"] == approx(66.7, abs=0.1)
    assert employees["wood"] == 20
    assert employees["stone"] == approx(33.3, abs=0.1)
    assert employees["iron"] == 0


def test_get_ratioed_employees_employees_limited_by_land():
    prices = Arithmetic_Dict({
        "food": 1.2,
        "wood": 1.5 * DEFAULT_PRICES["wood"],
        "stone": 0.6 * DEFAULT_PRICES["stone"],
        "iron": 0.9 * DEFAULT_PRICES["iron"]
    })

    state = Fake_State_Data(1000, prices=prices)
    resources = {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 1200
    }
    land = {
        "fields": 200,
        "woods": 400,
        "stone_mines": 0,
        "iron_mines": 1
    }
    nobles = Nobles(state, 100, resources, land)

    employees = nobles._get_ratioed_employees()
    assert employees["food"] == approx(10)
    assert employees["wood"] == approx(20)
    assert employees["stone"] == 0
    assert employees["iron"] == approx(100)


def test_get_produced_resources_february():
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
    land = {
        "fields": 25000,
        "woods": 15000,
        "stone_mines": 20,
        "iron_mines": 10
    }
    nobles = Nobles(state, 80, resources, land)

    produced = nobles._get_produced_resources()
    assert produced["food"] == \
        approx(FOOD_PRODUCTION["February"] * 28.6, abs=0.1)
    assert produced["wood"] == approx(WOOD_PRODUCTION * 35.7, abs=0.1)
    assert produced["stone"] == approx(STONE_PRODUCTION * 14.3, abs=0.1)
    assert produced["iron"] == approx(IRON_PRODUCTION * 21.4, abs=0.1)


def test_get_produced_resources_august():
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
    land = {
        "fields": 25000,
        "woods": 15000,
        "stone_mines": 20,
        "iron_mines": 10
    }
    nobles = Nobles(state, 80, resources, land)

    produced = nobles._get_produced_resources()

    assert produced["food"] == \
        approx(FOOD_PRODUCTION["August"] * 28.6, abs=0.6)
    assert produced["wood"] == approx(WOOD_PRODUCTION * 35.7, abs=0.1)
    assert produced["stone"] == approx(STONE_PRODUCTION * 14.3, abs=0.1)
    assert produced["iron"] == approx(IRON_PRODUCTION * 21.4, abs=0.1)


def test_get_tools_used_february():
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
    land = {
        "fields": 25000,
        "woods": 15000,
        "stone_mines": 20,
        "iron_mines": 10
    }
    nobles = Nobles(state, 80, resources, land)

    assert nobles._get_tools_used() == approx(
        MINER_TOOL_USAGE * 35.7 + PEASANT_TOOL_USAGE["February"] * 64.3,
        abs=0.1
    )


def test_get_tools_used_august():
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
    land = {
        "fields": 25000,
        "woods": 15000,
        "stone_mines": 20,
        "iron_mines": 10
    }
    nobles = Nobles(state, 80, resources, land)

    assert nobles._get_tools_used() == approx(
            MINER_TOOL_USAGE * 35.7 + PEASANT_TOOL_USAGE["August"] * 64.3,
            abs=0.1
        )


def test_produce():
    prices = Arithmetic_Dict({
        "food": 1.2,
        "wood": 1.5 * DEFAULT_PRICES["wood"],
        "stone": 0.6 * DEFAULT_PRICES["stone"],
        "iron": 0.9 * DEFAULT_PRICES["iron"]
    })

    state = Fake_State_Data(100, "August", prices)
    resources = {
        "food": 1000,
        "wood": 50,
        "stone": 5,
        "iron": 30,
        "tools": 1200
    }
    land = {
        "fields": 25000,
        "woods": 15000,
        "stone_mines": 20,
        "iron_mines": 10
    }
    nobles = Nobles(state, 80, resources, land)
    nobles.produce()

    assert nobles.resources["food"] == approx(
        (1 - OTHERS_WAGE) * FOOD_PRODUCTION["August"] * 28.6 + 1000, abs=0.6
    )
    assert nobles.resources["wood"] == \
        approx((1 - OTHERS_WAGE) * WOOD_PRODUCTION * 35.7 + 50, abs=0.1)
    assert nobles.resources["stone"] == \
        approx((1 - OTHERS_WAGE) * STONE_PRODUCTION * 14.3 + 5, abs=0.1)
    assert nobles.resources["iron"] == \
        approx((1 - OTHERS_WAGE) * IRON_PRODUCTION * 21.4 + 30, abs=0.1)
    assert nobles.resources["tools"] == approx(
        1200 - MINER_TOOL_USAGE * 35.7 - PEASANT_TOOL_USAGE["August"] * 64.3,
        abs=0.1
    )

    assert state.payments["food"] == \
        approx(OTHERS_WAGE * FOOD_PRODUCTION["August"] * 28.6, abs=0.6)
    assert state.payments["wood"] == \
        approx(OTHERS_WAGE * WOOD_PRODUCTION * 35.7, abs=0.1)
    assert state.payments["stone"] == \
        approx(OTHERS_WAGE * STONE_PRODUCTION * 14.3, abs=0.1)
    assert state.payments["iron"] == \
        approx(OTHERS_WAGE * IRON_PRODUCTION * 21.4, abs=0.1)

    assert nobles.class_overpopulation == 0


def test_consume_enough_resources():
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
    assert nobles.resources["food"] == 20
    assert nobles.resources["wood"] == 152
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == 0
    assert nobles.resources["tools"] == 100

    assert nobles.missing_resources["food"] == 0
    assert nobles.missing_resources["wood"] == 0


def test_consume_not_enough_food():
    state = State_Data()
    resources = {
        "food": 50,
        "wood": 100,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    nobles = Nobles(state, 80, resources)
    nobles.consume()
    assert nobles.resources["food"] == -30
    assert nobles.resources["wood"] == 52
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == 0
    assert nobles.resources["tools"] == 100

    assert nobles.missing_resources["food"] == 30
    assert nobles.missing_resources["wood"] == 0


def test_consume_not_enough_wood():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 40,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    nobles = Nobles(state, 80, resources)
    nobles.consume()
    assert nobles.resources["food"] == 20
    assert nobles.resources["wood"] == -8
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == 0
    assert nobles.resources["tools"] == 100

    assert nobles.missing_resources["food"] == 0
    assert nobles.missing_resources["wood"] == 8


def test_consume_not_enough_both():
    state = State_Data()
    resources = {
        "food": 50,
        "wood": 40,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    nobles = Nobles(state, 80, resources)
    nobles.consume()
    assert nobles.resources["food"] == -30
    assert nobles.resources["wood"] == -8
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == 0
    assert nobles.resources["tools"] == 100

    assert nobles.missing_resources["food"] == 30
    assert nobles.missing_resources["wood"] == 8


def test_move_population_in_enough_resources():
    state = State_Data()
    resources = {
        "food": 1000,
        "wood": 200,
        "iron": 0,
        "stone": 100,
        "tools": 100
    }
    land = {
        "fields": 10000,
        "woods": 1000,
        "stone_mines": 0,
        "iron_mines": 0
    }
    nobles = Nobles(state, 80, resources, land)

    nobles.move_population(20)

    assert nobles.population == 100

    assert nobles.resources["food"] == 1000
    assert nobles.resources["wood"] == 0
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == 20
    assert nobles.resources["tools"] == 20

    assert nobles.class_overpopulation == 0


def test_move_population_in_not_enough_resources():
    state = State_Data()
    resources = {
        "food": 1000,
        "wood": 20000,
        "iron": 0,
        "stone": 1000,
        "tools": 120
    }
    land = {
        "fields": 10000,
        "woods": 5000,
        "stone_mines": 0,
        "iron_mines": 0
    }
    nobles = Nobles(state, 80, resources, land)

    nobles.move_population(50, True)

    assert nobles.population == 130

    assert nobles.resources["food"] == 1000
    assert nobles.resources["wood"] == 19500
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == 800
    assert nobles.resources["tools"] == -80

    assert nobles.class_overpopulation == 80


def test_move_population_in_not_enough_land():
    state = State_Data()
    resources = {
        "food": 1000,
        "wood": 200,
        "iron": 0,
        "stone": 200,
        "tools": 100
    }
    land = {
        "fields": 2575,
        "woods": 667,
        "stone_mines": 0,
        "iron_mines": 0
    }
    nobles = Nobles(state, 80, resources, land)

    nobles.move_population(20)

    assert nobles.population == 100

    assert nobles.resources["food"] == 1000
    assert nobles.resources["wood"] == 0
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == 120
    assert nobles.resources["tools"] == 20

    assert ceil(nobles.class_overpopulation) == 19


def test_move_population_out_no_demotion():
    state = State_Data()
    resources = {
        "food": 1000,
        "wood": 120,
        "iron": 0,
        "stone": 0,
        "tools": 200
    }
    land = {
        "fields": 10000,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    nobles = Nobles(state, 80, resources, land)

    nobles.move_population(-20)

    assert nobles.population == 60

    assert nobles.resources["food"] == 1000
    assert nobles.resources["wood"] == 120
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == 0
    assert nobles.resources["tools"] == 200

    assert nobles.class_overpopulation == 0


def test_move_population_out_demotion():
    state = State_Data()
    resources = {
        "food": 1000,
        "wood": 120,
        "iron": 0,
        "stone": 0,
        "tools": 200
    }
    land = {
        "fields": 10000,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    nobles = Nobles(state, 80, resources, land)

    nobles.move_population(-20, True)

    assert nobles.population == 60

    assert nobles.resources["food"] == 1000
    assert nobles.resources["wood"] == 260
    assert nobles.resources["iron"] == 0
    assert nobles.resources["stone"] == 80
    assert nobles.resources["tools"] == 220

    assert nobles.class_overpopulation == 0
