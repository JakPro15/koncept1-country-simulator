from classes.constants import PEASANT_FOOD_NEEDED
from ..classes.state_data import State_Data
from ..classes.peasants import Peasants
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
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 80, resources, land)

    assert peasants._parent == state

    assert peasants._population == 80

    assert peasants.resources["food"] == 100
    assert peasants.resources["wood"] == 200
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 100

    assert peasants._land["fields"] == 1000
    assert peasants._land["woods"] == 500
    assert peasants._land["stone_mines"] == 0
    assert peasants._land["iron_mines"] == 0

    assert peasants.missing_resources["food"] == 0
    assert peasants.missing_resources["wood"] == 0

    assert peasants.class_overpopulation == 0


def test_default_constructor():
    state = State_Data()
    peasants = Peasants(state, 200)

    assert peasants._parent == state

    assert peasants._population == 200

    assert peasants.resources["food"] == 0
    assert peasants.resources["wood"] == 0
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 0

    assert peasants._land["fields"] == 0
    assert peasants._land["woods"] == 0
    assert peasants._land["stone_mines"] == 0
    assert peasants._land["iron_mines"] == 0

    assert peasants.missing_resources["food"] == 0
    assert peasants.missing_resources["wood"] == 0

    assert peasants.class_overpopulation == 0


def test_add_population_enough_resources():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 80, resources, land)

    peasants._add_population(20)
    assert peasants.resources["food"] == 100
    assert peasants.resources["wood"] == 140
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 40

    assert peasants.class_overpopulation == 0


def test_add_population_not_enough_tools():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 120
    }
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 80, resources, land)

    peasants._add_population(50)
    assert peasants.resources["food"] == 100
    assert peasants.resources["wood"] == 50
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == -30

    assert peasants.class_overpopulation == 10


def test_add_population_not_enough_wood():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 120,
        "iron": 0,
        "stone": 0,
        "tools": 200
    }
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 80, resources, land)

    peasants._add_population(50)
    assert peasants.resources["food"] == 100
    assert peasants.resources["wood"] == -30
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 50

    assert peasants.class_overpopulation == 10


def test_add_population_not_enough_both():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 120,
        "iron": 0,
        "stone": 0,
        "tools": 80
    }
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 80, resources, land)

    peasants._add_population(50)
    assert peasants.resources["food"] == 100
    assert peasants.resources["wood"] == -30
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == -70

    assert peasants.class_overpopulation == 24


def test_grow_population():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 80, resources, land)

    peasants.grow_population(0.256)
    assert peasants.resources["food"] == 100
    assert peasants.resources["wood"] == 140
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 40

    assert peasants.class_overpopulation == 0


def test_grow_population_not_enough_resources():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 120,
        "iron": 0,
        "stone": 0,
        "tools": 80
    }
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 80, resources, land)

    peasants.grow_population(0.63)
    assert peasants.resources["food"] == 100
    assert peasants.resources["wood"] == -30
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == -70

    assert peasants.class_overpopulation == 24


def test_get_food_needed_till_harvest():
    for month in PEASANT_FOOD_NEEDED:
        assert Peasants.get_food_needed_till_harvest(month) == \
            PEASANT_FOOD_NEEDED[month]


def test_get_food_needed_till_harvest_empty_months():
    for month in {'February', 'March', 'April', 'May', 'June', 'July'}:
        assert Peasants.get_food_needed_till_harvest(month) == 0


def test_optimal_resources_per_capita_february():
    month = "February"
    opt_res = Peasants.optimal_resources_per_capita(month)
    assert opt_res["food"] == 3
    assert opt_res["wood"] == 3.4
    assert opt_res["iron"] == 0
    assert opt_res["stone"] == 0
    assert opt_res["tools"] == 1.9


def test_optimal_resources_per_capita_august():
    month = "August"
    opt_res = Peasants.optimal_resources_per_capita(month)
    assert opt_res["food"] == 5
    assert opt_res["wood"] == 3.4
    assert opt_res["iron"] == 0
    assert opt_res["stone"] == 0
    assert opt_res["tools"] == 1.9


def test_optimal_resources_per_capita_november():
    month = "November"
    opt_res = Peasants.optimal_resources_per_capita(month)
    assert opt_res["food"] == 6
    assert opt_res["wood"] == 3.4
    assert opt_res["iron"] == 0
    assert opt_res["stone"] == 0
    assert opt_res["tools"] == 1.9


def test_calculate_optimal_resources_february():
    state = State_Data("February")
    peasants = Peasants(state, 200)
    peasants._calculate_optimal_resources()
    assert peasants._optimal_resources["food"] == 600
    assert peasants._optimal_resources["wood"] == 680
    assert peasants._optimal_resources["iron"] == 0
    assert peasants._optimal_resources["stone"] == 0
    assert peasants._optimal_resources["tools"] == 380


def test_calculate_optimal_resources_october():
    state = State_Data("October")
    peasants = Peasants(state, 100)
    peasants._calculate_optimal_resources()
    assert peasants._optimal_resources["food"] == 700
    assert peasants._optimal_resources["wood"] == 340
    assert peasants._optimal_resources["iron"] == 0
    assert peasants._optimal_resources["stone"] == 0
    assert peasants._optimal_resources["tools"] == 190


def test_get_optimal_resources():
    state = State_Data("February")
    peasants = Peasants(state, 200)
    peasants._calculate_optimal_resources()
    peasants._optimal_resources = {
        "food": 100,
        "wood": 100,
        "iron": 50,
        "stone": 0,
        "tools": 100
    }

    opt_res = peasants.get_optimal_resources()
    assert opt_res["food"] == 600
    assert opt_res["wood"] == 680
    assert opt_res["iron"] == 0
    assert opt_res["stone"] == 0
    assert opt_res["tools"] == 380


def test_get_working_peasants_not_enough_land():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 80, resources, land)

    assert peasants._get_working_peasants() == 75


def test_get_working_peasants_enough_land():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 60, resources, land)

    assert peasants._get_working_peasants() == 60


def test_produce_enough_land_and_tools():
    state = State_Data("March")
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 60, resources, land)

    peasants.produce()
    assert peasants.resources["food"] == 140
    assert peasants.resources["wood"] == 220
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 94
    assert peasants.class_overpopulation == 0


def test_produce_not_enough_land():
    state = State_Data("September")
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 80, resources, land)

    peasants.produce()
    assert peasants.resources["food"] == 250
    assert peasants.resources["wood"] == 225
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == approx(77.5)
    assert peasants.class_overpopulation == 0


def test_produce_not_enough_tools():
    state = State_Data("August")
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 32
    }
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 60, resources, land)

    peasants.produce()
    assert peasants.resources["food"] == 340
    assert peasants.resources["wood"] == 220
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == -4
    assert peasants.class_overpopulation == 2


def test_consume_enough_resources():
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
    assert peasants.resources["food"] == 20
    assert peasants.resources["wood"] == 152
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 100

    assert peasants.missing_resources["food"] == 0
    assert peasants.missing_resources["wood"] == 0


def test_consume_not_enough_food():
    state = State_Data()
    resources = {
        "food": 50,
        "wood": 100,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    peasants = Peasants(state, 80, resources)
    peasants.consume()
    assert peasants.resources["food"] == 0
    assert peasants.resources["wood"] == 52
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 100

    assert peasants.missing_resources["food"] == 30
    assert peasants.missing_resources["wood"] == 0


def test_consume_not_enough_wood():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 40,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    peasants = Peasants(state, 80, resources)
    peasants.consume()
    assert peasants.resources["food"] == 20
    assert peasants.resources["wood"] == 0
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 100

    assert peasants.missing_resources["food"] == 0
    assert peasants.missing_resources["wood"] == 8


def test_consume_not_enough_both():
    state = State_Data()
    resources = {
        "food": 50,
        "wood": 40,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    peasants = Peasants(state, 80, resources)
    peasants.consume()
    assert peasants.resources["food"] == 0
    assert peasants.resources["wood"] == 0
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 100

    assert peasants.missing_resources["food"] == 30
    assert peasants.missing_resources["wood"] == 8


def test_move_population_in_enough_resources():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    peasants = Peasants(state, 80, resources)

    peasants.move_population(20)

    assert peasants._population == 100

    assert peasants.resources["food"] == 100
    assert peasants.resources["wood"] == 140
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 40

    assert peasants.class_overpopulation == 0


def test_move_population_in_not_enough_resources():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 120,
        "iron": 0,
        "stone": 0,
        "tools": 200
    }
    peasants = Peasants(state, 80, resources)

    peasants.move_population(50, True)

    assert peasants._population == 130

    assert peasants.resources["food"] == 100
    assert peasants.resources["wood"] == -30
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 50

    assert peasants.class_overpopulation == 10


def test_move_population_out_no_demotion():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 120,
        "iron": 0,
        "stone": 0,
        "tools": 200
    }
    peasants = Peasants(state, 80, resources)

    peasants.move_population(-20)

    assert peasants._population == 60

    assert peasants.resources["food"] == 100
    assert peasants.resources["wood"] == 120
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 200

    assert peasants.class_overpopulation == 0


def test_move_population_out_demotion():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 120,
        "iron": 0,
        "stone": 0,
        "tools": 200
    }
    peasants = Peasants(state, 80, resources)

    peasants.move_population(-20, True)

    assert peasants._population == 60

    assert peasants.resources["food"] == 100
    assert peasants.resources["wood"] == 180
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 260

    assert peasants.class_overpopulation == 0
