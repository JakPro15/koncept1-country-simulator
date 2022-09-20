from math import inf
from random import randint
from typing import Any, Callable, ParamSpec, Type, TypeVar

from pytest import approx, raises  # type: ignore

from ..sources.auxiliaries.arithmetic_dict import Arithmetic_Dict
from ..sources.auxiliaries.constants import (BRIGAND_STRENGTH_CLASS,
                                             BRIGAND_STRENGTH_SOLDIER,
                                             DEFAULT_PRICES, FOOD_CONSUMPTION,
                                             INBUILT_RESOURCES,
                                             REBELLION_THRESHOLD, WAGE_CHANGE,
                                             WOOD_CONSUMPTION)
from ..sources.auxiliaries.enums import Class_Name, Month, Resource, Soldier
from ..sources.auxiliaries.resources import Resources
from ..sources.auxiliaries.soldiers import Soldiers
from ..sources.auxiliaries.testing import replace
from ..sources.state.market import Market, SupportsTrade
from ..sources.state.social_classes.class_file import Class
from ..sources.state.state_data import (Artisans, Government, Nobles, Others,
                                        Peasants, State_Data)
from ..sources.state.state_data_base_and_do_month import (
    EveryoneDeadError, RebellionError, StateDataNotFinalizedError)
from ..sources.state.state_modifiers import State_Modifiers


def test_constructor():
    state = State_Data(Month.August, 3)
    assert state.month == Month.August
    assert state.year == 3
    assert state.prices == DEFAULT_PRICES
    assert state.prices is not DEFAULT_PRICES
    assert isinstance(state.sm, State_Modifiers)
    assert state.brigands == 0
    assert state.brigands_strength == 0.8


def test_default_constructor():
    state = State_Data()
    assert state.month == Month.January
    assert state.year == 0
    assert state.prices == DEFAULT_PRICES
    assert state.prices is not DEFAULT_PRICES
    assert isinstance(state.sm, State_Modifiers)
    assert state.brigands == 0
    assert state.brigands_strength == 0.8


def test_classes():
    finalized = False

    def finalize(self: State_Data) -> None:
        nonlocal finalized
        finalized = True

    with replace(State_Data, "_create_market", finalize):
        state = State_Data()

        with raises(StateDataNotFinalizedError):
            state.classes

        resources = Resources({
            Resource.food: 31,
            Resource.wood: 32,
            Resource.stone: 33,
            Resource.iron: 34,
            Resource.tools: 35
        })

        nobles = Nobles(state, 20)
        artisans = Artisans(state, 30, resources)
        peasants = Peasants(state, 40)
        others = Others(state, 50)
        classes = {
            Class_Name.nobles: nobles,
            Class_Name.artisans: artisans,
            Class_Name.peasants: peasants,
            Class_Name.others: others
        }
        state.classes = classes

        assert nobles.lower_class is peasants
        assert artisans.lower_class is others
        assert peasants.lower_class is others
        assert others.lower_class is others

        assert finalized is False
        assert state.classes == classes
        assert state.classes is not classes

        state2 = State_Data()
        state2.government = Government(state2)
        state2.classes = classes
        assert finalized is True


def test_class_getters():
    state = State_Data.generate_empty_state()
    assert state.nobles is state.classes[Class_Name.nobles]
    assert state.artisans is state.classes[Class_Name.artisans]
    assert state.peasants is state.classes[Class_Name.peasants]
    assert state.others is state.classes[Class_Name.others]


def test_iteration():
    state = State_Data.generate_empty_state()
    for class1, class2 in zip(state.classes.values(), state):
        assert class1 is class2


def test_government():
    finalized = False

    def finalize(self: State_Data) -> None:
        nonlocal finalized
        finalized = True

    with replace(State_Data, "_create_market", finalize):
        state = State_Data()

        with raises(StateDataNotFinalizedError):
            state.government

        government = Government(state)
        state.government = government

        assert finalized is False
        assert state.government is government

        state2 = State_Data()
        state2.classes = {
            Class_Name.nobles: Nobles(state, 20),
            Class_Name.artisans: Artisans(state, 30),
            Class_Name.peasants: Peasants(state, 40),
            Class_Name.others: Others(state, 50)
        }
        state2.government = Government(state2)
        assert finalized is True


def test_market():
    state = State_Data()
    with raises(StateDataNotFinalizedError):
        state.market

    state.classes = {
        Class_Name.nobles: Nobles(state, 20),
        Class_Name.artisans: Artisans(state, 30),
        Class_Name.peasants: Peasants(state, 40),
        Class_Name.others: Others(state, 50)
    }
    state.government = Government(state)
    assert isinstance(state.market, Market)


def test_brigands_setters():
    state = State_Data()
    with raises(ValueError):
        state.brigands = -1
    with raises(ValueError):
        state.brigands_strength = -0.1

    state.brigands = 1
    state.brigands_strength = 0.1
    assert state.brigands == 1
    assert state.brigands_strength == 0.1

    state.brigands = 0
    state.brigands_strength = 0
    assert state.brigands == 0
    assert state.brigands_strength == 0


def test_set_wages_and_employers():
    class Fake_Class:
        def __init__(self, resources: Resources,
                     wage: float | None = None) -> None:
            self.resources = resources
            self.wage = wage if wage is not None else 0.15
            self.employees = randint(-500, 500)

        @property
        def real_resources(self) -> Resources:
            return self.resources

    res_land = Resources({Resource.land: 1})
    res_no_land = Resources()
    state = State_Data()
    state.sm.others_minimum_wage = 0.15
    classes = {
        Class_Name.nobles: Fake_Class(res_land, 0.8),
        Class_Name.artisans: Fake_Class(res_no_land),
        Class_Name.peasants: Fake_Class(res_land, 0.1),
        Class_Name.others: Fake_Class(res_no_land, 0.2),
    }
    state._classes = classes  # type: ignore

    govt = Fake_Class(res_land)
    state._government = govt  # type: ignore

    employers = state._set_wages_and_employers()  # type: ignore
    assert employers == [
        classes[Class_Name.nobles],
        classes[Class_Name.peasants],
        govt
    ]
    assert classes[Class_Name.nobles].wage == 0.8
    assert classes[Class_Name.artisans].wage == 0.15
    assert classes[Class_Name.peasants].wage == 0.15
    assert classes[Class_Name.others].wage == 0.2
    assert govt.wage == 0.15

    for social_class in classes.values():
        assert social_class.employees == 0
    assert govt.employees == 0


def test_set_wage_shares_and_employees_no_employer_max():
    class EmployerClass:
        def __init__(self, max_employees: float) -> None:
            self.max_employees = max_employees
            self.employable = False
            self.wage_share: float

    class EmployeeClass:
        def __init__(self, population: float) -> None:
            self.population = population
            self.employable = True
            self.wage_share: float

    employers = [
        EmployerClass(200),
        EmployerClass(50),
        EmployerClass(80),
        EmployerClass(100),
    ]

    classes = {
        0: employers[2],
        1: EmployeeClass(150),
        2: EmployeeClass(40),
        3: employers[0],
        4: EmployeeClass(100)
    }
    state = State_Data()
    state._classes = classes  # type: ignore

    employees_classes, employees, ratio = \
        state._set_employees_and_wage_shares(employers)  # type: ignore

    assert employees_classes == [
        classes[1], classes[2], classes[4]
    ]
    assert employees == 290
    assert classes[1].wage_share == approx(150 / 290)
    assert classes[2].wage_share == approx(40 / 290)
    assert classes[4].wage_share == approx(100 / 290)
    assert ratio == approx(290 / 430)


def test_set_wage_shares_and_employees_with_employer_max():
    class EmployerClass:
        def __init__(self, max_employees: float) -> None:
            self.max_employees = max_employees
            self.employable = False
            self.wage_share: float

    class EmployeeClass:
        def __init__(self, population: float) -> None:
            self.population = population
            self.employable = True
            self.wage_share: float

    employers = [
        EmployerClass(20),
        EmployerClass(5),
        EmployerClass(8),
        EmployerClass(10),
    ]

    classes = {
        0: employers[2],
        1: EmployeeClass(150),
        2: EmployeeClass(40),
        3: employers[0],
        4: EmployeeClass(100)
    }
    state = State_Data()
    state._classes = classes  # type: ignore

    employees_classes, employees, ratio = \
        state._set_employees_and_wage_shares(employers)  # type: ignore
    assert employees_classes == [
        classes[1], classes[2], classes[4]
    ]
    assert employees == 43
    assert classes[1].wage_share == approx(150 / 290)
    assert classes[2].wage_share == approx(40 / 290)
    assert classes[4].wage_share == approx(100 / 290)
    assert ratio == 1


def test_get_tools_used():
    state = State_Data()
    state.sm.peasant_tool_usage = 0.5
    state.sm.miner_tool_usage = 1.5
    employees = {
        Resource.food: 20,
        Resource.wood: 30,
        Resource.stone: 40,
        Resource.iron: 60
    }
    assert state._get_tools_used(employees) == 175  # type: ignore

    state.sm.peasant_tool_usage = 1
    state.sm.miner_tool_usage = 3
    employees = {
        Resource.food: 2.5,
        Resource.wood: 3.5,
        Resource.stone: 4.5,
        Resource.iron: 6.5
    }
    assert state._get_tools_used(employees) == 39  # type: ignore


def test_add_employees():
    class Empty_Class:
        def __init__(self):
            self.employees = 0

    employers = [
        Empty_Class(),
        Empty_Class(),
        Empty_Class()
    ]
    employees = {
        employers[0]: 20,
        employers[1]: 30,
        employers[2]: 65,
    }
    State_Data._add_employees(employees)  # type: ignore

    assert employers[0].employees == 20
    assert employers[1].employees == 30
    assert employers[2].employees == 65

    employers.append(Empty_Class())
    employees = {
        employers[0]: 20,
        employers[1]: 5,
        employers[2]: 15,
        employers[3]: 40
    }
    State_Data._add_employees(employees)  # type: ignore

    assert employers[0].employees == 40
    assert employers[1].employees == 35
    assert employers[2].employees == 80
    assert employers[3].employees == 40


def test_get_produced_and_used():
    ratioed_employees = Arithmetic_Dict({
        Resource.food: 20,
        Resource.wood: 40,
        Resource.stone: 10,
        Resource.iron: 30,
    })

    state = State_Data(Month.June)
    food_production = state.sm.food_production[Month.June]
    state.sm.wood_production = 2
    state.sm.stone_production = 1.2
    state.sm.iron_production = 1.5

    produced, used = state._get_produced_and_used(  # type: ignore
        ratioed_employees
    )
    assert produced == {
        Resource.food: food_production * 20,
        Resource.wood: 80,
        Resource.stone: 12,
        Resource.iron: 45
    }
    assert used == {
        Resource.tools: state._get_tools_used(  # type: ignore
            ratioed_employees
        )
    }


def test_set_employers_employees_no_max():
    class Employer_Class:
        def __init__(self, wage: float, max_emps: float) -> None:
            self.wage = wage
            self.max_employees = max_emps
            self.employees = 0
            self.increase_wage: bool

    employers = [
        Employer_Class(2, 500),
        Employer_Class(5, 500),
        Employer_Class(3, 500)
    ]
    employees = 400
    State_Data._set_employers_employees(employers,  # type: ignore
                                        employees, 4/15)

    assert employers[0].employees == 80
    assert employers[1].employees == 200
    assert employers[2].employees == 120

    assert employers[0].increase_wage
    assert not employers[1].increase_wage
    assert employers[2].increase_wage

    employers = [
        Employer_Class(2, 500),
        Employer_Class(5, 500)
    ]
    employees = 700
    State_Data._set_employers_employees(employers,  # type: ignore
                                        employees, 0.7)

    assert employers[0].employees == 200
    assert employers[1].employees == 500

    assert employers[0].increase_wage
    assert not employers[1].increase_wage


def test_set_employers_employees_with_max():
    class Employer_Class:
        def __init__(self, wage: float, max_emps: float) -> None:
            self.wage = wage
            self.max_employees = max_emps
            self.employees = 0
            self.increase_wage: bool

    employers = [
        Employer_Class(2, 50),
        Employer_Class(5, 500),
        Employer_Class(3, 500)
    ]
    employees = 850
    State_Data._set_employers_employees(employers,  # type: ignore
                                        employees, 85/105)

    assert employers[0].employees == 50
    assert employers[1].employees == 500
    assert employers[2].employees == 300

    assert not employers[0].increase_wage
    assert not employers[1].increase_wage
    assert employers[2].increase_wage

    employers = [
        Employer_Class(2, 50),
        Employer_Class(5, 600),
        Employer_Class(3, 250),
        Employer_Class(0, 500)
    ]
    employees = 850
    State_Data._set_employers_employees(employers,  # type: ignore
                                        employees, 85/140)

    assert employers[0].employees == 50
    assert employers[1].employees == 550
    assert employers[2].employees == 250
    assert employers[3].employees == 0

    assert not employers[0].increase_wage
    assert not employers[1].increase_wage
    assert not employers[2].increase_wage
    assert employers[3].increase_wage


def test_set_employers_employees_not_all_employed():
    class Employer_Class:
        def __init__(self, wage: float, max_emps: float) -> None:
            self.wage = wage
            self.max_employees = max_emps
            self.employees = 0
            self.increase_wage: bool

    employers = [
        Employer_Class(2, 50),
        Employer_Class(5, 100),
        Employer_Class(3, 150)
    ]
    employees = 850
    State_Data._set_employers_employees(employers,  # type: ignore
                                        employees, 1)

    assert employers[0].employees == 50
    assert employers[1].employees == 100
    assert employers[2].employees == 150

    assert not employers[0].increase_wage
    assert not employers[1].increase_wage
    assert not employers[2].increase_wage

    employers = [
        Employer_Class(0, 50),
        Employer_Class(0, 600),
        Employer_Class(0, 250),
        Employer_Class(0, 500)
    ]
    employees = 850
    State_Data._set_employers_employees(employers,  # type: ignore
                                        employees, 85/140)

    assert employers[0].employees == 0
    assert employers[1].employees == 0
    assert employers[2].employees == 0
    assert employers[3].employees == 0

    assert employers[0].increase_wage
    assert employers[1].increase_wage
    assert employers[2].increase_wage
    assert employers[3].increase_wage


def test_employees_to_profit():
    class Employer_Class:
        def __init__(self, employees: float) -> None:
            self.employees = employees
            self.profit_share: float

    employers = [
        Employer_Class(50),
        Employer_Class(150),
        Employer_Class(500),
        Employer_Class(300)
    ]
    State_Data._employees_to_profit(employers)  # type: ignore

    assert employers[0].profit_share == 0.05
    assert employers[1].profit_share == 0.15
    assert employers[2].profit_share == 0.5
    assert employers[3].profit_share == 0.3

    employers = [
        Employer_Class(50),
        Employer_Class(150),
        Employer_Class(50)
    ]
    State_Data._employees_to_profit(employers)  # type: ignore

    assert employers[0].profit_share == 0.2
    assert employers[1].profit_share == 0.6
    assert employers[2].profit_share == 0.2


def test_distribute_produced_and_used():
    class EmployerClass:
        def __init__(self, wage: float, profit_share: float,
                     resources: Resources) -> None:
            self.wage = wage
            self.profit_share = profit_share
            self.resources = resources.copy()

    class EmployeeClass:
        def __init__(self, wage_share: float, resources: Resources) -> None:
            self.wage_share = wage_share
            self.resources = resources.copy()

    state = State_Data()
    state.prices = Resources({
        Resource.food: 1,
        Resource.wood: 1,
        Resource.stone: 1,
        Resource.iron: 1,
        Resource.tools: 1,
        Resource.land: 1
    })

    resources = Resources({
        Resource.food: 100,
        Resource.wood: 100,
        Resource.stone: 100,
        Resource.iron: 100,
        Resource.tools: 100,
        Resource.land: 100
    })
    employers = [
        EmployerClass(0.2, 0.3, resources),
        EmployerClass(0.3, 0.2, Resources()),
        EmployerClass(0.5, 0.5, resources)
    ]
    employees = [
        EmployeeClass(0.4, resources),
        EmployeeClass(0.6, Resources())
    ]
    produced = Resources({
        Resource.food: 100,
        Resource.wood: 100,
        Resource.stone: 100,
        Resource.iron: 100
    })
    used = Resources({
        Resource.tools: 10
    })
    state._distribute_produced_and_used(employers, employees,  # type: ignore
                                        produced, used)
    assert state.max_wage == 0.975

    assert employers[0].resources == {
        Resource.food: 124,
        Resource.wood: 124,
        Resource.stone: 124,
        Resource.iron: 124,
        Resource.tools: 97,
        Resource.land: 100
    }
    assert employers[1].resources == {
        Resource.food: 14,
        Resource.wood: 14,
        Resource.stone: 14,
        Resource.iron: 14,
        Resource.tools: -2
    }
    assert employers[2].resources == {
        Resource.food: 125,
        Resource.wood: 125,
        Resource.stone: 125,
        Resource.iron: 125,
        Resource.tools: 95,
        Resource.land: 100
    }
    assert employees[0].resources == {
        Resource.food: 114.8,
        Resource.wood: 114.8,
        Resource.stone: 114.8,
        Resource.iron: 114.8,
        Resource.tools: 100,
        Resource.land: 100
    }
    assert employees[1].resources == {
        Resource.food: 22.2,
        Resource.wood: 22.2,
        Resource.stone: 22.2,
        Resource.iron: 22.2
    }


def test_set_new_wages_with_max_wage():
    class EmployerClass:
        def __init__(self, wage: float, increase_wage: float) -> None:
            self.wage = wage
            self.increase_wage = increase_wage

    state = State_Data()
    state.max_wage = 0.8

    employers = [
        EmployerClass(0.4, True),
        EmployerClass(1 - WAGE_CHANGE, True),
        EmployerClass(0.4, False),
        EmployerClass(WAGE_CHANGE, True),
        EmployerClass(WAGE_CHANGE / 2, False),
        EmployerClass(1 - WAGE_CHANGE / 2, False),
    ]
    state._set_new_wages(employers)  # type: ignore
    assert employers[0].wage == 0.4 + WAGE_CHANGE
    assert employers[1].wage == 0.8
    assert employers[2].wage == 0.4 - WAGE_CHANGE
    assert employers[3].wage == 2 * WAGE_CHANGE
    assert employers[4].wage == 0
    assert employers[5].wage == 0.8


def test_employ():  # EXCEL CALCULATIONS USED
    def max_emps(number: float) -> Resources:
        return Resources({Resource.land: number * 10,
                          Resource.tools: 100000})

    state = State_Data(Month.June)
    state.sm.worker_land_usage = 10
    state.sm.others_minimum_wage = 0.3
    state.sm.avg_food_production = 2
    state.sm.wood_production = 1.5
    state.sm.stone_production = 0.7
    state.sm.iron_production = 1.2
    state.sm.peasant_tool_usage = 0.15
    state.sm.miner_tool_usage = 0.2
    state.prices = Resources({
        Resource.food: 2 * DEFAULT_PRICES.food,
        Resource.wood: 1.5 * DEFAULT_PRICES.wood,
        Resource.stone: 3 * DEFAULT_PRICES.stone,
        Resource.iron: 0.75 * DEFAULT_PRICES.iron,
        Resource.tools: 1 * DEFAULT_PRICES.tools,
        Resource.land: 1.25 * DEFAULT_PRICES.land,
    })

    state.classes = {
        Class_Name.nobles: Nobles(state, 20, max_emps(30)),
        Class_Name.artisans: Artisans(state, 30, max_emps(0)),
        Class_Name.peasants: Peasants(state, 40, max_emps(40 + 20)),
        Class_Name.others: Others(state, 50, max_emps(10))
    }
    state.nobles.resources.land \
        -= INBUILT_RESOURCES[Class_Name.nobles].land * 20
    state.peasants.resources.land \
        -= INBUILT_RESOURCES[Class_Name.peasants].land * 40

    state.nobles.wage = 0.5
    state.peasants.wage = 0.25
    state.others.wage = 0.35
    state.government = Government(state)

    state._employ()  # type: ignore

    def _approx(x: float):
        return approx(x, abs=0.01)

    assert state.nobles.resources == {
        Resource.food: _approx(3.45),
        Resource.wood: _approx(3.88),
        Resource.stone: _approx(3.62),
        Resource.iron: _approx(1.55),
        Resource.tools: _approx(100000 - 4.4),
        Resource.land:
        -INBUILT_RESOURCES[Class_Name.nobles].land * 20 + max_emps(30).land
    }
    assert state.artisans.resources == {
        Resource.tools: 100000
    }
    assert state.peasants.resources == {
        Resource.food: _approx(2.9),
        Resource.wood: _approx(3.26),
        Resource.stone: _approx(3.04),
        Resource.iron: _approx(1.3),
        Resource.tools: _approx(100000 - 2.64),
        Resource.land:
        -INBUILT_RESOURCES[Class_Name.peasants].land * 40 + max_emps(60).land
    }
    assert state.others.resources == {
        Resource.food: _approx(7.45),
        Resource.wood: _approx(8.38),
        Resource.stone: _approx(7.82),
        Resource.iron: _approx(3.35),
        Resource.tools: _approx(100000 - 1.76),
        Resource.land: max_emps(10).land
    }

    assert state.nobles.employees == approx(25)
    assert state.artisans.employees == approx(0)
    assert state.peasants.employees == approx(15)
    assert state.others.employees == approx(10)

    assert state.nobles.wage == approx(0.5 - WAGE_CHANGE)
    assert state.artisans.wage == approx(0)
    assert state.peasants.wage == approx(0.3 + WAGE_CHANGE)
    assert state.others.wage == approx(0.3)

    assert state.nobles.old_wage == approx(0.5)
    assert state.artisans.old_wage == approx(0.3)
    assert state.peasants.old_wage == approx(0.3)
    assert state.others.old_wage == approx(0.35)


def test_advance_month():
    state = State_Data(Month.August, 3)
    assert state.year == 3
    assert state.month == Month.August
    state._advance_month()  # type: ignore
    assert state.year == 3
    assert state.month == Month.September
    state._advance_month()  # type: ignore
    assert state.year == 3
    assert state.month == Month.October
    state._advance_month()  # type: ignore
    assert state.year == 3
    assert state.month == Month.November
    state._advance_month()  # type: ignore
    assert state.year == 3
    assert state.month == Month.December
    state._advance_month()  # type: ignore
    assert state.year == 4
    assert state.month == Month.January


def test_create_market():
    state = State_Data()
    classes: dict[int, int] = {4: 1, 5: 2, 6: 3}
    govt = Government(state)
    state.government = govt
    state._classes = classes  # type: ignore
    state._create_market()  # type: ignore
    assert state._market.trading_objs == [1, 2, 3, govt]  # type: ignore


def test_get_available_employees():
    state = State_Data.generate_empty_state()
    state.nobles.population = 1
    state.artisans.population = 10
    state.peasants.population = 100
    state.others.population = 1000
    assert state.get_available_employees() == 1000


def test_get_available_employees_multiple_employable_classes():
    state = State_Data.generate_empty_state()
    state.nobles.population = 1
    state.peasants.population = 100
    state.others.population = 1000
    state._classes[Class_Name.artisans] = Others(state, 10)  # type: ignore
    assert state.get_available_employees() == 1010


def classes_eq(class1: Class, class2: Class) -> bool:
    """
    Normally Class objects are compared by identity, but in this test case I
    want to compare them by value. Doesn't compare parents.
    """
    if type(class1) != type(class2):
        return False
    if class1.population != class2.population:
        return False
    if class1.resources != class2.resources:
        return False

    if class1.starving != class2.starving:
        return False
    if class1.freezing != class2.freezing:
        return False
    if class1.demoted_from != class2.demoted_from:
        return False
    if class1.demoted_to != class2.demoted_to:
        return False
    if class1.promoted_from != class2.promoted_from:
        return False
    if class1.promoted_to != class2.promoted_to:
        return False

    if class1.happiness != class2.happiness:
        return False
    if class1.employees != class2.employees:
        return False
    if class1.wage != class2.wage:
        return False
    if class1.old_wage != class2.old_wage:
        return False

    return True


def govt_eq(govt1: Government, govt2: Government) -> bool:
    """
    Normally Government objects are compared by identity, but in this test
    case I want to compare them by value. Doesn't compare parents.
    """
    if govt1.resources != govt2.resources:
        return False
    if govt1.secure_resources != govt2.secure_resources:
        return False
    if govt1.optimal_resources != govt2.optimal_resources:
        return False

    if govt1.soldiers != govt2.soldiers:
        return False
    if govt1.missing_food != govt2.missing_food:
        return False

    if govt1.employees != govt2.employees:
        return False
    if govt1.wage != govt2.wage:
        return False
    if govt1.wage_autoregulation != govt2.wage_autoregulation:
        return False
    if govt1.old_wage != govt2.old_wage:
        return False

    return True


def test_from_dict():
    state = State_Data()
    nobles = Nobles(state, 20, Resources({Resource.land: 456}))
    nobles.promoted_to = True
    nobles.demoted_from = True
    artisans = Artisans(state, 20, Resources({Resource.tools: 654}))
    artisans.starving = True
    peasants = Peasants(state, 20, Resources({Resource.iron: 45}))
    others = Others(state, 20, Resources({Resource.food: 5, Resource.wood: 6}))
    others.demoted_to = True
    res = Resources({Resource.food: 20, Resource.wood: 30, Resource.land: 40})
    govt = Government(state, res / 4, res / 2, res / 1.5,
                      Soldiers({Soldier.footmen: 10, Soldier.knights: 2}))
    govt.wage = 0.8
    govt.wage_autoregulation = False

    data = {
        "year": 81,
        "month": "April",
        "classes": {
            "nobles": nobles.to_dict(),
            "artisans": artisans.to_dict(),
            "peasants": peasants.to_dict(),
            "others": others.to_dict()
        },
        "government": govt.to_dict(),
        "prices": res.to_raw_dict(),
        "laws": {
            "tax_personal": {
                "nobles": 0.1,
                "artisans": 0.2,
                "peasants": 0.3,
                "others": 0.4,
            },
            "tax_property": {
                "nobles": 0.15,
                "artisans": 0.25,
                "peasants": 0.35,
                "others": 0.45,
            },
            "tax_income": {
                "nobles": 0.16,
                "artisans": 0.26,
                "peasants": 0.36,
                "others": 0.46,
            },
            "wage_minimum": 0.6,
            "max_prices": (res * 2).to_raw_dict(),
        }
    }
    state = State_Data.from_dict(data)
    assert state.month == Month.April
    assert state.year == 81
    assert classes_eq(state.nobles, nobles)
    assert classes_eq(state.artisans, artisans)
    assert classes_eq(state.peasants, peasants)
    assert classes_eq(state.others, others)
    assert govt_eq(state.government, govt)
    assert state.prices == res
    assert state.sm.tax_rates["personal"] == {
        Class_Name.nobles: 0.1,
        Class_Name.artisans: 0.2,
        Class_Name.peasants: 0.3,
        Class_Name.others: 0.4,
    }
    assert state.sm.tax_rates["property"] == {
        Class_Name.nobles: 0.15,
        Class_Name.artisans: 0.25,
        Class_Name.peasants: 0.35,
        Class_Name.others: 0.45,
    }
    assert state.sm.tax_rates["income"] == {
        Class_Name.nobles: 0.16,
        Class_Name.artisans: 0.26,
        Class_Name.peasants: 0.36,
        Class_Name.others: 0.46,
    }
    assert state.sm.others_minimum_wage == 0.6
    assert state.sm.max_prices == res * 2


def test_from_dict_all_strings():
    state = State_Data()
    nobles = Nobles(state, 20, Resources({Resource.land: 456}))
    nobles.promoted_to = True
    nobles.demoted_from = True
    artisans = Artisans(state, 20, Resources({Resource.tools: 654}))
    artisans.starving = True
    peasants = Peasants(state, 20, Resources({Resource.iron: 45}))
    others = Others(state, 20, Resources({Resource.food: 5, Resource.wood: 6}))
    others.demoted_to = True
    res = Resources({Resource.food: 20, Resource.wood: 30, Resource.land: 40})
    govt = Government(state, res / 4, res / 2, res / 1.5,
                      Soldiers({Soldier.footmen: 10, Soldier.knights: 2}))
    govt.wage = 0.8
    govt.wage_autoregulation = False

    data = {
        "year": "81",
        "month": "April",
        "classes": {
            "nobles": nobles.to_dict(),
            "artisans": artisans.to_dict(),
            "peasants": peasants.to_dict(),
            "others": others.to_dict()
        },
        "government": govt.to_dict(),
        "prices": res.to_raw_dict(),
        "laws": {
            "tax_personal": {
                "nobles": "0.1",
                "artisans": "0.2",
                "peasants": "0.3",
                "others": "0.4",
            },
            "tax_property": {
                "nobles": "0.15",
                "artisans": "0.25",
                "peasants": "0.35",
                "others": "0.45",
            },
            "tax_income": {
                "nobles": "0.16",
                "artisans": "0.26",
                "peasants": "0.36",
                "others": "0.46",
            },
            "wage_minimum": "0.6",
            "max_prices": (res * 2).to_raw_dict(),
        }
    }
    state = State_Data.from_dict(data)
    assert state.month == Month.April
    assert state.year == 81
    assert classes_eq(state.nobles, nobles)
    assert classes_eq(state.artisans, artisans)
    assert classes_eq(state.peasants, peasants)
    assert classes_eq(state.others, others)
    assert govt_eq(state.government, govt)
    assert state.prices == res
    assert state.sm.tax_rates["personal"] == {
        Class_Name.nobles: 0.1,
        Class_Name.artisans: 0.2,
        Class_Name.peasants: 0.3,
        Class_Name.others: 0.4,
    }
    assert state.sm.tax_rates["property"] == {
        Class_Name.nobles: 0.15,
        Class_Name.artisans: 0.25,
        Class_Name.peasants: 0.35,
        Class_Name.others: 0.45,
    }
    assert state.sm.tax_rates["income"] == {
        Class_Name.nobles: 0.16,
        Class_Name.artisans: 0.26,
        Class_Name.peasants: 0.36,
        Class_Name.others: 0.46,
    }
    assert state.sm.others_minimum_wage == 0.6
    assert state.sm.max_prices == res * 2


def test_to_dict():
    state = State_Data(Month.April, 81)

    nobles = Nobles(state, 20, Resources({Resource.land: 456}))
    nobles.promoted_to = True
    nobles.demoted_from = True
    artisans = Artisans(state, 20, Resources({Resource.tools: 654}))
    artisans.starving = True
    peasants = Peasants(state, 20, Resources({Resource.iron: 45}))
    others = Others(state, 20, Resources({Resource.food: 5, Resource.wood: 6}))
    others.demoted_to = True
    state.classes = {
        Class_Name.nobles: nobles,
        Class_Name.artisans: artisans,
        Class_Name.peasants: peasants,
        Class_Name.others: others
    }

    res = Resources({Resource.food: 20, Resource.wood: 30, Resource.land: 40})
    govt = Government(state, res / 4, res / 2, res / 1.5,
                      Soldiers({Soldier.footmen: 10, Soldier.knights: 2}))
    govt.wage = 0.8
    govt.wage_autoregulation = False
    state.government = govt
    state.prices = res

    state.sm.tax_rates["personal"] = Arithmetic_Dict({
        Class_Name.nobles: 0.1,
        Class_Name.artisans: 0.2,
        Class_Name.peasants: 0.3,
        Class_Name.others: 0.4,
    })
    state.sm.tax_rates["property"] = Arithmetic_Dict({
        Class_Name.nobles: 0.15,
        Class_Name.artisans: 0.25,
        Class_Name.peasants: 0.35,
        Class_Name.others: 0.45,
    })
    state.sm.tax_rates["income"] = Arithmetic_Dict({
        Class_Name.nobles: 0.16,
        Class_Name.artisans: 0.26,
        Class_Name.peasants: 0.36,
        Class_Name.others: 0.46,
    })
    state.sm.others_minimum_wage = 0.6
    state.sm.max_prices = res * 2

    data = {
        "year": 81,
        "month": Month.April,
        "classes": {
            "nobles": nobles.to_dict(),
            "artisans": artisans.to_dict(),
            "peasants": peasants.to_dict(),
            "others": others.to_dict()
        },
        "government": govt.to_dict(),
        "prices": res.to_raw_dict(),
        "laws": {
            "tax_personal": {
                "nobles": 0.1,
                "artisans": 0.2,
                "peasants": 0.3,
                "others": 0.4,
            },
            "tax_property": {
                "nobles": 0.15,
                "artisans": 0.25,
                "peasants": 0.35,
                "others": 0.45,
            },
            "tax_income": {
                "nobles": 0.16,
                "artisans": 0.26,
                "peasants": 0.36,
                "others": 0.46,
            },
            "wage_minimum": 0.6,
            "max_prices": (res * 2).to_raw_dict(),
        }
    }
    assert state.to_dict() == data


def test_do_growth():
    grown: dict[Class_Name, float] = {}

    def fake_grow(self: Class, factor: float) -> None:
        nonlocal grown
        grown[self.class_name] = factor

    with replace(Class, "grow_population", fake_grow):
        state = State_Data.generate_empty_state()
        state.sm.default_growth_factor = 0.1 * 12
        state._do_growth()  # type: ignore
        assert grown == {
            Class_Name.nobles: approx(0.1),
            Class_Name.artisans: approx(0.1),
            Class_Name.peasants: approx(0.1),
            Class_Name.others: approx(0.1),
        }


def test_do_starvation_food():
    state = State_Data.generate_empty_state()
    state.sm.starvation_mortality = 0.1

    res = Resources({Resource.food: -20 * FOOD_CONSUMPTION})

    nobles = Nobles(state, 20)
    artisans = Artisans(state, 40)
    artisans.resources = res
    peasants = Peasants(state)
    others = Others(state, 200)
    others.resources = res * 100

    state.classes = {
        Class_Name.nobles: nobles,
        Class_Name.artisans: artisans,
        Class_Name.peasants: peasants,
        Class_Name.others: others
    }
    state.government = Government(state)

    state._do_starvation()  # type: ignore

    assert nobles.population == 20
    assert nobles.resources == {}
    assert nobles.happiness == 0

    assert artisans.population == 38
    assert artisans.resources == INBUILT_RESOURCES[Class_Name.artisans] * 2
    assert artisans.happiness == approx(Class.starvation_happiness(0.05))

    assert peasants.population == 0
    assert peasants.resources == {}
    assert peasants.happiness == 0

    assert others.population == 0
    assert others.resources == {}
    assert others.happiness == 0


def test_do_starvation_wood():
    state = State_Data.generate_empty_state()
    state.sm.freezing_mortality = 0.1

    res = Resources({Resource.wood: -20 * WOOD_CONSUMPTION[Month.January]})

    nobles = Nobles(state, 20)
    artisans = Artisans(state, 40)
    artisans.resources = res
    peasants = Peasants(state)
    others = Others(state, 200)
    others.resources = res * 100

    state.classes = {
        Class_Name.nobles: nobles,
        Class_Name.artisans: artisans,
        Class_Name.peasants: peasants,
        Class_Name.others: others
    }
    state.government = Government(state)

    state._do_starvation()  # type: ignore

    assert nobles.population == 20
    assert nobles.resources == {}
    assert nobles.happiness == 0

    assert artisans.population == 38
    assert artisans.resources == INBUILT_RESOURCES[Class_Name.artisans] * 2
    assert artisans.happiness == approx(Class.starvation_happiness(0.05))

    assert peasants.population == 0
    assert peasants.resources == {}
    assert peasants.happiness == 0

    assert others.population == 0
    assert others.resources == {}
    assert others.happiness == 0


def test_do_starvation_both():
    state = State_Data.generate_empty_state()
    state.sm.starvation_mortality = 0.2
    state.sm.freezing_mortality = 0.1

    res = Resources({
        Resource.food: -10 * FOOD_CONSUMPTION,
        Resource.wood: -20 * WOOD_CONSUMPTION[Month.January]
    })

    nobles = Nobles(state, 20)
    artisans = Artisans(state, 40)
    artisans.resources = res
    peasants = Peasants(state)
    others = Others(state, 200)
    others.resources = res * 50

    state.classes = {
        Class_Name.nobles: nobles,
        Class_Name.artisans: artisans,
        Class_Name.peasants: peasants,
        Class_Name.others: others
    }
    state.government = Government(state)

    state._do_starvation()  # type: ignore

    assert nobles.population == 20
    assert nobles.resources == {}
    assert nobles.happiness == 0

    assert artisans.population == 36
    assert artisans.resources == INBUILT_RESOURCES[Class_Name.artisans] * 4
    assert artisans.happiness == approx(Class.starvation_happiness(0.1))

    assert peasants.population == 0
    assert peasants.resources == {}
    assert peasants.happiness == 0

    assert others.population == 0
    assert others.resources == {}
    assert others.happiness == 0


def test_reset_flags():
    state = State_Data.generate_empty_state()
    state.nobles.starving = True
    state.nobles.promoted_to = True
    state.nobles.demoted_from = True

    state.artisans.freezing = True
    state.artisans.demoted_from = True
    state.artisans.demoted_to = True

    state.peasants.freezing = True
    state.peasants.promoted_to = True
    state.peasants.demoted_to = True
    state.peasants.promoted_from = True

    state.others.starving = True
    state.others.freezing = True
    state.others.promoted_from = True

    state._reset_flags()  # type: ignore

    for social_class in state:
        assert social_class.promoted_to is False
        assert social_class.promoted_from is False
        assert social_class.demoted_to is False
        assert social_class.demoted_from is False

    assert state.nobles.starving is True
    assert state.nobles.freezing is False
    assert state.artisans.starving is False
    assert state.artisans.freezing is True
    assert state.peasants.starving is False
    assert state.peasants.freezing is True
    assert state.others.starving is True
    assert state.others.freezing is True


def test_do_demotions():
    class Overpopulated(Class):
        def __init__(self, parent: State_Data, overpopulation: float,
                     name: Class_Name):
            self._name = name
            self._overpopulation = overpopulation
            super().__init__(parent, 50, Resources(100))

        @property
        def class_overpopulation(self) -> float:
            return self._overpopulation

        @property
        def class_name(self) -> Class_Name:
            return self._name

        def produce(self) -> None:
            return super().produce()

    state = State_Data()
    state.classes = {
        Class_Name.nobles: Overpopulated(state, 10, Class_Name.nobles),
        Class_Name.artisans: Overpopulated(state, 100, Class_Name.artisans),
        Class_Name.peasants: Overpopulated(state, 10, Class_Name.peasants),
        Class_Name.others: Overpopulated(state, 0, Class_Name.others)
    }
    state.government = Government(state)

    state._do_demotions()  # type: ignore

    assert state.nobles.population == 40
    assert state.nobles.resources == Resources(100) \
        + (INBUILT_RESOURCES[Class_Name.nobles]
           - INBUILT_RESOURCES[Class_Name.peasants]) * 10
    assert state.nobles.demoted_from
    assert not state.nobles.demoted_to

    assert state.artisans.population == 0
    # entire class demoted - all their resources moved
    assert state.artisans.resources == {}
    assert state.artisans.demoted_from
    assert not state.artisans.demoted_to

    assert state.peasants.population == 50
    assert state.peasants.resources == Resources(100) \
        + (INBUILT_RESOURCES[Class_Name.peasants]
           - INBUILT_RESOURCES[Class_Name.others]) * 10
    assert state.peasants.demoted_from
    assert state.peasants.demoted_to

    assert state.others.population == 110
    assert state.others.resources == Resources(100) * 2 + \
        INBUILT_RESOURCES[Class_Name.artisans] * 50
    assert not state.others.demoted_from
    assert state.others.demoted_to


def test_secure_classes():
    handles: set[str] = set()
    validates: set[str] = set()

    def fake_handle(self: Class) -> None:
        handles.add(self.class_name.name)

    def fake_validate_cls(self: Class) -> None:
        validates.add(self.class_name.name)

    def fake_validate_govt(self: Government) -> None:
        validates.add("government")

    with replace(Class, "handle_empty_class", fake_handle), \
         replace(Class, "validate", fake_validate_cls), \
         replace(Government, "validate", fake_validate_govt):
        state = State_Data.generate_empty_state()
        state._secure_classes()  # type: ignore

    assert validates == {"nobles", "artisans", "peasants", "others",
                         "government"}
    assert handles == {"nobles", "artisans", "peasants", "others"}


def test_promotion_math():
    assert State_Data._promotion_math(2000, 200, inf) == (0, 0)  # type: ignore
    assert State_Data._promotion_math(2000, 0, 5) == (0, 0)  # type: ignore
    assert State_Data._promotion_math(0, 200, 5) == (0, 0)  # type: ignore

    old_part_paid = 0
    old_transferred = 0
    for cost in range(1, 2000):
        part_paid, transferred = \
            State_Data._promotion_math(cost, 200, 5)  # type: ignore
        assert 0 <= part_paid <= 1
        assert 0 <= transferred <= 200
        assert old_part_paid <= part_paid
        assert old_transferred <= transferred
        old_part_paid = part_paid
        old_transferred = transferred

    for population in range(1, 2000):
        part_paid, transferred = \
            State_Data._promotion_math(2000, population, 5)  # type: ignore
        assert 0 <= part_paid <= 1
        assert 0 <= transferred <= population

    old_part_paid = 1
    old_transferred = 200
    for cost in range(1, 2000):
        part_paid, transferred = \
            State_Data._promotion_math(2000, 200, cost)  # type: ignore
        assert 0 <= part_paid <= 1
        assert 0 <= transferred <= 200
        assert old_part_paid >= part_paid
        assert old_transferred >= transferred
        old_part_paid = part_paid
        old_transferred = transferred


def fake_pop_getter(self: Class) -> float:
    return self._population  # type: ignore


def fake_pop_setter(self: Class, new: float) -> None:
    self._population = new  # type: ignore


fake_population = property(fake_pop_getter, fake_pop_setter)


def test_do_one_promotion():
    with replace(Class, "population", fake_population):
        state = State_Data.generate_empty_state()
        state.prices = Resources(1)
        state.peasants.resources = Resources(100)
        state.peasants.population = 60

        part_paid, transferred = State_Data._promotion_math(  # type: ignore
            600, 60, 6
        )
        state._do_one_promotion(  # type: ignore
            state.peasants, state.nobles, 6
        )
        assert state.peasants.population == approx(60 - transferred)
        assert state.nobles.population == approx(transferred)
        assert state.peasants.resources == Resources((1 - part_paid) * 100)
        assert state.nobles.resources == Resources(part_paid * 100)


def test_do_double_promotion():
    with replace(Class, "population", fake_population):
        state = State_Data.generate_empty_state()
        state.prices = Resources(1)
        state.others.resources = Resources(100)
        state.others.population = 60

        part_paid, transferred = State_Data._promotion_math(  # type: ignore
            600, 60, 6
        )
        state._do_double_promotion(  # type: ignore
            state.others, state.peasants, 4, state.artisans, 8
        )
        assert state.others.population == approx(60 - transferred)
        assert state.peasants.population == approx(transferred / 2)
        assert state.artisans.population == approx(transferred / 2)

        assert state.others.resources == Resources((1 - part_paid) * 100)
        assert state.peasants.resources == Resources(part_paid * (1 / 3) * 100)
        assert state.artisans.resources == Resources(part_paid * (2 / 3) * 100)


def test_do_promotions_all():
    promotions: set[Any] = set()

    def fake_single_prom(self: State_Data, *args: Any) -> None:
        promotions.add(("single", args))

    def fake_double_prom(self: State_Data, *args: Any) -> None:
        promotions.add(("double", args))

    with replace(State_Data, "_do_one_promotion", fake_single_prom), \
         replace(State_Data, "_do_double_promotion", fake_double_prom):
        state = State_Data.generate_empty_state()
        state.prices = Resources(1)
        state.sm.increase_price_factor = 1.5
        state.sm.nobles_cap = 1

        state.nobles.population = 20
        state.artisans.population = 30
        state.peasants.population = 40
        state.others.population = 50

        state.nobles.resources = Resources(500)
        state.artisans.resources = Resources(400)
        state.peasants.resources = Resources(300)
        state.others.resources = Resources(200)

        state._do_promotions()  # type: ignore

        p_to_n_inc_price = (
            INBUILT_RESOURCES[Class_Name.nobles]
            - INBUILT_RESOURCES[Class_Name.peasants]
        ).worth(state.prices) * 1.5

        a_to_n_inc_price = (
            INBUILT_RESOURCES[Class_Name.nobles]
            - INBUILT_RESOURCES[Class_Name.artisans]
        ).worth(state.prices) * 1.5

        o_to_p_inc_price = (
            INBUILT_RESOURCES[Class_Name.peasants]
            - INBUILT_RESOURCES[Class_Name.others]
        ).worth(state.prices) * 1.5

        o_to_a_inc_price = (
            INBUILT_RESOURCES[Class_Name.artisans]
            - INBUILT_RESOURCES[Class_Name.others]
        ).worth(state.prices) * 1.5

        assert promotions == {
            ("single", (state.peasants, state.nobles, p_to_n_inc_price)),
            ("single", (state.artisans, state.nobles, a_to_n_inc_price)),
            ("double", (state.others, state.peasants, o_to_p_inc_price,
                        state.artisans, o_to_a_inc_price)),
        }


def test_do_promotions_starving_freezing():
    promotions: set[Any] = set()

    def fake_single_prom(self: State_Data, *args: Any) -> None:
        promotions.add(("single", args))

    def fake_double_prom(self: State_Data, *args: Any) -> None:
        promotions.add(("double", args))

    with replace(State_Data, "_do_one_promotion", fake_single_prom), \
         replace(State_Data, "_do_double_promotion", fake_double_prom):
        state = State_Data.generate_empty_state()
        state.prices = Resources(1)
        state.sm.increase_price_factor = 1.5
        state.sm.nobles_cap = 1

        state.nobles.population = 20
        state.artisans.population = 30
        state.peasants.population = 40
        state.others.population = 50

        state.nobles.resources = Resources(500)
        state.artisans.resources = Resources(400)
        state.peasants.resources = Resources(300)
        state.others.resources = Resources(200)

        state.peasants.starving = True
        state.others.freezing = True
        state.artisans.starving = True
        state.artisans.freezing = True

        state._do_promotions()  # type: ignore

        assert promotions == set()


def test_do_promotions_nobles_cap():
    promotions: set[Any] = set()

    def fake_single_prom(self: State_Data, *args: Any) -> None:
        promotions.add(("single", args))

    def fake_double_prom(self: State_Data, *args: Any) -> None:
        promotions.add(("double", args))

    with replace(State_Data, "_do_one_promotion", fake_single_prom), \
         replace(State_Data, "_do_double_promotion", fake_double_prom):
        state = State_Data.generate_empty_state()
        state.prices = Resources(1)
        state.sm.increase_price_factor = 1.5
        state.sm.nobles_cap = 0.4

        state.nobles.population = 20
        state.artisans.population = 30
        state.peasants.population = 40
        state.others.population = 50

        state.nobles.resources = Resources(500)
        state.artisans.resources = Resources(400)
        state.peasants.resources = Resources(300)
        state.others.resources = Resources(200)

        state._do_promotions()  # type: ignore

        o_to_p_inc_price = (
            INBUILT_RESOURCES[Class_Name.peasants]
            - INBUILT_RESOURCES[Class_Name.others]
        ).worth(state.prices) * 1.5

        o_to_a_inc_price = (
            INBUILT_RESOURCES[Class_Name.artisans]
            - INBUILT_RESOURCES[Class_Name.others]
        ).worth(state.prices) * 1.5

        assert promotions == {
            ("double", (state.others, state.peasants, o_to_p_inc_price,
                        state.artisans, o_to_a_inc_price)),
        }


def test_get_personal_taxes():
    state = State_Data()
    populations = Arithmetic_Dict({
        Class_Name.nobles: 10,
        Class_Name.artisans: 20,
        Class_Name.peasants: 30,
        Class_Name.others: 40
    })
    net_worths = Arithmetic_Dict({
        Class_Name.nobles: 150,
        Class_Name.artisans: 200,
        Class_Name.peasants: 900,
        Class_Name.others: 100
    })
    state.sm.tax_rates["personal"] = Arithmetic_Dict({
        Class_Name.nobles: 0,
        Class_Name.artisans: 1,
        Class_Name.peasants: 1.5,
        Class_Name.others: 2
    })
    rel_tax = state._get_personal_taxes(  # type: ignore
        populations, net_worths
    )
    assert rel_tax == {
        Class_Name.nobles: 0,
        Class_Name.artisans: 0.1,
        Class_Name.peasants: 0.05,
        Class_Name.others: 0.8
    }


def test_get_property_taxes():
    state = State_Data()
    state.sm.tax_rates["property"] = Arithmetic_Dict({
        Class_Name.nobles: 0,
        Class_Name.artisans: 0.1,
        Class_Name.peasants: 0.15,
        Class_Name.others: 0.8
    })
    assert state._get_property_taxes(  # type: ignore
        ) == state.sm.tax_rates["property"]


def test_get_income_taxes():
    state = State_Data()
    state.sm.tax_rates["income"] = Arithmetic_Dict({
        Class_Name.nobles: 0.2,
        Class_Name.artisans: 0.5,
        Class_Name.peasants: 0.8,
        Class_Name.others: 1
    })
    net_worths_change = Arithmetic_Dict({
        Class_Name.nobles: 0,
        Class_Name.artisans: 80,
        Class_Name.peasants: 100,
        Class_Name.others: 160
    })
    net_worths = Arithmetic_Dict({
        Class_Name.nobles: 2000,
        Class_Name.artisans: 400,
        Class_Name.peasants: 400,
        Class_Name.others: 320
    })
    rel_tax = state._get_income_taxes(  # type: ignore
        net_worths_change, net_worths
    )
    assert rel_tax == {
        Class_Name.nobles: 0,
        Class_Name.artisans: 0.1,
        Class_Name.peasants: 0.2,
        Class_Name.others: 0.5
    }


def test_do_taxes():
    arguments: dict[str, Any] = {}

    def fake_personal(self: State_Data, *args: Any
                      ) -> Arithmetic_Dict[Class_Name]:
        arguments["personal"] = args
        return Arithmetic_Dict({
            Class_Name.nobles: 0.1,
            Class_Name.artisans: 0.2,
            Class_Name.peasants: 0.3,
            Class_Name.others: 0.4
        })

    def fake_income(self: State_Data, *args: Any
                    ) -> Arithmetic_Dict[Class_Name]:
        arguments["income"] = args
        return Arithmetic_Dict({
            Class_Name.nobles: 0.04,
            Class_Name.artisans: 0.03,
            Class_Name.peasants: 0.02,
            Class_Name.others: 0.01
        })

    def fake_property(self: State_Data, *args: Any
                      ) -> Arithmetic_Dict[Class_Name]:
        arguments["property"] = args
        return Arithmetic_Dict({
            Class_Name.nobles: 0.005,
            Class_Name.artisans: 0.006,
            Class_Name.peasants: 0.007,
            Class_Name.others: 0.8
        })

    with replace(State_Data, "_get_personal_taxes", fake_personal), \
         replace(State_Data, "_get_income_taxes", fake_income), \
         replace(State_Data, "_get_property_taxes", fake_property):
        state = State_Data.generate_empty_state()
        state.nobles.population = 20
        state.nobles.resources = Resources(10)
        state.artisans.population = 30
        state.artisans.resources = Resources(20)
        state.peasants.population = 40
        state.peasants.resources = Resources(40)
        state.others.population = 50
        state.others.resources = Resources({
            Resource.food: 50,
            Resource.wood: 100,
            Resource.stone: 50,
            Resource.iron: 50,
            Resource.tools: 100,
            Resource.land: 50
        })
        state.prices = Resources({
            Resource.food: 1,
            Resource.wood: 2,
            Resource.stone: 3,
            Resource.iron: 4,
            Resource.tools: 5,
            Resource.land: 5
        })

        net_worths = Arithmetic_Dict({
            name: social_class.net_worth
            for name, social_class
            in state.classes.items()
        })
        populations = Arithmetic_Dict({
            name: social_class.population
            for name, social_class
            in state.classes.items()
        })
        net_worths_change = Arithmetic_Dict({
            Class_Name.nobles: 60,
            Class_Name.artisans: 30,
            Class_Name.peasants: 40,
            Class_Name.others: 60
        })
        rel_tax = Arithmetic_Dict({
            Class_Name.nobles: 0.145,
            Class_Name.artisans: 0.236,
            Class_Name.peasants: 0.327,
            Class_Name.others: 1
        })

        tax = {
            social_class.class_name:
            social_class.real_resources * rel_tax[social_class.class_name]
            for social_class in state
        }
        after = {
            class_name:
            state.classes[class_name].resources - tax[class_name]
            for class_name in Class_Name
        }
        govt_after = sum(tax.values(), start=Resources())

        happiness = {
            class_name:
            Class.resources_seized_happiness(
                rel_tax[class_name] * net_worths[class_name]
                / populations[class_name])
            for class_name in Class_Name
        }

        state._do_taxes(net_worths - net_worths_change)  # type: ignore

        assert state.nobles.resources == after[Class_Name.nobles]
        assert state.artisans.resources == after[Class_Name.artisans]
        assert state.peasants.resources == after[Class_Name.peasants]
        assert state.others.resources == after[Class_Name.others]
        assert state.government.resources == govt_after

        assert state.nobles.happiness == approx(happiness[Class_Name.nobles])
        assert state.artisans.happiness == \
            approx(happiness[Class_Name.artisans])
        assert state.peasants.happiness == \
            approx(happiness[Class_Name.peasants])
        assert state.others.happiness == approx(happiness[Class_Name.others])

        assert arguments == {
            "personal": (populations, net_worths),
            "income": (net_worths_change, net_worths),
            "property": ()
        }


def test_get_flee_rate():
    for i in range(1000):
        assert State_Data._get_flee_rate(i) == 0  # type: ignore

    old_rate = 0
    for i in range(-1, -1000, -1):
        new_rate = State_Data._get_flee_rate(i)  # type: ignore
        assert new_rate >= old_rate
        assert 0 < new_rate <= 1
        old_rate = new_rate


def test_add_brigands():
    state = State_Data()
    assert state.brigands == 0

    state._add_brigands(10, 1)  # type: ignore
    assert state.brigands == 10
    assert state.brigands_strength == 1

    state._add_brigands(10, 0.5)  # type: ignore
    assert state.brigands == 20
    assert state.brigands_strength == approx(0.75)

    state._add_brigands(10, 2)  # type: ignore
    assert state.brigands == 30
    assert state.brigands_strength == approx(1.1667, abs=0.001)

    state._add_brigands(30, 0.8333333)  # type: ignore
    assert state.brigands == 60
    assert state.brigands_strength == approx(1, abs=0.001)


def test_total_population():
    state = State_Data()
    state.government = Government(
        state, soldiers=Soldiers({Soldier.knights: 10, Soldier.footmen: 30})
    )
    state.classes = {
        Class_Name.nobles: Nobles(state, 22),
        Class_Name.artisans: Artisans(state, 33),
        Class_Name.peasants: Peasants(state, 44),
        Class_Name.others: Others(state, 55)
    }
    state.brigands = 15
    assert state.total_population == 209

    state.brigands = 6
    assert state.total_population == 200

    state.peasants.population = 54
    assert state.total_population == 210

    state.nobles.population = 20
    assert state.total_population == 208

    state.government.soldiers.footmen = 12
    assert state.total_population == 190


def test_do_theft():
    def remaining_resources(class_: Class, prev: Resources) -> Resources:
        # part stolen is 0.05
        inbuilt = class_.real_resources - class_.resources
        stolen = (prev + inbuilt) * 0.05
        del stolen.land
        remaining = prev - stolen
        return remaining

    def happiness_after(class_: Class, prev: Resources) -> float:
        # part stolen is 0.05
        inbuilt = class_.real_resources - class_.resources
        stolen = (prev + inbuilt) * 0.05
        del stolen.land
        value = stolen.worth(class_.parent.prices)
        return Class.resources_seized_happiness(value / class_.population)

    state = State_Data.generate_empty_state()
    state.nobles.population = 20
    state.nobles.resources = Resources(10)
    state.artisans.population = 30
    state.artisans.resources = Resources(20)
    state.peasants.population = 40
    state.peasants.resources = Resources(40)
    state.others.population = 36
    others_res = Resources({
        Resource.food: 50,
        Resource.wood: 100,
        Resource.stone: 50,
        Resource.iron: 50,
        Resource.tools: 100,
        Resource.land: 50
    })
    state.others.resources = others_res.copy()
    state.government.resources = Resources(100)
    state.brigands = 14
    state.brigands_strength = 0

    state._do_theft()  # type: ignore

    assert state.nobles.population == 20
    assert state.nobles.resources == remaining_resources(
        state.nobles, Resources(10)
    )
    assert state.nobles.happiness == happiness_after(
        state.nobles, Resources(10)
    )

    assert state.artisans.population == 30
    assert state.artisans.resources == remaining_resources(
        state.artisans, Resources(20)
    )
    assert state.artisans.happiness == happiness_after(
        state.artisans, Resources(20)
    )

    assert state.peasants.population == 40
    assert state.peasants.resources == remaining_resources(
        state.peasants, Resources(40)
    )
    assert state.peasants.happiness == happiness_after(
        state.peasants, Resources(40)
    )

    assert state.others.population == 36
    assert state.others.resources == remaining_resources(
        state.others, others_res
    )
    assert state.others.happiness == happiness_after(
        state.others, others_res
    )

    assert state.government.resources == Resources({
        Resource.food: 95,
        Resource.wood: 95,
        Resource.stone: 95,
        Resource.iron: 95,
        Resource.tools: 95,
        Resource.land: 100
    })


def test_make_new_brigands():
    brigands_added: set[tuple[float, float]] = set()

    def fake_add_brigands(self: State_Data, *args: Any) -> None:
        brigands_added.add(args)

    with replace(State_Data, "_add_brigands", fake_add_brigands):
        state = State_Data.generate_empty_state()
        state.nobles.happiness = -20
        state.nobles.population = 100

        state.artisans.happiness = 10
        state.artisans.population = 120

        state.peasants.happiness = -50
        state.peasants.population = 200

        state.others.happiness = 0
        state.others.population = 12

        state.government = Government(state)
        state.government.soldiers = Soldiers({
            Soldier.knights: 20,
            Soldier.footmen: 80
        })
        state.government.missing_food = 40

        flee_rate_1 = State_Data._get_flee_rate(-20)  # type: ignore
        flee_rate_2 = State_Data._get_flee_rate(-50)  # type: ignore
        flee_rate_3 = State_Data._get_flee_rate(-40)  # type: ignore

        state._make_new_brigands()  # type: ignore

        assert brigands_added == {
            (100 * flee_rate_1, BRIGAND_STRENGTH_CLASS[Class_Name.nobles]),
            (200 * flee_rate_2, BRIGAND_STRENGTH_CLASS[Class_Name.peasants]),
            (20 * flee_rate_3, BRIGAND_STRENGTH_SOLDIER[Soldier.knights]),
            (80 * flee_rate_3, BRIGAND_STRENGTH_SOLDIER[Soldier.footmen])
        }
        assert state.nobles.population == 100 * (1 - flee_rate_1)
        assert state.artisans.population == 120
        assert state.peasants.population == 200 * (1 - flee_rate_2)
        assert state.others.population == 12
        assert state.government.soldiers.knights == 20 * (1 - flee_rate_3)
        assert state.government.soldiers.footmen == 80 * (1 - flee_rate_3)


def test_do_crime():
    did_theft = 0
    did_flee = 0

    def fake_do_theft(self: State_Data) -> None:
        nonlocal did_theft
        did_theft += 1

    def fake_make_new_brigands(self: State_Data) -> None:
        nonlocal did_flee
        did_flee += 1

    with replace(State_Data, "_do_theft", fake_do_theft), \
         replace(State_Data, "_make_new_brigands", fake_make_new_brigands):
        state = State_Data.generate_empty_state()
        state._do_crime()  # type: ignore

    assert did_theft == 1
    assert did_flee == 1


def test_do_month_exceptions():
    state = State_Data.generate_empty_state()
    with raises(EveryoneDeadError):
        state.do_month()

    state.nobles.population = 10
    state.nobles.happiness = 1.01 * REBELLION_THRESHOLD
    with raises(RebellionError):
        state.do_month()
    state.nobles.happiness = 0.5 * REBELLION_THRESHOLD

    state.artisans.population = 10
    state.others.population = 20
    state.others.happiness = 1.5 * REBELLION_THRESHOLD
    with raises(RebellionError):
        state.do_month()


def test_do_month():
    # all components have been tested before
    # tests calling of right methods - doesn't test their order
    # also shallowly tests the returned data
    P = ParamSpec("P")
    V = TypeVar("V")
    T = TypeVar("T")

    calls: set[str] = set()

    def log_to_set(class_name: str, method: Callable[P, V]) -> Callable[P, V]:
        def inner(*args: P.args, **kwargs: P.kwargs) -> V:
            calls.add(f"{class_name}.{method.__name__}")
            return method(*args, **kwargs)
        return inner

    def logged_class(class_: Type[T]) -> Type[T]:
        class New(class_):  # type: ignore
            pass

        for member in dir(New):
            method = getattr(New, member)
            if callable(method) and \
                    member not in {"__class__", "__new__", "__init__"}:
                setattr(New, member, log_to_set(class_.__name__, method))
        return New

    state = logged_class(State_Data)()
    state.classes = {
        Class_Name.nobles: logged_class(Nobles)(state, 20, Resources(10)),
        Class_Name.artisans: logged_class(Artisans)(state, 30, Resources(20)),
        Class_Name.peasants: logged_class(Peasants)(state, 40, Resources(30)),
        Class_Name.others: logged_class(Others)(state, 50, Resources(40))
    }
    state.government = logged_class(Government)(state)
    state._market = logged_class(Market)(  # type: ignore
        list[SupportsTrade](state) + [state.government], state
    )

    old_resources = {
        "nobles": state.nobles.real_resources,
        "artisans": state.artisans.real_resources,
        "peasants": state.peasants.real_resources,
        "others": state.others.real_resources,
        "government": state.government.real_resources
    }

    state.nobles.happiness = 10
    state.artisans.happiness = 10
    state.peasants.happiness = 10
    state.others.happiness = 10

    state.brigands = 10
    state.brigands_strength = 0.9

    state.prices = DEFAULT_PRICES * 1.5

    returns = state.do_month()

    assert "State_Data._do_growth" in calls
    for social_class in state:
        assert \
            f"{social_class.class_name.name.title()}.decay_happiness" in calls
        assert f"{social_class.class_name.name.title()}.produce" in calls
        assert f"{social_class.class_name.name.title()}.consume" in calls
    assert "Government.consume" in calls
    assert "State_Data._employ" in calls
    assert "State_Data._do_crime" in calls
    assert "State_Data._do_taxes" in calls
    assert "State_Data._reset_flags" in calls
    assert "State_Data._do_demotions" in calls
    assert "State_Data._do_starvation" in calls
    assert "State_Data._secure_classes" in calls
    assert "State_Data._do_promotions" in calls
    assert "Market.do_trade" in calls
    assert "State_Data._advance_month" in calls

    assert returns["prices"] == state.prices.to_raw_dict()
    assert returns["resources_after"] == {
        "nobles": state.nobles.real_resources.to_raw_dict(),
        "artisans": state.artisans.real_resources.to_raw_dict(),
        "peasants": state.peasants.real_resources.to_raw_dict(),
        "others": state.others.real_resources.to_raw_dict(),
        "government": state.government.real_resources.to_raw_dict()
    }
    assert returns["population_after"] == {
        "nobles": state.nobles.population,
        "artisans": state.artisans.population,
        "peasants": state.peasants.population,
        "others": state.others.population
    }
    assert returns["change_resources"] == {
        "nobles": (state.nobles.real_resources
                   - old_resources["nobles"]).to_raw_dict(),
        "artisans": (state.artisans.real_resources
                     - old_resources["artisans"]).to_raw_dict(),
        "peasants": (state.peasants.real_resources
                     - old_resources["peasants"]).to_raw_dict(),
        "others": (state.others.real_resources
                   - old_resources["others"]).to_raw_dict(),
        "government": (state.government.real_resources
                       - old_resources["government"]).to_raw_dict()
    }
    assert returns["change_population"] == {
        "nobles": state.nobles.population - 20,
        "artisans": state.artisans.population - 30,
        "peasants": state.peasants.population - 40,
        "others": state.others.population - 50
    }
    assert returns["growth_modifiers"] == {
        "nobles": {
            "starving": state.nobles.starving,
            "freezing": state.nobles.freezing,
            "promoted_to": state.nobles.promoted_to,
            "promoted_from": state.nobles.promoted_from,
            "demoted_to": state.nobles.demoted_to,
            "demoted_from": state.nobles.demoted_from
        },
        "artisans": {
            "starving": state.artisans.starving,
            "freezing": state.artisans.freezing,
            "promoted_to": state.artisans.promoted_to,
            "promoted_from": state.artisans.promoted_from,
            "demoted_to": state.artisans.demoted_to,
            "demoted_from": state.artisans.demoted_from
        },
        "peasants": {
            "starving": state.peasants.starving,
            "freezing": state.peasants.freezing,
            "promoted_to": state.peasants.promoted_to,
            "promoted_from": state.peasants.promoted_from,
            "demoted_to": state.peasants.demoted_to,
            "demoted_from": state.peasants.demoted_from
        },
        "others": {
            "starving": state.others.starving,
            "freezing": state.others.freezing,
            "promoted_to": state.others.promoted_to,
            "promoted_from": state.others.promoted_from,
            "demoted_to": state.others.demoted_to,
            "demoted_from": state.others.demoted_from
        }
    }
    assert returns["employees"] == {
        "nobles": state.nobles.employees,
        "artisans": state.artisans.employees,
        "peasants": state.peasants.employees,
        "others": state.others.employees,
        "government": state.government.employees
    }
    assert returns["wages"] == {
        "nobles": state.nobles.old_wage,
        "artisans": state.artisans.old_wage,
        "peasants": state.peasants.old_wage,
        "others": state.others.old_wage,
        "government": state.government.old_wage
    }
    assert returns["happiness"] == {
        "nobles": state.nobles.happiness,
        "artisans": state.artisans.happiness,
        "peasants": state.peasants.happiness,
        "others": state.others.happiness
    }
