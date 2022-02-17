from ..classes.state_data import State_Data
from ..classes.artisans import Artisans
from pytest import raises
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
        "fields": 0,
        "woods": 0,
        "stone_mines": 0,
        "iron_mines": 0
    }
    artisans = Artisans(state, 80, resources, land)

    assert artisans.parent == state

    assert not artisans.employable

    assert artisans.population == 80

    assert artisans.resources["food"] == 100
    assert artisans.resources["wood"] == 200
    assert artisans.resources["iron"] == 0
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == 100

    assert artisans.land["fields"] == 0
    assert artisans.land["woods"] == 0
    assert artisans.land["stone_mines"] == 0
    assert artisans.land["iron_mines"] == 0

    assert artisans.missing_resources["food"] == 0
    assert artisans.missing_resources["wood"] == 0

    assert artisans.class_overpopulation == 0


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

    assert artisans.land["fields"] == 0
    assert artisans.land["woods"] == 0
    assert artisans.land["stone_mines"] == 0
    assert artisans.land["iron_mines"] == 0

    assert artisans.missing_resources["food"] == 0
    assert artisans.missing_resources["wood"] == 0

    assert artisans.class_overpopulation == 0


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
        "fields": 20,
        "woods": 0,
        "stone_mines": 0,
        "iron_mines": 0
    }
    with raises(AssertionError):
        Artisans(state, 80, resources, land)

    land = {
        "fields": 0,
        "woods": 30,
        "stone_mines": 0,
        "iron_mines": 0
    }
    with raises(AssertionError):
        Artisans(state, 80, resources, land)

    land = {
        "fields": 0,
        "woods": 0,
        "stone_mines": 3,
        "iron_mines": 0
    }
    with raises(AssertionError):
        Artisans(state, 80, resources, land)

    land = {
        "fields": 0,
        "woods": 0,
        "stone_mines": 0,
        "iron_mines": 1
    }
    with raises(AssertionError):
        Artisans(state, 80, resources, land)


def test_add_population_enough_resources():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 200,
        "stone": 0,
        "tools": 100
    }
    artisans = Artisans(state, 80, resources)

    artisans._add_population(20)
    assert artisans.resources["food"] == 100
    assert artisans.resources["wood"] == 160
    assert artisans.resources["iron"] == 160
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == 40

    assert artisans.class_overpopulation == 0


def test_add_population_not_enough_tools():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 200,
        "stone": 0,
        "tools": 120
    }
    artisans = Artisans(state, 80, resources)

    artisans._add_population(50)
    assert artisans.resources["food"] == 100
    assert artisans.resources["wood"] == 100
    assert artisans.resources["iron"] == 100
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == -30

    assert artisans.class_overpopulation == 10


def test_add_population_not_enough_wood():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 70,
        "iron": 100,
        "stone": 0,
        "tools": 200
    }
    artisans = Artisans(state, 80, resources)

    artisans._add_population(50)
    assert artisans.resources["food"] == 100
    assert artisans.resources["wood"] == -30
    assert artisans.resources["iron"] == 0
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == 50

    assert artisans.class_overpopulation == 15


def test_add_population_not_enough_both():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 70,
        "iron": 0,
        "stone": 0,
        "tools": 80
    }
    artisans = Artisans(state, 80, resources)

    artisans._add_population(50)
    assert artisans.resources["food"] == 100
    assert artisans.resources["wood"] == -30
    assert artisans.resources["iron"] == -100
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == -70

    assert artisans.class_overpopulation == 50


def test_grow_population():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 200,
        "stone": 0,
        "tools": 100
    }
    artisans = Artisans(state, 80, resources)

    artisans.grow_population(0.25)
    assert artisans.resources["food"] == 100
    assert artisans.resources["wood"] == 160
    assert artisans.resources["iron"] == 160
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == 40

    assert artisans.class_overpopulation == 0


def test_grow_population_not_enough_resources():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 70,
        "iron": 100,
        "stone": 0,
        "tools": 80
    }
    artisans = Artisans(state, 80, resources)

    artisans.grow_population(0.625)
    assert artisans.resources["food"] == 100
    assert artisans.resources["wood"] == -30
    assert artisans.resources["iron"] == 0
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == -70

    assert ceil(artisans.class_overpopulation) == 24


def test_optimal_resources_per_capita_february():
    state = State_Data("February")
    artisans = Artisans(state, 200)
    opt_res = artisans.optimal_resources_per_capita()
    assert opt_res["food"] == 4
    assert opt_res["wood"] == 3.7
    assert opt_res["iron"] == 2.5
    assert opt_res["stone"] == 0
    assert opt_res["tools"] == 1.6


def test_optimal_resources_per_capita_august():
    state = State_Data("August")
    artisans = Artisans(state, 200)
    opt_res = artisans.optimal_resources_per_capita()
    assert opt_res["food"] == 4
    assert opt_res["wood"] == 3.7
    assert opt_res["iron"] == 2.5
    assert opt_res["stone"] == 0
    assert opt_res["tools"] == 1.6


def test_calculate_optimal_resources_february():
    state = State_Data("February")
    artisans = Artisans(state, 200)
    opt_res = artisans.optimal_resources
    assert opt_res["food"] == 800
    assert opt_res["wood"] == 740
    assert opt_res["iron"] == 500
    assert opt_res["stone"] == 0
    assert opt_res["tools"] == 320


def test_calculate_optimal_resources_october():
    state = State_Data("October")
    artisans = Artisans(state, 100)
    opt_res = artisans.optimal_resources
    assert opt_res["food"] == 400
    assert opt_res["wood"] == 370
    assert opt_res["iron"] == 250
    assert opt_res["stone"] == 0
    assert opt_res["tools"] == 160


def test_produce_enough_resources():
    state = State_Data("March")
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 100,
        "stone": 0,
        "tools": 100
    }
    artisans = Artisans(state, 60, resources)

    artisans.produce()
    assert artisans.resources["food"] == 100
    assert artisans.resources["wood"] == 188
    assert artisans.resources["iron"] == 70
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == 151
    assert artisans.class_overpopulation == 0


def test_produce_not_enough_resources():
    state = State_Data("March")
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 25,
        "stone": 0,
        "tools": 100
    }
    artisans = Artisans(state, 60, resources)

    artisans.produce()
    assert artisans.resources["food"] == 100
    assert artisans.resources["wood"] == 188
    assert artisans.resources["iron"] == -5
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == 151
    assert ceil(artisans.class_overpopulation) == 3


def test_consume_enough_resources():
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
    assert artisans.resources["food"] == 20
    assert artisans.resources["wood"] == 152
    assert artisans.resources["iron"] == 0
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == 100

    assert artisans.missing_resources["food"] == 0
    assert artisans.missing_resources["wood"] == 0


def test_consume_not_enough_food():
    state = State_Data()
    resources = {
        "food": 50,
        "wood": 100,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    artisans = Artisans(state, 80, resources)
    artisans.consume()
    assert artisans.resources["food"] == -30
    assert artisans.resources["wood"] == 52
    assert artisans.resources["iron"] == 0
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == 100

    assert artisans.missing_resources["food"] == 30
    assert artisans.missing_resources["wood"] == 0


def test_consume_not_enough_wood():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 40,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    artisans = Artisans(state, 80, resources)
    artisans.consume()
    assert artisans.resources["food"] == 20
    assert artisans.resources["wood"] == -8
    assert artisans.resources["iron"] == 0
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == 100

    assert artisans.missing_resources["food"] == 0
    assert artisans.missing_resources["wood"] == 8


def test_consume_not_enough_both():
    state = State_Data()
    resources = {
        "food": 50,
        "wood": 40,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    artisans = Artisans(state, 80, resources)
    artisans.consume()
    assert artisans.resources["food"] == -30
    assert artisans.resources["wood"] == -8
    assert artisans.resources["iron"] == 0
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == 100

    assert artisans.missing_resources["food"] == 30
    assert artisans.missing_resources["wood"] == 8


def test_move_population_in_enough_resources():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 200,
        "stone": 0,
        "tools": 100
    }
    artisans = Artisans(state, 80, resources)

    artisans.move_population(20)

    assert artisans.population == 100

    assert artisans.resources["food"] == 100
    assert artisans.resources["wood"] == 160
    assert artisans.resources["iron"] == 160
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == 40

    assert artisans.class_overpopulation == 0


def test_move_population_in_not_enough_resources():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 70,
        "iron": 200,
        "stone": 0,
        "tools": 200
    }
    artisans = Artisans(state, 80, resources)

    artisans.move_population(50, True)

    assert artisans.population == 130

    assert artisans.resources["food"] == 100
    assert artisans.resources["wood"] == -30
    assert artisans.resources["iron"] == 100
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == 50

    assert artisans.class_overpopulation == 15


def test_move_population_out_no_demotion():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 120,
        "iron": 0,
        "stone": 0,
        "tools": 200
    }
    artisans = Artisans(state, 80, resources)

    artisans.move_population(-20)

    assert artisans.population == 60

    assert artisans.resources["food"] == 100
    assert artisans.resources["wood"] == 120
    assert artisans.resources["iron"] == 0
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == 200

    assert artisans.class_overpopulation == 0


def test_move_population_out_demotion():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 120,
        "iron": 0,
        "stone": 0,
        "tools": 200
    }
    artisans = Artisans(state, 80, resources)

    artisans.move_population(-20, True)

    assert artisans.population == 60

    assert artisans.resources["food"] == 100
    assert artisans.resources["wood"] == 160
    assert artisans.resources["iron"] == 0
    assert artisans.resources["stone"] == 0
    assert artisans.resources["tools"] == 260

    assert artisans.class_overpopulation == 0
