from pytest import raises

from ..sources.auxiliaries.constants import (FOOD_CONSUMPTION,
                                             INBUILT_RESOURCES,
                                             WOOD_CONSUMPTION)
from ..sources.auxiliaries.enums import Class_Name, Month, Resource
from ..sources.auxiliaries.resources import Resources
from ..sources.state.social_classes.class_file import ValidationError
from ..sources.state.social_classes.nobles import Nobles
from ..sources.state.state_data import State_Data


def test_constructor():
    state = State_Data()
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.tools: 100
    })
    nobles = Nobles(state, 80, resources)

    assert nobles.parent is state
    assert nobles.population == 80

    assert nobles.resources.food == 100
    assert nobles.resources.wood == 200
    assert nobles.resources.iron == 0
    assert nobles.resources.stone == 0
    assert nobles.resources.tools == 100
    assert nobles.resources.land == 0

    assert not nobles.starving
    assert not nobles.freezing
    assert not nobles.demoted_from
    assert not nobles.demoted_to
    assert not nobles.promoted_from
    assert not nobles.promoted_to

    assert nobles.employees == 0
    assert nobles.old_wage == state.sm.others_minimum_wage

    assert nobles.happiness == 0

    with raises(ValueError):
        Nobles(state, -1)
    with raises(ValueError):
        Nobles(state, resources=Resources({Resource.food: -1}))


def test_default_constructor():
    state = State_Data()
    nobles = Nobles(state, 200)

    assert nobles.parent is state
    assert nobles.population == 200

    assert nobles.resources.food == 0
    assert nobles.resources.wood == 0
    assert nobles.resources.iron == 0
    assert nobles.resources.stone == 0
    assert nobles.resources.tools == 0
    assert nobles.resources.land == 0

    assert not nobles.starving
    assert not nobles.freezing
    assert not nobles.demoted_from
    assert not nobles.demoted_to
    assert not nobles.promoted_from
    assert not nobles.promoted_to

    assert nobles.employees == 0
    assert nobles.old_wage == state.sm.others_minimum_wage

    assert nobles.happiness == 0


def test_class_name():
    state = State_Data()
    nobles = Nobles(state, 200)
    assert nobles.class_name == Class_Name.nobles


def test_population():
    state = State_Data()
    resources = Resources({
        Resource.food: 200,
        Resource.wood: 300,
        Resource.iron: 400,
        Resource.land: 500,
    })
    nobles = Nobles(state, 200, resources)

    nobles.population += 40
    assert nobles.resources == \
        resources - INBUILT_RESOURCES[Class_Name.nobles] * 40

    nobles.population = 150
    assert nobles.resources == \
        resources + INBUILT_RESOURCES[Class_Name.nobles] * 50

    nobles.population = 500
    assert nobles.resources == \
        resources - INBUILT_RESOURCES[Class_Name.nobles] * 300


def test_employable():
    state = State_Data()
    nobles = Nobles(state, 200)
    assert not nobles.employable


def test_real_resources():
    state = State_Data()
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.tools: 100
    })
    nobles = Nobles(state, 80, resources)
    assert nobles.real_resources == \
        INBUILT_RESOURCES[Class_Name.nobles] * 80 + resources


def test_optimal_resources():
    state = State_Data.generate_empty_state()
    state.nobles.population = 50
    assert state.nobles.optimal_resources == \
        state.sm.optimal_resources[Class_Name.nobles] * 50


def test_missing_resources():
    state = State_Data()
    nobles = Nobles(state, 200)
    assert nobles.missing_resources == {}

    nobles.resources = Resources({
        Resource.food: 234,
        Resource.wood: 23,
        Resource.stone: -1,
        Resource.land: -200
    })
    assert nobles.missing_resources == {
        Resource.stone: 1,
        Resource.land: 200
    }


def test_class_overpopulation_1():
    state = State_Data.generate_empty_state()
    resources = Resources({
        Resource.food: 200,
        Resource.wood: -500,
        Resource.stone: -20,
        Resource.tools: 1200
    })
    missing_wood = 500
    missing_stone = 20

    state.nobles.resources = resources

    inbuilt_wood = INBUILT_RESOURCES[Class_Name.nobles][Resource.wood] - \
        INBUILT_RESOURCES[Class_Name.peasants][Resource.wood]
    inbuilt_stone = INBUILT_RESOURCES[Class_Name.nobles][Resource.stone] - \
        INBUILT_RESOURCES[Class_Name.peasants][Resource.stone]

    overpop = max(missing_wood / inbuilt_wood, missing_stone / inbuilt_stone)

    assert state.nobles.class_overpopulation == overpop


def test_class_overpopulation_2():
    state = State_Data.generate_empty_state()
    state.others.population = 500

    resources = Resources({
        Resource.food: 200,
        Resource.wood: -50,
        Resource.stone: -200,
        Resource.tools: 1200
    })
    missing_wood = 50
    missing_stone = 200

    state.nobles.resources = resources

    inbuilt_wood = INBUILT_RESOURCES[Class_Name.nobles][Resource.wood] - \
        INBUILT_RESOURCES[Class_Name.peasants][Resource.wood]
    inbuilt_stone = INBUILT_RESOURCES[Class_Name.nobles][Resource.stone] - \
        INBUILT_RESOURCES[Class_Name.peasants][Resource.stone]

    overpop = max(missing_wood / inbuilt_wood, missing_stone / inbuilt_stone)

    assert state.nobles.class_overpopulation == overpop


def test_class_overpopulation_3():
    state = State_Data.generate_empty_state()
    state.others.population = 500

    resources = Resources({
        Resource.food: 200,
        Resource.wood: 500,
        Resource.stone: 20,
        Resource.iron: 0,
        Resource.tools: 100,
        Resource.land: 0
    })

    state.nobles.resources = resources

    assert state.nobles.class_overpopulation == 0


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
    nobles = Nobles(state, 80, resources)

    nobles.grow_population(0.25)
    assert nobles.population == 100
    assert nobles.resources == \
        resources - INBUILT_RESOURCES[Class_Name.nobles] * 20


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
    nobles = Nobles(state, 80, resources)

    nobles.grow_population(0.625)
    assert nobles.population == 130
    assert nobles.resources == \
        resources - INBUILT_RESOURCES[Class_Name.nobles] * 50


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
        (INBUILT_RESOURCES[Class_Name.nobles] * state.prices * 20).values()
    )
    nobles = Nobles(state, 20, resources)
    assert nobles.net_worth == 234567 + inbuilt_worth


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
    nobles = Nobles(state, 50, resources)

    emps = 10 + INBUILT_RESOURCES[Class_Name.nobles][Resource.land] * 5

    assert nobles.max_employees == emps


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
    nobles = Nobles(state, 50, resources)

    assert nobles.max_employees == 100


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
    nobles = Nobles(state, 80, resources)
    nobles.consume()

    consumed = Resources({
        Resource.food: FOOD_CONSUMPTION * 80,
        Resource.wood: WOOD_CONSUMPTION[Month.January] * 80
    })

    assert nobles.resources == resources - consumed
    assert nobles.missing_resources == {}


def test_produce():
    state = State_Data()
    nobles = Nobles(state, 200)
    nobles.produce()
    assert nobles.population == 200
    assert nobles.resources == {}
    assert nobles.happiness == 0


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
    nobles = Nobles(state, 80, resources)
    nobles.population += 20
    nobles.happiness = -20
    nobles.freezing = True
    nobles.promoted_to = True

    dicted = nobles.to_dict()
    assert dicted == {
        "population": 100,
        "resources":
        (resources - INBUILT_RESOURCES[Class_Name.nobles] * 20).to_raw_dict(),
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
    nobles = Nobles.from_dict(state, dicted)

    assert nobles.parent is state
    assert nobles.population == 80
    assert nobles.resources == resources
    assert nobles.starving is False
    assert nobles.freezing is True
    assert nobles.demoted_from is False
    assert nobles.demoted_to is False
    assert nobles.promoted_from is False
    assert nobles.promoted_to is True
    assert nobles.happiness == -20


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

    state.nobles.resources = resources.copy()
    state.nobles._population = 0.3  # type: ignore

    state.nobles.handle_empty_class()
    assert state.nobles.population == 0
    assert state.nobles.resources == {}
    assert state.government.resources == \
        resources + INBUILT_RESOURCES[Class_Name.nobles] * 0.3


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

    state.nobles.resources = resources.copy()
    state.nobles._population = 0.5  # type: ignore

    state.nobles.handle_empty_class()
    assert state.nobles.population == 0.5
    assert state.nobles.resources == resources
    assert state.government.resources == {}


def test_validate():
    state = State_Data()
    nobles = Nobles(state, 5)

    nobles.resources = Resources({
        Resource.food: 100,
        Resource.wood: -0.00001,
        Resource.iron: -0.000099999,
        Resource.tools: 0.00001,
    })

    nobles.validate()
    assert nobles.resources == {
        Resource.food: 100,
        Resource.tools: 0.00001
    }

    nobles.resources = Resources({
        Resource.food: 100,
        Resource.wood: -0.0001,
        Resource.iron: -0.000099999,
        Resource.tools: 0.00001,
    })
    with raises(ValidationError):
        nobles.validate()

    nobles.resources = Resources({
        Resource.food: -100,
        Resource.iron: -0.000099999,
        Resource.tools: -100,
    })
    with raises(ValidationError):
        nobles.validate()


def test_decay_happiness():
    state = State_Data()
    nobles = Nobles(state, 80)
    nobles.happiness = 20
    nobles.decay_happiness()
    assert nobles.happiness == 16

    nobles.happiness = -20
    nobles.decay_happiness()
    assert nobles.happiness == -16

    nobles.happiness = 0
    nobles.decay_happiness()
    assert nobles.happiness == 0

    nobles.happiness = 0.6
    nobles.decay_happiness()
    assert nobles.happiness == 0

    nobles.happiness = -0.6
    nobles.decay_happiness()
    assert nobles.happiness == 0
