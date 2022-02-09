from ..classes.state_data import State_Data
from ..classes.peasants import Peasants
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
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 80, resources, land)

    assert peasants.parent == state

    assert not peasants.employable

    assert peasants.population == 80

    assert peasants.resources["food"] == 100
    assert peasants.resources["wood"] == 200
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 100

    assert peasants.land["fields"] == 1000
    assert peasants.land["woods"] == 500
    assert peasants.land["stone_mines"] == 0
    assert peasants.land["iron_mines"] == 0

    assert peasants.missing_resources["food"] == 0
    assert peasants.missing_resources["wood"] == 0

    assert peasants.class_overpopulation == 0


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

    assert peasants.land["fields"] == 0
    assert peasants.land["woods"] == 0
    assert peasants.land["stone_mines"] == 0
    assert peasants.land["iron_mines"] == 0

    assert peasants.missing_resources["food"] == 0
    assert peasants.missing_resources["wood"] == 0

    assert peasants.class_overpopulation == 200


def test_land():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    land = {
        "fields": 0,
        "woods": 0,
        "stone_mines": 3,
        "iron_mines": 0
    }
    with raises(AssertionError):
        Peasants(state, 80, resources, land)

    land = {
        "fields": 0,
        "woods": 0,
        "stone_mines": 0,
        "iron_mines": 1
    }
    with raises(AssertionError):
        Peasants(state, 80, resources, land)


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

    peasants.grow_population(0.25)
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
        "woods": 950,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 80, resources, land)

    peasants.grow_population(0.625)
    assert peasants.resources["food"] == 100
    assert peasants.resources["wood"] == -30
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == -70

    assert peasants.class_overpopulation == 24


def test_optimal_resources_per_capita_february():
    state = State_Data("February")
    peasants = Peasants(state, 200)
    opt_res = peasants.optimal_resources_per_capita()
    assert opt_res["food"] == 4
    assert opt_res["wood"] == 3.4
    assert opt_res["iron"] == 0
    assert opt_res["stone"] == 0
    assert opt_res["tools"] == 1.9


def test_optimal_resources_per_capita_august():
    state = State_Data("August")
    peasants = Peasants(state, 200)
    opt_res = peasants.optimal_resources_per_capita()
    assert opt_res["food"] == 4
    assert opt_res["wood"] == 3.4
    assert opt_res["iron"] == 0
    assert opt_res["stone"] == 0
    assert opt_res["tools"] == 1.9


def test_calculate_optimal_resources_february():
    state = State_Data("February")
    peasants = Peasants(state, 200)
    opt_res = peasants.optimal_resources
    assert opt_res["food"] == 800
    assert opt_res["wood"] == 680
    assert opt_res["iron"] == 0
    assert opt_res["stone"] == 0
    assert opt_res["tools"] == 380


def test_calculate_optimal_resources_october():
    state = State_Data("October")
    peasants = Peasants(state, 100)
    opt_res = peasants.optimal_resources
    assert opt_res["food"] == 400
    assert opt_res["wood"] == 340
    assert opt_res["iron"] == 0
    assert opt_res["stone"] == 0
    assert opt_res["tools"] == 190


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
        "fields": 1010,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 80, resources, land)

    assert peasants._get_working_peasants() == approx(75.5)


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
    assert peasants.resources["food"] == -30
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
    assert peasants.resources["wood"] == -8
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
    assert peasants.resources["food"] == -30
    assert peasants.resources["wood"] == -8
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
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 80, resources, land)

    peasants.move_population(20)

    assert peasants.population == 100

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
    land = {
        "fields": 1000,
        "woods": 1000,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 80, resources, land)

    peasants.move_population(50, True)

    assert peasants.population == 130

    assert peasants.resources["food"] == 100
    assert peasants.resources["wood"] == -30
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 50

    assert peasants.class_overpopulation == 10


def test_move_population_in_not_enough_land():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    land = {
        "fields": 850,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 80, resources, land)

    peasants.move_population(20)

    assert peasants.population == 100

    assert peasants.resources["food"] == 100
    assert peasants.resources["wood"] == 140
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 40

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
    land = {
        "fields": 850,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 80, resources, land)

    peasants.move_population(-20)

    assert peasants.population == 60

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
    land = {
        "fields": 1000,
        "woods": 500,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, 80, resources, land)

    peasants.move_population(-20, True)

    assert peasants.population == 60

    assert peasants.resources["food"] == 100
    assert peasants.resources["wood"] == 180
    assert peasants.resources["iron"] == 0
    assert peasants.resources["stone"] == 0
    assert peasants.resources["tools"] == 260

    assert peasants.class_overpopulation == 0
