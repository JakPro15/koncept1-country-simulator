from pytest import raises

from ..sources.auxiliaries.constants import (DEFAULT_PRICES, FOOD_CONSUMPTION,
                                             INBUILT_RESOURCES,
                                             OTHERS_MINIMUM_WAGE,
                                             WOOD_CONSUMPTION)
from ..sources.auxiliaries.enums import Class_Name, Month, Resource
from ..sources.auxiliaries.resources import Resources
from ..sources.state.social_classes.peasants import Peasants
from ..sources.state.social_classes.class_file import ValidationError
from ..sources.state.state_data import State_Data


def test_constructor():
    state = State_Data()
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.tools: 100
    })
    peasants = Peasants(state, 80, resources)

    assert peasants.parent == state
    assert peasants.population == 80

    assert peasants.resources.food == 100
    assert peasants.resources.wood == 200
    assert peasants.resources.iron == 0
    assert peasants.resources.stone == 0
    assert peasants.resources.tools == 100
    assert peasants.resources.land == 0

    assert not peasants.starving
    assert not peasants.freezing
    assert not peasants.demoted_from
    assert not peasants.demoted_to
    assert not peasants.promoted_from
    assert not peasants.promoted_to

    assert peasants.employees == 0
    assert peasants.old_wage == OTHERS_MINIMUM_WAGE

    assert peasants.happiness == 0

    with raises(ValueError):
        Peasants(state, -1)
    with raises(ValueError):
        Peasants(state, resources=Resources({Resource.food: -1}))


def test_default_constructor():
    state = State_Data()
    peasants = Peasants(state, 200)

    assert peasants.parent == state
    assert peasants.population == 200

    assert peasants.resources.food == 0
    assert peasants.resources.wood == 0
    assert peasants.resources.iron == 0
    assert peasants.resources.stone == 0
    assert peasants.resources.tools == 0
    assert peasants.resources.land == 0

    assert not peasants.starving
    assert not peasants.freezing
    assert not peasants.demoted_from
    assert not peasants.demoted_to
    assert not peasants.promoted_from
    assert not peasants.promoted_to

    assert peasants.employees == 0
    assert peasants.old_wage == OTHERS_MINIMUM_WAGE

    assert peasants.happiness == 0


def test_class_name():
    state = State_Data()
    peasants = Peasants(state, 200)
    assert peasants.class_name == Class_Name.peasants


def test_population():
    state = State_Data()
    resources = Resources({
        Resource.food: 200,
        Resource.wood: 300,
        Resource.iron: 400,
        Resource.land: 500,
    })
    peasants = Peasants(state, 200, resources)

    peasants.population += 40
    assert peasants.resources == \
        resources - INBUILT_RESOURCES[Class_Name.peasants] * 40

    peasants.population = 150
    assert peasants.resources == \
        resources + INBUILT_RESOURCES[Class_Name.peasants] * 50

    peasants.population = 500
    assert peasants.resources == \
        resources - INBUILT_RESOURCES[Class_Name.peasants] * 300


def test_employable():
    state = State_Data()
    peasants = Peasants(state, 200)
    assert not peasants.employable


def test_real_resources():
    state = State_Data()
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.tools: 100
    })
    peasants = Peasants(state, 80, resources)
    assert peasants.real_resources == \
        INBUILT_RESOURCES[Class_Name.peasants] * 80 + resources


def test_optimal_resources():
    state = State_Data.generate_empty_state()
    state.classes[Class_Name.peasants].population = 50
    assert state.classes[Class_Name.peasants].optimal_resources == \
        state.sm.optimal_resources[Class_Name.peasants] * 50


def test_missing_resources():
    state = State_Data()
    peasants = Peasants(state, 200)
    assert peasants.missing_resources == {}

    peasants.resources = Resources({
        Resource.food: 234,
        Resource.wood: 23,
        Resource.stone: -1,
        Resource.land: -200
    })
    assert peasants.missing_resources == {
        Resource.stone: 1,
        Resource.land: 200
    }


def test_class_overpopulation_1():
    state = State_Data.generate_empty_state()
    peasants = state.classes[Class_Name.peasants]

    resources = Resources({
        Resource.food: 200,
        Resource.wood: -500,
        Resource.land: -20,
        Resource.tools: 1200
    })
    missing_wood = 500
    missing_land = 20

    peasants.resources = resources

    inbuilt_wood = INBUILT_RESOURCES[Class_Name.peasants][Resource.wood] - \
        INBUILT_RESOURCES[Class_Name.others][Resource.wood]
    inbuilt_land = INBUILT_RESOURCES[Class_Name.peasants][Resource.land] - \
        INBUILT_RESOURCES[Class_Name.others][Resource.land]

    overpop = max(missing_wood / inbuilt_wood, missing_land / inbuilt_land)

    assert peasants.class_overpopulation == overpop


def test_class_overpopulation_2():
    state = State_Data.generate_empty_state()
    peasants = state.classes[Class_Name.peasants]

    resources = Resources({
        Resource.food: 200,
        Resource.wood: -50,
        Resource.land: -200,
        Resource.tools: 1200
    })
    missing_wood = 50
    missing_land = 200

    peasants.resources = resources

    inbuilt_wood = INBUILT_RESOURCES[Class_Name.peasants][Resource.wood] - \
        INBUILT_RESOURCES[Class_Name.others][Resource.wood]
    inbuilt_land = INBUILT_RESOURCES[Class_Name.peasants][Resource.land] - \
        INBUILT_RESOURCES[Class_Name.others][Resource.land]

    overpop = max(missing_wood / inbuilt_wood, missing_land / inbuilt_land)

    assert peasants.class_overpopulation == overpop


def test_class_overpopulation_3():
    state = State_Data.generate_empty_state()
    peasants = state.classes[Class_Name.peasants]

    resources = Resources({
        Resource.food: 200,
        Resource.wood: 500,
        Resource.stone: 20,
        Resource.iron: 0,
        Resource.tools: 100,
        Resource.land: 0
    })

    peasants.resources = resources

    assert peasants.class_overpopulation == 0


def test_grow_population_1():
    state = State_Data()
    resources = Resources({
        Resource.food: 1000,
        Resource.wood: 200,
        Resource.iron: 0,
        Resource.stone: 100,
        Resource.tools: 100,
        Resource.land: 0
    })
    peasants = Peasants(state, 80, resources)

    peasants.grow_population(0.25)
    assert peasants.population == 100
    assert peasants.resources == \
        resources - INBUILT_RESOURCES[Class_Name.peasants] * 20


def test_grow_population_2():
    state = State_Data()
    resources = Resources({
        Resource.food: 1000,
        Resource.wood: 20000,
        Resource.iron: 0,
        Resource.stone: 120,
        Resource.tools: 1000,
        Resource.land: 0
    })
    peasants = Peasants(state, 80, resources)

    peasants.grow_population(0.625)
    assert peasants.population == 130
    assert peasants.resources == \
        resources - INBUILT_RESOURCES[Class_Name.peasants] * 50


def test_net_worth():
    state = State_Data()
    state.prices = Resources({
        Resource.food: 2,
        Resource.wood: 3,
        Resource.stone: 4,
        Resource.iron: 5,
        Resource.tools: 6,
        Resource.land: 7
    })
    resources = Resources({
        Resource.food: 100000,
        Resource.wood: 10000,
        Resource.stone: 1000,
        Resource.iron: 100,
        Resource.tools: 10,
        Resource.land: 1
    })
    inbuilt_worth = sum(
        (INBUILT_RESOURCES[Class_Name.peasants] * state.prices * 20).values()
    )
    peasants = Peasants(state, 20, resources)
    assert peasants.net_worth == 234567 + inbuilt_worth


def test_max_employees_from_land():
    state = State_Data()
    state.sm.worker_land_usage = 10
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.iron: 0,
        Resource.stone: 0,
        Resource.tools: 1000000,
        Resource.land: 100
    })
    peasants = Peasants(state, 50, resources)

    emps = 10 + INBUILT_RESOURCES[Class_Name.peasants][Resource.land] * 5

    assert peasants.max_employees == max(emps - 50, 0)


def test_max_employees_from_tools():
    state = State_Data()
    state.sm.worker_land_usage = 10
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.iron: 0,
        Resource.stone: 0,
        Resource.tools: 300,
        Resource.land: 1000000
    })
    peasants = Peasants(state, 50, resources)

    assert peasants.max_employees == 50


def test_consume():
    state = State_Data()
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.iron: 0,
        Resource.stone: 0,
        Resource.tools: 100,
        Resource.land: 0
    })
    peasants = Peasants(state, 80, resources)
    peasants.consume()

    consumed = Resources({
        Resource.food: FOOD_CONSUMPTION * 80,
        Resource.wood: WOOD_CONSUMPTION[Month.January] * 80
    })

    assert peasants.resources == resources - consumed
    assert peasants.missing_resources == {}


def test_produce():
    state = State_Data(Month.July)
    state.prices = Resources({
        Resource.food: 2,
        Resource.wood: 3
    }) * DEFAULT_PRICES
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.iron: 0,
        Resource.stone: 0,
        Resource.tools: 100,
        Resource.land: 0
    })
    peasants = Peasants(state, 200, resources)
    peasants.produce()

    resources.tools -= state.sm.peasant_tool_usage * 200
    resources.food += state.sm.food_production[Month.July] * 80
    resources.wood += state.sm.wood_production * 120

    assert peasants.population == 200
    assert peasants.resources == resources
    assert peasants.happiness == 0


def test_to_dict():
    state = State_Data()
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.iron: 0,
        Resource.stone: 0,
        Resource.tools: 100,
        Resource.land: 0
    })
    peasants = Peasants(state, 80, resources)
    peasants.population += 20
    peasants.happiness = -20
    peasants.freezing = True
    peasants.promoted_to = True

    dicted = peasants.to_dict()
    assert dicted == {
        "population": 100,
        "resources": (resources - INBUILT_RESOURCES[Class_Name.peasants]
                      * 20).to_raw_dict(),
        "starving": False,
        "freezing": True,
        "demoted_from": False,
        "demoted_to": False,
        "promoted_from": False,
        "promoted_to": True,
        "happiness": -20
    }


def test_from_dict():
    state = State_Data()
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.iron: 0,
        Resource.stone: 0,
        Resource.tools: 100,
        Resource.land: 0
    })
    dicted = {
        "population": 80,
        "resources": resources.to_raw_dict(),
        "starving": False,
        "freezing": True,
        "demoted_from": False,
        "demoted_to": False,
        "promoted_from": False,
        "promoted_to": True,
        "happiness": -20
    }
    peasants = Peasants.from_dict(state, dicted)

    assert peasants.parent == state
    assert peasants.population == 80
    assert peasants.resources == resources
    assert peasants.starving is False
    assert peasants.freezing is True
    assert peasants.demoted_from is False
    assert peasants.demoted_to is False
    assert peasants.promoted_from is False
    assert peasants.promoted_to is True
    assert peasants.happiness == -20


def test_handle_empty_class_emptying():
    state = State_Data.generate_empty_state()
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.iron: 0,
        Resource.stone: 0,
        Resource.tools: 100,
        Resource.land: 0
    })
    peasants = state.classes[Class_Name.peasants]

    peasants.resources = resources.copy()
    peasants._population = 0.3  # type: ignore

    peasants.handle_empty_class()
    assert peasants.population == 0
    assert peasants.resources == {}
    assert state.government.resources == \
        resources + INBUILT_RESOURCES[Class_Name.peasants] * 0.3


def test_handle_empty_class_not_emptying():
    state = State_Data.generate_empty_state()
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.iron: 0,
        Resource.stone: 0,
        Resource.tools: 100,
        Resource.land: 0
    })
    peasants = state.classes[Class_Name.peasants]

    peasants.resources = resources.copy()
    peasants._population = 0.5  # type: ignore

    peasants.handle_empty_class()
    assert peasants.population == 0.5
    assert peasants.resources == resources
    assert state.government.resources == {}


def test_validate():
    state = State_Data()
    peasants = Peasants(state, 5)

    peasants.resources = Resources({
        Resource.food: 100,
        Resource.wood: -0.00001,
        Resource.iron: -0.000099999,
        Resource.tools: 0.00001,
    })

    peasants.validate()
    assert peasants.resources == {
        Resource.food: 100,
        Resource.tools: 0.00001
    }

    peasants.resources = Resources({
        Resource.food: 100,
        Resource.wood: -0.0001,
        Resource.iron: -0.000099999,
        Resource.tools: 0.00001,
    })
    with raises(ValidationError):
        peasants.validate()

    peasants.resources = Resources({
        Resource.food: -100,
        Resource.iron: -0.000099999,
        Resource.tools: -100,
    })
    with raises(ValidationError):
        peasants.validate()


def test_decay_happiness():
    state = State_Data()
    peasants = Peasants(state, 80)
    peasants.happiness = 20
    peasants.decay_happiness()
    assert peasants.happiness == 16

    peasants.happiness = -20
    peasants.decay_happiness()
    assert peasants.happiness == -16

    peasants.happiness = 0
    peasants.decay_happiness()
    assert peasants.happiness == 0

    peasants.happiness = 0.6
    peasants.decay_happiness()
    assert peasants.happiness == 0

    peasants.happiness = -0.6
    peasants.decay_happiness()
    assert peasants.happiness == 0
