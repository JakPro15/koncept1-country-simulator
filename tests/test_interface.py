from pytest import raises
from sources.auxiliaries.constants import INBUILT_RESOURCES, RECRUITMENT_COST
from sources.state.government import Government
from ..sources.abstract_interface.interface import (
    Interface,
    NotEnoughClassPopulation,
    NotEnoughClassResources,
    NotEnoughGovtResources,
    InvalidArgumentError
)
from ..sources.abstract_interface.history import History
from ..sources.state.state_data import State_Data
from ..sources.state.social_classes.nobles import Nobles
from ..sources.auxiliaries.testing import replace


def fake_do_month(self, debug=False):
    self.did_month += 1


def test_next_month_first():
    with replace(State_Data, "do_month", fake_do_month):
        state = State_Data()
        state.did_month = 0

        history = History({}, [])

        interface = Interface()
        interface.state = state
        interface.history = history

        interface.next_month()

        assert state.did_month == 1
        assert history.history_lines == ["next 1"]


def test_next_month_next():
    with replace(State_Data, "do_month", fake_do_month):
        state = State_Data()
        state.did_month = 0

        history = History({}, ["next 6"])

        interface = Interface()
        interface.state = state
        interface.history = history

        interface.next_month()

        assert state.did_month == 1
        assert history.history_lines == ["next 7"]


def test_transfer():
    def fake_do_transfer(self, class_name, resource, amount):
        self.transfers.append([class_name, resource, amount])

    with replace(State_Data, "do_transfer", fake_do_transfer):
        state = State_Data()
        state.transfers = []
        resources = {
            "food": 300,
            "wood": 300,
            "stone": 300,
            "iron": 300,
            "tools": 300,
            "land": 300,
        }
        resources2 = {
            "food": 100,
            "wood": 100,
            "stone": 100,
            "iron": 100,
            "tools": 100,
            "land": 100,
        }
        state.government = Government(state, resources)
        nobles = Nobles(state, 100, resources2)
        state._classes = [nobles]

        history = History({}, ["next 6"])

        interface = Interface()
        interface.state = state
        interface.history = history

        interface.transfer_resources("nobles", "food", 100)
        with raises(NotEnoughGovtResources):
            interface.transfer_resources("nobles", "food", 350)
        with raises(NotEnoughClassResources):
            interface.transfer_resources("nobles", "food", -150)

        assert state.transfers == [["nobles", "food", 100]]
        assert history.history_lines == [
            "next 6",
            "transfer nobles food 100"
        ]


def test_secure():
    def fake_do_secure(self, resource, amount):
        self.secures.append([resource, amount])

    with replace(State_Data, "do_secure", fake_do_secure):
        state = State_Data()
        state.secures = []
        resources = {
            "food": 300,
            "wood": 300,
            "stone": 300,
            "iron": 300,
            "tools": 300,
            "land": 300,
        }
        resources2 = {
            "food": 100,
            "wood": 100,
            "stone": 100,
            "iron": 100,
            "tools": 100,
            "land": 100,
        }
        state.government = Government(state, resources, secure_res=resources2)

        history = History({}, ["next 6"])

        interface = Interface()
        interface.state = state
        interface.history = history

        interface.secure_resources("food", 100)
        with raises(NotEnoughGovtResources):
            interface.secure_resources("food", 350)
        with raises(NotEnoughGovtResources):
            interface.secure_resources("food", -150)

        assert state.secures == [["food", 100]]
        assert history.history_lines == [
            "next 6",
            "secure food 100"
        ]

        interface.secure_resources("iron", None)
        assert state.secures == [
            ["food", 100],
            ["iron", 300]
        ]
        assert history.history_lines == [
            "next 6",
            "secure food 100",
            "secure iron 300"
        ]


def test_optimal():
    def fake_do_optimal(self, resource, amount):
        self.optimals.append([resource, amount])

    with replace(State_Data, "do_optimal", fake_do_optimal):
        state = State_Data()
        state.optimals = []
        state.government = Government(state)

        history = History({}, ["next 6"])

        interface = Interface()
        interface.state = state
        interface.history = history

        interface.set_govt_optimal("food", 100)
        with raises(InvalidArgumentError):
            interface.set_govt_optimal("wood", -100)

        assert state.optimals == [["food", 100]]
        assert history.history_lines == [
            "next 6",
            "optimal food 100"
        ]

        interface.set_govt_optimal("iron", 50)
        assert state.optimals == [
            ["food", 100],
            ["iron", 50]
        ]
        assert history.history_lines == [
            "next 6",
            "optimal food 100",
            "optimal iron 50"
        ]

        interface.set_govt_optimal("land", 0)
        assert state.optimals == [
            ["food", 100],
            ["iron", 50],
            ["land", 0]
        ]
        assert history.history_lines == [
            "next 6",
            "optimal food 100",
            "optimal iron 50",
            "optimal land 0"
        ]


def test_set_law():
    def fake_do_set_law(self, resource, social_class, amount):
        self.setlaws.append([resource, social_class, amount])

    with replace(State_Data, "do_set_law", fake_do_set_law):
        state = State_Data()
        state.setlaws = []
        state.government = Government(state)

        history = History({}, ["next 6"])

        interface = Interface()
        interface.state = state
        interface.history = history

        interface.set_law("tax_personal", "nobles", 100)
        with raises(InvalidArgumentError):
            interface.set_law("tax_property", "nobles", 2)
        with raises(InvalidArgumentError):
            interface.set_law("tax_income", "nobles", -0.1)
        with raises(InvalidArgumentError):
            interface.set_law("wage_minimum", None, 1.2)

        assert state.setlaws == [["tax_personal", "nobles", 100]]
        assert history.history_lines == [
            "next 6",
            "laws set tax_personal nobles 100"
        ]

        interface.set_law("wage_minimum", None, 0.99)
        assert state.setlaws == [
            ["tax_personal", "nobles", 100],
            ["wage_minimum", None, 0.99]
        ]
        assert history.history_lines == [
            "next 6",
            "laws set tax_personal nobles 100",
            "laws set wage_minimum None 0.99"
        ]

        interface.set_law("tax_income", "artisans", 0.01)
        assert state.setlaws == [
            ["tax_personal", "nobles", 100],
            ["wage_minimum", None, 0.99],
            ["tax_income", "artisans", 0.01]
        ]
        assert history.history_lines == [
            "next 6",
            "laws set tax_personal nobles 100",
            "laws set wage_minimum None 0.99",
            "laws set tax_income artisans 0.01"
        ]


def test_force_promotion():
    def fake_do_force_promotion(self, class_name, amount):
        self.force_promotions.append([class_name, amount])

    class Fake_Class:
        def __init__(self, population, name):
            self.population = population
            self.class_name = name

    with replace(State_Data, "do_force_promotion", fake_do_force_promotion):
        state = State_Data()
        state._classes = [
            Fake_Class(50, "nobles"),
            Fake_Class(50, "artisans"),
            Fake_Class(60, "peasants"),
            Fake_Class(200, "others"),
        ]
        state._classes[0].lower_class = state._classes[2]
        state._classes[1].lower_class = state._classes[3]
        state._classes[2].lower_class = state._classes[3]
        state._classes[3].lower_class = state._classes[3]
        state.force_promotions = []
        state.government = Government(state)
        state.government.new_resources = (INBUILT_RESOURCES["peasants"] -
                                          INBUILT_RESOURCES["others"]) * 100
        state.government.flush()

        history = History({}, ["next 6"])

        interface = Interface()
        interface.state = state
        interface.history = history

        interface.force_promotion("peasants", 60)
        with raises(InvalidArgumentError):
            interface.force_promotion("peasants", -1)
        with raises(NotEnoughClassPopulation):
            interface.force_promotion("nobles", 61)
        with raises(NotEnoughGovtResources):
            interface.force_promotion("peasants", 101)

        assert state.force_promotions == [["peasants", 60]]
        assert history.history_lines == [
            "next 6",
            "promote peasants 60"
        ]

        state.government.new_resources = (INBUILT_RESOURCES["nobles"] -
                                          INBUILT_RESOURCES["peasants"]) * 20
        state.government.flush()

        interface.force_promotion("nobles", 20)
        with raises(NotEnoughGovtResources):
            interface.force_promotion("nobles", 21)

        assert state.force_promotions == [
            ["peasants", 60],
            ["nobles", 20]
        ]
        assert history.history_lines == [
            "next 6",
            "promote peasants 60",
            "promote nobles 20"
        ]

        state.government.new_resources = (INBUILT_RESOURCES["artisans"] -
                                          INBUILT_RESOURCES["others"]) * 20
        state.government.flush()

        interface.force_promotion("artisans", 20)
        with raises(NotEnoughGovtResources):
            interface.force_promotion("artisans", 21)

        assert state.force_promotions == [
            ["peasants", 60],
            ["nobles", 20],
            ["artisans", 20]
        ]
        assert history.history_lines == [
            "next 6",
            "promote peasants 60",
            "promote nobles 20",
            "promote artisans 20"
        ]


def test_recruit():
    def fake_do_recruit(self, class_name, amount):
        self.recruits.append([class_name, amount])

    class Fake_Class:
        def __init__(self, population, name):
            self.population = population
            self.class_name = name

    with replace(State_Data, "do_recruit", fake_do_recruit):
        state = State_Data()
        state._classes = [
            Fake_Class(300, "nobles"),
            Fake_Class(50, "artisans"),
            Fake_Class(60, "peasants"),
            Fake_Class(200000, "others"),
        ]
        state.recruits = []
        state.government = Government(state, RECRUITMENT_COST["knights"] * 40)

        history = History({}, ["next 6"])

        interface = Interface()
        interface.state = state
        interface.history = history

        interface.recruit("nobles", 30)
        with raises(InvalidArgumentError):
            interface.recruit("peasants", -1)
        with raises(NotEnoughClassPopulation):
            interface.recruit("peasants", 61)
        with raises(NotEnoughGovtResources):
            interface.recruit("nobles", 101)

        assert state.recruits == [["nobles", 30]]
        assert history.history_lines == [
            "next 6",
            "recruit nobles 30"
        ]

        interface.recruit("artisans", 40)
        with raises(NotEnoughGovtResources):
            interface.recruit("others", 21000)

        assert state.recruits == [
            ["nobles", 30],
            ["artisans", 40]
        ]
        assert history.history_lines == [
            "next 6",
            "recruit nobles 30",
            "recruit artisans 40"
        ]


def test_get_brigands():
    class EmptyState:
        def __init__(self, brig, strength):
            self.brigands = brig
            self.brigand_strength = strength
    interface = Interface()
    interface.state = EmptyState(24, 0.7)
    brigands, strength = interface.get_brigands(True)
    assert brigands == 24
    assert strength == 0.7

    brigands, strength = interface.get_brigands(False)
    assert brigands == (20, 30)
    assert strength == (0.5, 1)

    interface.state.brigands = 100
    interface.state.brigand_strength = 1.999
    brigands, strength = interface.get_brigands(False)
    assert brigands == (100, 200)
    assert strength == (1.5, 2)

    interface.state.brigands = 6
    interface.state.brigand_strength = 2
    brigands, strength = interface.get_brigands(False)
    assert brigands == (0, 10)
    assert strength == (2, 2.5)

    interface.state.brigands = 0
    interface.state.brigand_strength = 1
    brigands, strength = interface.get_brigands(False)
    assert brigands == (0, 10)
    assert strength == (1, 1.5)
