from pytest import raises

from ..sources.auxiliaries.constants import (FOOD_CONSUMPTION,
                                             INBUILT_RESOURCES,
                                             WOOD_CONSUMPTION)
from ..sources.auxiliaries.enums import Class_Name, Month, Resource
from ..sources.auxiliaries.resources import Resources
from ..sources.state.social_classes.others import Others
from ..sources.state.social_classes.class_file import ValidationError
from ..sources.state.state_data import State_Data


def test_constructor():
    state = State_Data()
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.tools: 100
    })
    others = Others(state, 80, resources)

    assert others.parent is state
    assert others.population == 80

    assert others.resources.food == 100
    assert others.resources.wood == 200
    assert others.resources.iron == 0
    assert others.resources.stone == 0
    assert others.resources.tools == 100
    assert others.resources.land == 0

    assert not others.starving
    assert not others.freezing
    assert not others.demoted_from
    assert not others.demoted_to
    assert not others.promoted_from
    assert not others.promoted_to

    assert others.employees == 0
    assert others.old_wage == state.sm.others_minimum_wage

    assert others.happiness == 0

    with raises(ValueError):
        Others(state, -1)
    with raises(ValueError):
        Others(state, resources=Resources({Resource.food: -1}))


def test_default_constructor():
    state = State_Data()
    others = Others(state, 200)

    assert others.parent is state
    assert others.population == 200

    assert others.resources.food == 0
    assert others.resources.wood == 0
    assert others.resources.iron == 0
    assert others.resources.stone == 0
    assert others.resources.tools == 0
    assert others.resources.land == 0

    assert not others.starving
    assert not others.freezing
    assert not others.demoted_from
    assert not others.demoted_to
    assert not others.promoted_from
    assert not others.promoted_to

    assert others.employees == 0
    assert others.old_wage == state.sm.others_minimum_wage

    assert others.happiness == 0


def test_class_name():
    state = State_Data()
    others = Others(state, 200)
    assert others.class_name == Class_Name.others


def test_population():
    state = State_Data()
    resources = Resources({
        Resource.food: 200,
        Resource.wood: 300,
        Resource.iron: 400,
        Resource.land: 500,
    })
    others = Others(state, 200, resources)

    others.population += 40
    assert others.resources == \
        resources - INBUILT_RESOURCES[Class_Name.others] * 40

    others.population = 150
    assert others.resources == \
        resources + INBUILT_RESOURCES[Class_Name.others] * 50

    others.population = 500
    assert others.resources == \
        resources - INBUILT_RESOURCES[Class_Name.others] * 300


def test_employable():
    state = State_Data()
    others = Others(state, 200)
    assert others.employable


def test_real_resources():
    state = State_Data()
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.tools: 100
    })
    others = Others(state, 80, resources)
    assert others.real_resources == \
        INBUILT_RESOURCES[Class_Name.others] * 80 + resources


def test_optimal_resources():
    state = State_Data.generate_empty_state()
    state.classes[Class_Name.others].population = 50
    assert state.classes[Class_Name.others].optimal_resources == \
        state.sm.optimal_resources[Class_Name.others] * 50


def test_missing_resources():
    state = State_Data()
    others = Others(state, 200)
    assert others.missing_resources == {}

    others.resources = Resources({
        Resource.food: 234,
        Resource.wood: 23,
        Resource.stone: -1,
        Resource.land: -200
    })
    assert others.missing_resources == {
        Resource.stone: 1,
        Resource.land: 200
    }


def test_class_overpopulation_1():
    state = State_Data.generate_empty_state()
    others = state.classes[Class_Name.others]

    resources = Resources({
        Resource.food: 200,
        Resource.wood: -500,
        Resource.iron: -20,
        Resource.tools: 1200
    })

    others.resources = resources

    assert others.class_overpopulation == 0


def test_class_overpopulation_2():
    state = State_Data.generate_empty_state()
    others = state.classes[Class_Name.others]

    resources = Resources({
        Resource.food: 200,
        Resource.wood: -50,
        Resource.stone: -200,
        Resource.tools: 1200
    })

    others.resources = resources

    assert others.class_overpopulation == 0


def test_class_overpopulation_3():
    state = State_Data.generate_empty_state()
    others = state.classes[Class_Name.others]

    resources = Resources({
        Resource.food: 200,
        Resource.wood: 500,
        Resource.stone: 20,
        Resource.iron: 0,
        Resource.tools: 100,
        Resource.land: 0
    })

    others.resources = resources

    assert others.class_overpopulation == 0


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
    others = Others(state, 80, resources)

    others.grow_population(0.25)
    assert others.population == 100
    assert others.resources == \
        resources - INBUILT_RESOURCES[Class_Name.others] * 20


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
    others = Others(state, 80, resources)

    others.grow_population(0.625)
    assert others.population == 130
    assert others.resources == \
        resources - INBUILT_RESOURCES[Class_Name.others] * 50


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
        (INBUILT_RESOURCES[Class_Name.others] * state.prices * 20).values()
    )
    others = Others(state, 20, resources)
    assert others.net_worth == 234567 + inbuilt_worth


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
    others = Others(state, 50, resources)

    emps = 10 + INBUILT_RESOURCES[Class_Name.others][Resource.land] * 5

    assert others.max_employees == emps


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
    others = Others(state, 50, resources)

    assert others.max_employees == 100


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
    others = Others(state, 80, resources)
    others.consume()

    consumed = Resources({
        Resource.food: FOOD_CONSUMPTION * 80,
        Resource.wood: WOOD_CONSUMPTION[Month.January] * 80
    })

    assert others.resources == resources - consumed
    assert others.missing_resources == {}


def test_produce():
    state = State_Data()
    others = Others(state, 200)
    others.produce()
    assert others.population == 200
    assert others.resources == {}
    assert others.happiness == 0


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
    others = Others(state, 80, resources)
    others.population += 20
    others.happiness = -20
    others.freezing = True
    others.promoted_to = True

    dicted = others.to_dict()
    assert dicted == {
        "population": 100,
        "resources": (resources - INBUILT_RESOURCES[Class_Name.others]
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
    others = Others.from_dict(state, dicted)

    assert others.parent is state
    assert others.population == 80
    assert others.resources == resources
    assert others.starving is False
    assert others.freezing is True
    assert others.demoted_from is False
    assert others.demoted_to is False
    assert others.promoted_from is False
    assert others.promoted_to is True
    assert others.happiness == -20


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
    others = state.classes[Class_Name.others]

    others.resources = resources.copy()
    others._population = 0.3  # type: ignore

    others.handle_empty_class()
    assert others.population == 0
    assert others.resources == {}
    assert state.government.resources == \
        resources + INBUILT_RESOURCES[Class_Name.others] * 0.3


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
    others = state.classes[Class_Name.others]

    others.resources = resources.copy()
    others._population = 0.5  # type: ignore

    others.handle_empty_class()
    assert others.population == 0.5
    assert others.resources == resources
    assert state.government.resources == {}


def test_validate():
    state = State_Data()
    others = Others(state, 5)

    others.resources = Resources({
        Resource.food: 100,
        Resource.wood: -0.00001,
        Resource.iron: -0.000099999,
        Resource.tools: 0.00001,
    })

    others.validate()
    assert others.resources == {
        Resource.food: 100,
        Resource.tools: 0.00001
    }

    others.resources = Resources({
        Resource.food: 100,
        Resource.wood: -0.0001,
        Resource.iron: -0.000099999,
        Resource.tools: 0.00001,
    })
    with raises(ValidationError):
        others.validate()

    others.resources = Resources({
        Resource.food: -100,
        Resource.iron: -0.000099999,
        Resource.tools: -100,
    })
    with raises(ValidationError):
        others.validate()


def test_decay_happiness():
    state = State_Data()
    others = Others(state, 80)
    others.happiness = 20
    others.decay_happiness()
    assert others.happiness == 16

    others.happiness = -20
    others.decay_happiness()
    assert others.happiness == -16

    others.happiness = 0
    others.decay_happiness()
    assert others.happiness == 0

    others.happiness = 0.6
    others.decay_happiness()
    assert others.happiness == 0

    others.happiness = -0.6
    others.decay_happiness()
    assert others.happiness == 0
