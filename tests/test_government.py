from ..sources.auxiliaries.constants import (
    KNIGHT_FOOD_CONSUMPTION
)
from ..sources.state.government import Government
from ..sources.state.state_data import State_Data
from ..sources.auxiliaries.resources import Resources
from ..sources.auxiliaries.soldiers import Soldiers
from ..sources.auxiliaries.enums import Resource, Soldier
from ..sources.state.social_classes.class_file import ValidationError
from pytest import raises


def test_constructor():
    state = State_Data()
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.tools: 100
    })
    soldiers = Soldiers({
        Soldier.knights: 10,
        Soldier.footmen: 50
    })
    govt = Government(state, resources, resources / 2, resources / 4, soldiers)

    assert govt.parent is state

    assert govt.resources == resources
    assert govt.secure_resources == resources / 4
    assert govt.optimal_resources == resources / 2

    assert govt.wage == state.sm.others_minimum_wage
    assert govt.wage_autoregulation is True

    assert govt.soldiers == soldiers

    assert govt.missing_food == 0
    assert govt.employees == 0
    assert govt.old_wage == state.sm.others_minimum_wage


def test_default_constructor():
    state = State_Data()
    govt = Government(state)

    assert govt.parent is state

    assert govt.resources == {}
    assert govt.secure_resources == {}
    assert govt.optimal_resources == {}

    assert govt.wage == state.sm.others_minimum_wage
    assert govt.wage_autoregulation is True

    assert govt.soldiers == {}

    assert govt.missing_food == 0
    assert govt.employees == 0
    assert govt.old_wage == state.sm.others_minimum_wage


def test_real_resources():
    state = State_Data()
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 200,
        Resource.iron: 0,
        Resource.stone: 0,
        Resource.tools: 100,
        Resource.land: 0
    })
    govt = Government(state, resources, resources / 2, resources / 4)
    assert govt.real_resources == resources * 1.25

    govt.resources = Resources()
    assert govt.real_resources == resources * 0.25

    govt.optimal_resources = Resources()
    assert govt.real_resources == resources * 0.25

    govt.secure_resources = Resources()
    assert govt.real_resources == {}


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
    govt = Government(state, resources)

    assert govt.max_employees == 10


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
    govt = Government(state, resources)

    assert govt.max_employees == 100


def test_soldier_revolt():
    state = State_Data()
    govt = Government(state)
    assert govt.soldier_revolt is False
    govt.missing_food = 2
    assert govt.soldier_revolt is True
    govt.missing_food = -2
    assert govt.soldier_revolt is False


def test_consume_typical():
    state = State_Data()
    res = Resources({
        Resource.food: 300,
        Resource.wood: 20,
        Resource.stone: 230,
        Resource.iron: 1,
        Resource.tools: 44,
        Resource.land: 234
    })
    govt = Government(state, res)
    govt.soldiers = Soldiers({
        Soldier.knights: 30,
        Soldier.footmen: 100
    })
    govt.consume()
    assert govt.resources == {
        Resource.food: 200 - 30 * KNIGHT_FOOD_CONSUMPTION,
        Resource.wood: 20,
        Resource.stone: 230,
        Resource.iron: 1,
        Resource.tools: 44,
        Resource.land: 234
    }

    govt.soldiers = Soldiers({
        Soldier.knights: 10,
        Soldier.footmen: 20
    })
    govt.consume()
    assert govt.resources == {
        Resource.food: 180 - 40 * KNIGHT_FOOD_CONSUMPTION,
        Resource.wood: 20,
        Resource.stone: 230,
        Resource.iron: 1,
        Resource.tools: 44,
        Resource.land: 234
    }


def test_consume_no_food():
    state = State_Data()
    res = Resources({
        Resource.food: 100,
        Resource.wood: 20,
        Resource.stone: 230,
        Resource.iron: 1,
        Resource.tools: 44,
        Resource.land: 234
    })
    govt = Government(state, res)
    govt.soldiers = Soldiers({
        Soldier.knights: 30,
        Soldier.footmen: 100
    })
    govt.consume()
    assert govt.resources == {
        Resource.wood: 20,
        Resource.stone: 230,
        Resource.iron: 1,
        Resource.tools: 44,
        Resource.land: 234
    }
    assert govt.missing_food == 30 * KNIGHT_FOOD_CONSUMPTION


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
    optimal_resources = Resources({
        Resource.food: 10,
        Resource.wood: 20,
        Resource.iron: 0,
        Resource.stone: 0,
        Resource.tools: 10,
        Resource.land: 0
    })
    secure_resources = Resources({
        Resource.food: 300,
        Resource.wood: 300,
        Resource.iron: 10,
        Resource.stone: 10,
        Resource.tools: 300,
        Resource.land: 10
    })
    soldiers = Soldiers({
        Soldier.knights: 20,
        Soldier.footmen: 34
    })
    govt = Government(state, resources, optimal_resources,
                      secure_resources, soldiers)
    govt.wage = 0.9
    govt.wage_autoregulation = False
    govt.missing_food = 21
    govt.employees = 56.6
    govt.old_wage = 0.8

    assert govt.to_dict() == {
        "resources": resources.to_raw_dict(),
        "optimal_resources": optimal_resources.to_raw_dict(),
        "secure_resources": secure_resources.to_raw_dict(),
        "wage": 0.9,
        "wage_autoregulation": False,
        "soldiers": soldiers.to_raw_dict(),
        "missing_food": 21,
        "employees": 56.6,
        "old_wage": 0.8
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
    optimal_resources = Resources({
        Resource.food: 10,
        Resource.wood: 20,
        Resource.iron: 0,
        Resource.stone: 0,
        Resource.tools: 10,
        Resource.land: 0
    })
    secure_resources = Resources({
        Resource.food: 300,
        Resource.wood: 300,
        Resource.iron: 10,
        Resource.stone: 10,
        Resource.tools: 300,
        Resource.land: 10
    })
    soldiers = Soldiers({
        Soldier.knights: 20,
        Soldier.footmen: 34
    })

    dicted = {
        "resources": resources.to_raw_dict(),
        "optimal_resources": optimal_resources.to_raw_dict(),
        "secure_resources": secure_resources.to_raw_dict(),
        "wage": 0.9,
        "wage_autoregulation": False,
        "soldiers": soldiers.to_raw_dict(),
        "missing_food": 21,
        "employees": 56.6,
        "old_wage": 0.8
    }
    govt = Government.from_dict(state, dicted)
    assert govt.parent is state
    assert govt.resources == resources
    assert govt.optimal_resources == optimal_resources
    assert govt.secure_resources == secure_resources
    assert govt.wage == 0.9
    assert govt.wage_autoregulation is False
    assert govt.soldiers == soldiers
    assert govt.missing_food == 21
    assert govt.employees == 56.6
    assert govt.old_wage == 0.8


def test_validate():
    state = State_Data()
    govt = Government(state)

    govt.resources = Resources({
        Resource.food: 100,
        Resource.wood: -0.00001,
        Resource.iron: -0.000099999,
        Resource.tools: 0.00001,
    })

    govt.validate()
    assert govt.resources == {
        Resource.food: 100,
        Resource.tools: 0.00001
    }

    govt.resources = Resources({
        Resource.food: 100,
        Resource.wood: -0.0001,
        Resource.iron: -0.000099999,
        Resource.tools: 0.00001,
    })
    with raises(ValidationError):
        govt.validate()

    govt.resources = Resources({
        Resource.food: -100,
        Resource.iron: -0.000099999,
        Resource.tools: -100,
    })
    with raises(ValidationError):
        govt.validate()
