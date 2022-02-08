from ..classes.state_data import State_Data
from ..classes.others import Others
from pytest import raises


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
    others = Others(state, 80, resources, land)

    assert others.parent == state

    assert others.employable

    assert others.population == 80

    assert others.resources["food"] == 100
    assert others.resources["wood"] == 200
    assert others.resources["iron"] == 0
    assert others.resources["stone"] == 0
    assert others.resources["tools"] == 100

    assert others.land["fields"] == 0
    assert others.land["woods"] == 0
    assert others.land["stone_mines"] == 0
    assert others.land["iron_mines"] == 0

    assert others.missing_resources["food"] == 0
    assert others.missing_resources["wood"] == 0

    assert others.class_overpopulation == 0


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

    assert others.land["fields"] == 0
    assert others.land["woods"] == 0
    assert others.land["stone_mines"] == 0
    assert others.land["iron_mines"] == 0

    assert others.missing_resources["food"] == 0
    assert others.missing_resources["wood"] == 0

    assert others.class_overpopulation == 0


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
        Others(state, 80, resources, land)

    land = {
        "fields": 0,
        "woods": 30,
        "stone_mines": 0,
        "iron_mines": 0
    }
    with raises(AssertionError):
        Others(state, 80, resources, land)

    land = {
        "fields": 0,
        "woods": 0,
        "stone_mines": 3,
        "iron_mines": 0
    }
    with raises(AssertionError):
        Others(state, 80, resources, land)

    land = {
        "fields": 0,
        "woods": 0,
        "stone_mines": 0,
        "iron_mines": 1
    }
    with raises(AssertionError):
        Others(state, 80, resources, land)


def test_add_population():
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
    others = Others(state, 80, resources, land)

    others._add_population(20)
    assert others.resources["food"] == 100
    assert others.resources["wood"] == 200
    assert others.resources["iron"] == 0
    assert others.resources["stone"] == 0
    assert others.resources["tools"] == 100

    assert others.class_overpopulation == 0


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
        "fields": 0,
        "woods": 0,
        "stone_mines": 0,
        "iron_mines": 0
    }
    others = Others(state, 80, resources, land)

    others.grow_population(0.25)

    assert others.population == 100

    assert others.resources["food"] == 100
    assert others.resources["wood"] == 200
    assert others.resources["iron"] == 0
    assert others.resources["stone"] == 0
    assert others.resources["tools"] == 100

    assert others.class_overpopulation == 0


def test_optimal_resources_per_capita_february():
    state = State_Data("February")
    others = Others(state, 200)
    opt_res = others.optimal_resources_per_capita()
    assert opt_res["food"] == 4
    assert opt_res["wood"] == 2.4
    assert opt_res["iron"] == 0
    assert opt_res["stone"] == 0
    assert opt_res["tools"] == 0


def test_optimal_resources_per_capita_august():
    state = State_Data("August")
    others = Others(state, 200)
    opt_res = others.optimal_resources_per_capita()
    assert opt_res["food"] == 4
    assert opt_res["wood"] == 2.4
    assert opt_res["iron"] == 0
    assert opt_res["stone"] == 0
    assert opt_res["tools"] == 0


def test_calculate_optimal_resources_february():
    state = State_Data("February")
    others = Others(state, 200)
    opt_res = others.optimal_resources
    assert opt_res["food"] == 800
    assert opt_res["wood"] == 480
    assert opt_res["iron"] == 0
    assert opt_res["stone"] == 0
    assert opt_res["tools"] == 0


def test_calculate_optimal_resources_october():
    state = State_Data("October")
    others = Others(state, 100)
    opt_res = others.optimal_resources
    assert opt_res["food"] == 400
    assert opt_res["wood"] == 240
    assert opt_res["iron"] == 0
    assert opt_res["stone"] == 0
    assert opt_res["tools"] == 0


def test_produce():
    state = State_Data("March")
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
    others = Others(state, 60, resources, land)

    others.produce()
    assert others.resources["food"] == 100
    assert others.resources["wood"] == 200
    assert others.resources["iron"] == 0
    assert others.resources["stone"] == 0
    assert others.resources["tools"] == 100
    assert others.class_overpopulation == 0


def test_consume_enough_resources():
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
    assert others.resources["food"] == 20
    assert others.resources["wood"] == 152
    assert others.resources["iron"] == 0
    assert others.resources["stone"] == 0
    assert others.resources["tools"] == 100

    assert others.missing_resources["food"] == 0
    assert others.missing_resources["wood"] == 0


def test_consume_not_enough_food():
    state = State_Data()
    resources = {
        "food": 50,
        "wood": 100,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    others = Others(state, 80, resources)
    others.consume()
    assert others.resources["food"] == -30
    assert others.resources["wood"] == 52
    assert others.resources["iron"] == 0
    assert others.resources["stone"] == 0
    assert others.resources["tools"] == 100

    assert others.missing_resources["food"] == 30
    assert others.missing_resources["wood"] == 0


def test_consume_not_enough_wood():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 40,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    others = Others(state, 80, resources)
    others.consume()
    assert others.resources["food"] == 20
    assert others.resources["wood"] == -8
    assert others.resources["iron"] == 0
    assert others.resources["stone"] == 0
    assert others.resources["tools"] == 100

    assert others.missing_resources["food"] == 0
    assert others.missing_resources["wood"] == 8


def test_consume_not_enough_both():
    state = State_Data()
    resources = {
        "food": 50,
        "wood": 40,
        "iron": 0,
        "stone": 0,
        "tools": 100
    }
    others = Others(state, 80, resources)
    others.consume()
    assert others.resources["food"] == -30
    assert others.resources["wood"] == -8
    assert others.resources["iron"] == 0
    assert others.resources["stone"] == 0
    assert others.resources["tools"] == 100

    assert others.missing_resources["food"] == 30
    assert others.missing_resources["wood"] == 8


def test_move_population_in():
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
    others = Others(state, 80, resources, land)

    others.move_population(20)

    assert others.population == 100

    assert others.resources["food"] == 100
    assert others.resources["wood"] == 200
    assert others.resources["iron"] == 0
    assert others.resources["stone"] == 0
    assert others.resources["tools"] == 100

    assert others.class_overpopulation == 0


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
        "fields": 0,
        "woods": 0,
        "stone_mines": 0,
        "iron_mines": 0
    }
    others = Others(state, 80, resources, land)

    others.move_population(-20)

    assert others.population == 60

    assert others.resources["food"] == 100
    assert others.resources["wood"] == 120
    assert others.resources["iron"] == 0
    assert others.resources["stone"] == 0
    assert others.resources["tools"] == 200

    assert others.class_overpopulation == 0


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
        "fields": 0,
        "woods": 0,
        "stone_mines": 0,
        "iron_mines": 0
    }
    others = Others(state, 80, resources, land)

    others.move_population(-20, True)

    assert others.population == 60

    assert others.resources["food"] == 100
    assert others.resources["wood"] == 120
    assert others.resources["iron"] == 0
    assert others.resources["stone"] == 0
    assert others.resources["tools"] == 200

    assert others.class_overpopulation == 0
