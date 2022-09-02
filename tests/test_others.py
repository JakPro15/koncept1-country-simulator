from ..sources.auxiliaries.constants import (
    EMPTY_RESOURCES,
    FOOD_CONSUMPTION,
    INBUILT_RESOURCES,
    RESOURCE_NAMES,
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
        "tools": 100,
        "land": 0
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
    assert others.resources["land"] == 0

    assert others.missing_resources["food"] == 0
    assert others.missing_resources["wood"] == 0

    assert not others.is_temp
    assert others.temp["population"] == 0
    assert others.temp["resources"] == EMPTY_RESOURCES
    assert not others.starving
    assert not others.freezing

    assert others.happiness == 0
    assert others.happiness_plateau == 0


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
    assert others.resources["land"] == 0

    assert others.missing_resources["food"] == 0
    assert others.missing_resources["wood"] == 0

    assert not others.is_temp
    assert others.temp["population"] == 0
    assert others.temp["resources"] == EMPTY_RESOURCES
    assert not others.starving
    assert not others.freezing

    assert others.happiness == 0
    assert others.happiness_plateau == 0


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
        "tools": 100,
        "land": 0
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
        "tools": 100,
        "land": 0
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
        "tools": 100,
        "land": 0
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
        "tools": 1000,
        "land": 0
    }
    others = Others(state, 80, resources)

    others.grow_population(0.625)
    assert others._new_population == 130
    assert others._new_resources == \
        others.resources - INBUILT_RESOURCES["others"] * 50


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
    others = Others(state, 80, resources)
    opt_res = others.optimal_resources
    assert opt_res == state.sm.optimal_resources["others"] * 80


def test_missing_resources_1():
    state = State_Data("July")
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
    others = Others(state, 80)
    others.new_resources = resources
    assert others.missing_resources == missing


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
        "tools": -40,
        "land": 0
    }

    others = Others(state, 80)
    others.new_resources = resources
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
        "tools": 100,
        "land": 0
    }

    others = Others(state, 80, resources)
    others2 = Fake_Class()
    others.lower_class = others2

    assert others.class_overpopulation == 0


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
    resources2 = resources1 + INBUILT_RESOURCES["others"] * 80
    others = Others(state, 80, resources1)
    assert others.resources == resources1
    assert others.real_resources == resources2


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
        (INBUILT_RESOURCES["others"] * state.prices * 20).values()
    )
    others = Others(state, 20, resources)
    assert others.net_worth == 234567 + inbuilt_worth


def test_max_employees_from_land():
    state = State_Data()
    state.sm.worker_land_usage = 10
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 1000000,
        "land": 100
    }
    others = Others(state, 50, resources)

    emps = 10 + INBUILT_RESOURCES["others"]["land"] * 5

    assert others.max_employees == emps


def test_max_employees_from_tools():
    state = State_Data()
    state.sm.worker_land_usage = 10
    resources = {
        "food": 100,
        "wood": 200,
        "iron": 0,
        "stone": 0,
        "tools": 300,
        "land": 1000000
    }
    others = Others(state, 50, resources)

    assert others.max_employees == 100


def test_produce_january():
    state = State_Data()
    resources = Arithmetic_Dict({
        "food": 0,
        "wood": 400,
        "stone": 0,
        "iron": 400,
        "tools": 1200,
        "land": 0
    })
    others = Others(state, 80, resources)

    final_res = resources.copy()

    others.produce()
    for res in RESOURCE_NAMES:
        assert others._new_resources[res] == approx(final_res[res])


def test_produce_august():
    state = State_Data("August")
    resources = Arithmetic_Dict({
        "food": 0,
        "wood": 400,
        "stone": 0,
        "iron": 400,
        "tools": 1200,
        "land": 0
    })
    others = Others(state, 80, resources)

    final_res = resources.copy()

    others.produce()
    for res in RESOURCE_NAMES:
        assert others._new_resources[res] == approx(final_res[res])


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
        "tools": 100,
        "land": 0
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
        "tools": 100,
        "land": 0
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
        "tools": 100,
        "land": 0
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
        "tools": 100,
        "land": 0
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
        "tools": 100,
        "land": 0
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
        "tools": 0.0001,
        "land": 0
    })

    others.validate()
    assert others.new_resources == {
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
        "iron": 0,
        "stone": 100,
        "tools": 100,
        "land": 0
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
        "tools": 100,
        "land": 0
    })
    others.new_resources = resources
    with raises(Exception):
        others.flush()


def test_decay_happiness_no_plateau():
    state = State_Data()
    others = Others(state, 80)
    others.happiness = 20
    others.decay_happiness()
    assert 0 < others.happiness < 20

    others.happiness = -20
    others.decay_happiness()
    assert 0 > others.happiness > -20

    others.happiness = 0
    others.decay_happiness()
    assert others.happiness == 0


def test_decay_happiness_with_plateau():
    state = State_Data()
    others = Others(state, 80)
    others.happiness = 30
    others.happiness_plateau = 10
    others.decay_happiness()
    assert 10 < others.happiness < 30

    others.happiness = -10
    others.decay_happiness()
    assert 10 > others.happiness > -10

    others.happiness = 10
    others.decay_happiness()
    assert others.happiness == 10


def test_update_happiness_plateau():
    state = State_Data()
    others = Others(state, 80)

    others.starving = False
    others.freezing = True
    others.demoted_from = False
    others.demoted_to = True
    others.promoted_from = True
    others.promoted_to = False

    others.update_happiness_plateau()
    assert others.happiness_plateau == -20

    others.starving = True
    others.freezing = False
    others.demoted_from = False
    others.demoted_to = False
    others.promoted_from = True
    others.promoted_to = False

    others.update_happiness_plateau()
    assert others.happiness_plateau == -10

    others.starving = False
    others.freezing = False
    others.demoted_from = True
    others.demoted_to = False
    others.promoted_from = False
    others.promoted_to = True

    others.update_happiness_plateau()
    assert others.happiness_plateau == 0
