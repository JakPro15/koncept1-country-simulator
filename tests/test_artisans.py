from pytest import raises

from ..sources.auxiliaries.constants import (FOOD_CONSUMPTION,
                                             INBUILT_RESOURCES,
                                             OTHERS_MINIMUM_WAGE,
                                             WOOD_CONSUMPTION)
from ..sources.auxiliaries.enums import Class_Name, Month, Resource
from ..sources.auxiliaries.resources import Resources
from ..sources.state.social_classes.artisans import Artisans
from ..sources.state.social_classes.class_file import ValidationError
from ..sources.state.state_data import State_Data


def test_constructor():
    state = State_Data()
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.tools: 100
    })
    artisans = Artisans(state, 80, resources)

    assert artisans.parent == state
    assert artisans.population == 80

    assert artisans.resources.food == 100
    assert artisans.resources.wood == 200
    assert artisans.resources.iron == 0
    assert artisans.resources.stone == 0
    assert artisans.resources.tools == 100
    assert artisans.resources.land == 0

    assert not artisans.starving
    assert not artisans.freezing
    assert not artisans.demoted_from
    assert not artisans.demoted_to
    assert not artisans.promoted_from
    assert not artisans.promoted_to

    assert artisans.employees == 0
    assert artisans.old_wage == OTHERS_MINIMUM_WAGE

    assert artisans.happiness == 0

    with raises(ValueError):
        Artisans(state, -1)
    with raises(ValueError):
        Artisans(state, resources=Resources({Resource.food: -1}))


def test_default_constructor():
    state = State_Data()
    artisans = Artisans(state, 200)

    assert artisans.parent == state
    assert artisans.population == 200

    assert artisans.resources.food == 0
    assert artisans.resources.wood == 0
    assert artisans.resources.iron == 0
    assert artisans.resources.stone == 0
    assert artisans.resources.tools == 0
    assert artisans.resources.land == 0

    assert not artisans.starving
    assert not artisans.freezing
    assert not artisans.demoted_from
    assert not artisans.demoted_to
    assert not artisans.promoted_from
    assert not artisans.promoted_to

    assert artisans.employees == 0
    assert artisans.old_wage == OTHERS_MINIMUM_WAGE

    assert artisans.happiness == 0


def test_class_name():
    state = State_Data()
    artisans = Artisans(state, 200)
    assert artisans.class_name == Class_Name.artisans


def test_population():
    state = State_Data()
    resources = Resources({
        Resource.food: 200,
        Resource.wood: 300,
        Resource.iron: 400,
        Resource.land: 500,
    })
    artisans = Artisans(state, 200, resources)

    artisans.population += 40
    assert artisans.resources == \
        resources - INBUILT_RESOURCES[Class_Name.artisans] * 40

    artisans.population = 150
    assert artisans.resources == \
        resources + INBUILT_RESOURCES[Class_Name.artisans] * 50

    artisans.population = 500
    assert artisans.resources == \
        resources - INBUILT_RESOURCES[Class_Name.artisans] * 300


def test_employable():
    state = State_Data()
    artisans = Artisans(state, 200)
    assert not artisans.employable


def test_real_resources():
    state = State_Data()
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.tools: 100
    })
    artisans = Artisans(state, 80, resources)
    assert artisans.real_resources == \
        INBUILT_RESOURCES[Class_Name.artisans] * 80 + resources


def test_optimal_resources():
    state = State_Data.generate_empty_state()
    state.classes[Class_Name.artisans].population = 50
    assert state.classes[Class_Name.artisans].optimal_resources == \
        state.sm.optimal_resources[Class_Name.artisans] * 50


def test_missing_resources():
    state = State_Data()
    artisans = Artisans(state, 200)
    assert artisans.missing_resources == {}

    artisans.resources = Resources({
        Resource.food: 234,
        Resource.wood: 23,
        Resource.stone: -1,
        Resource.land: -200
    })
    assert artisans.missing_resources == {
        Resource.stone: 1,
        Resource.land: 200
    }


def test_class_overpopulation_1():
    state = State_Data.generate_empty_state()
    artisans = state.classes[Class_Name.artisans]

    resources = Resources({
        Resource.food: 200,
        Resource.wood: -500,
        Resource.iron: -20,
        Resource.tools: 1200
    })
    missing_wood = 500
    missing_iron = 20

    artisans.resources = resources

    inbuilt_wood = INBUILT_RESOURCES[Class_Name.artisans][Resource.wood] - \
        INBUILT_RESOURCES[Class_Name.others][Resource.wood]
    inbuilt_iron = INBUILT_RESOURCES[Class_Name.artisans][Resource.iron] - \
        INBUILT_RESOURCES[Class_Name.others][Resource.iron]

    overpop = max(missing_wood / inbuilt_wood, missing_iron / inbuilt_iron)

    assert artisans.class_overpopulation == overpop


def test_class_overpopulation_2():
    state = State_Data.generate_empty_state()
    artisans = state.classes[Class_Name.artisans]

    resources = Resources({
        Resource.food: 200,
        Resource.wood: -50,
        Resource.iron: -200,
        Resource.tools: 1200
    })
    missing_wood = 50
    missing_iron = 200

    artisans.resources = resources

    inbuilt_wood = INBUILT_RESOURCES[Class_Name.artisans][Resource.wood] - \
        INBUILT_RESOURCES[Class_Name.others][Resource.wood]
    inbuilt_iron = INBUILT_RESOURCES[Class_Name.artisans][Resource.iron] - \
        INBUILT_RESOURCES[Class_Name.others][Resource.iron]

    overpop = max(missing_wood / inbuilt_wood, missing_iron / inbuilt_iron)

    assert artisans.class_overpopulation == overpop


def test_class_overpopulation_3():
    state = State_Data.generate_empty_state()
    artisans = state.classes[Class_Name.artisans]

    resources = Resources({
        Resource.food: 200,
        Resource.wood: 500,
        Resource.stone: 20,
        Resource.iron: 0,
        Resource.tools: 100,
        Resource.land: 0
    })

    artisans.resources = resources

    assert artisans.class_overpopulation == 0


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
    artisans = Artisans(state, 80, resources)

    artisans.grow_population(0.25)
    assert artisans.population == 100
    assert artisans.resources == \
        resources - INBUILT_RESOURCES[Class_Name.artisans] * 20


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
    artisans = Artisans(state, 80, resources)

    artisans.grow_population(0.625)
    assert artisans.population == 130
    assert artisans.resources == \
        resources - INBUILT_RESOURCES[Class_Name.artisans] * 50


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
        (INBUILT_RESOURCES[Class_Name.artisans] * state.prices * 20).values()
    )
    artisans = Artisans(state, 20, resources)
    assert artisans.net_worth == 234567 + inbuilt_worth


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
    artisans = Artisans(state, 50, resources)

    emps = 10 + INBUILT_RESOURCES[Class_Name.artisans][Resource.land] * 5

    assert artisans.max_employees == emps


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
    artisans = Artisans(state, 50, resources)

    assert artisans.max_employees == 100


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
    artisans = Artisans(state, 80, resources)
    artisans.consume()

    consumed = Resources({
        Resource.food: FOOD_CONSUMPTION * 80,
        Resource.wood: WOOD_CONSUMPTION[Month.January] * 80
    })

    assert artisans.resources == resources - consumed
    assert artisans.missing_resources == {}


def test_produce():
    state = State_Data()
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.iron: 0,
        Resource.stone: 0,
        Resource.tools: 100,
        Resource.land: 0
    })
    artisans = Artisans(state, 200, resources)
    artisans.produce()

    resources.tools += \
        (state.sm.tools_production - state.sm.artisan_tool_usage) * 200
    resources.wood -= state.sm.artisan_wood_usage * 200
    resources.iron -= state.sm.artisan_iron_usage * 200

    assert artisans.population == 200
    assert artisans.resources == resources
    assert artisans.happiness == 0


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
    artisans = Artisans(state, 80, resources)
    artisans.population += 20
    artisans.happiness = -20
    artisans.freezing = True
    artisans.promoted_to = True

    dicted = artisans.to_dict()
    assert dicted == {
        "population": 100,
        "resources": (resources - INBUILT_RESOURCES[Class_Name.artisans]
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
    artisans = Artisans.from_dict(state, dicted)

    assert artisans.parent == state
    assert artisans.population == 80
    assert artisans.resources == resources
    assert artisans.starving is False
    assert artisans.freezing is True
    assert artisans.demoted_from is False
    assert artisans.demoted_to is False
    assert artisans.promoted_from is False
    assert artisans.promoted_to is True
    assert artisans.happiness == -20


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
    artisans = state.classes[Class_Name.artisans]

    artisans.resources = resources.copy()
    artisans._population = 0.3  # type: ignore

    artisans.handle_empty_class()
    assert artisans.population == 0
    assert artisans.resources == {}
    assert state.government.resources == \
        resources + INBUILT_RESOURCES[Class_Name.artisans] * 0.3


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
    artisans = state.classes[Class_Name.artisans]

    artisans.resources = resources.copy()
    artisans._population = 0.5  # type: ignore

    artisans.handle_empty_class()
    assert artisans.population == 0.5
    assert artisans.resources == resources
    assert state.government.resources == {}


def test_validate():
    state = State_Data()
    artisans = Artisans(state, 5)

    artisans.resources = Resources({
        Resource.food: 100,
        Resource.wood: -0.00001,
        Resource.iron: -0.000099999,
        Resource.tools: 0.00001,
    })

    artisans.validate()
    assert artisans.resources == {
        Resource.food: 100,
        Resource.tools: 0.00001
    }

    artisans.resources = Resources({
        Resource.food: 100,
        Resource.wood: -0.0001,
        Resource.iron: -0.000099999,
        Resource.tools: 0.00001,
    })
    with raises(ValidationError):
        artisans.validate()

    artisans.resources = Resources({
        Resource.food: -100,
        Resource.iron: -0.000099999,
        Resource.tools: -100,
    })
    with raises(ValidationError):
        artisans.validate()


def test_decay_happiness():
    state = State_Data()
    artisans = Artisans(state, 80)
    artisans.happiness = 20
    artisans.decay_happiness()
    assert artisans.happiness == 16

    artisans.happiness = -20
    artisans.decay_happiness()
    assert artisans.happiness == -16

    artisans.happiness = 0
    artisans.decay_happiness()
    assert artisans.happiness == 0

    artisans.happiness = 0.6
    artisans.decay_happiness()
    assert artisans.happiness == 0

    artisans.happiness = -0.6
    artisans.decay_happiness()
    assert artisans.happiness == 0
