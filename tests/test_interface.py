from pytest import raises
from sources.state.government import Government
from ..sources.abstract_interface.interface import (
    Interface,
    NotEnoughClassResources,
    NotEnoughGovtResources
)
from ..sources.abstract_interface.history import History
from ..sources.state.state_data import State_Data
from ..sources.state.social_classes.nobles import Nobles


def test_next_month_first():
    def fake_do_month(self, debug=False):
        self.did_month += 1

    old_do_month = State_Data.do_month
    State_Data.do_month = fake_do_month

    state = State_Data()
    state.did_month = 0

    history = History({}, [])

    interface = Interface()
    interface.state = state
    interface.history = history

    interface.next_month()

    assert state.did_month == 1
    assert history.history_lines == ["next 1"]

    State_Data.do_month = old_do_month


def test_next_month_next():
    def fake_do_month(self, debug=False):
        self.did_month += 1

    old_do_month = State_Data.do_month
    State_Data.do_month = fake_do_month

    state = State_Data()
    state.did_month = 0

    history = History({}, ["next 6"])

    interface = Interface()
    interface.state = state
    interface.history = history

    interface.next_month()

    assert state.did_month == 1
    assert history.history_lines == ["next 7"]

    State_Data.do_month = old_do_month


def test_transfer():
    def fake_do_transfer(self, class_name, resource, amount):
        self.transfers.append([class_name, resource, amount])

    old_do_transfer = State_Data.do_transfer
    State_Data.do_transfer = fake_do_transfer

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

    State_Data.do_transfer = old_do_transfer


def test_secure():
    def fake_do_secure(self, resource, amount):
        self.secures.append([resource, amount])

    old_do_secure = State_Data.do_secure
    State_Data.do_secure = fake_do_secure

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

    State_Data.do_secure = old_do_secure


def test_optimal():
    def fake_do_optimal(self, resource, amount):
        self.optimals.append([resource, amount])

    old_do_optimal = State_Data.do_optimal
    State_Data.do_optimal = fake_do_optimal

    state = State_Data()
    state.optimals = []
    state.government = Government(state)

    history = History({}, ["next 6"])

    interface = Interface()
    interface.state = state
    interface.history = history

    interface.set_govt_optimal("food", 100)
    with raises(AssertionError):
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

    State_Data.do_optimal = old_do_optimal


def test_set_law():
    def fake_do_set_law(self, resource, social_class, amount):
        self.setlaws.append([resource, social_class, amount])

    old_do_set_law = State_Data.do_set_law
    State_Data.do_set_law = fake_do_set_law

    state = State_Data()
    state.setlaws = []
    state.government = Government(state)

    history = History({}, ["next 6"])

    interface = Interface()
    interface.state = state
    interface.history = history

    interface.set_law("tax_personal", "nobles", 100)
    with raises(AssertionError):
        interface.set_law("tax_property", "nobles", 2)
    with raises(AssertionError):
        interface.set_law("tax_income", "nobles", -0.1)
    with raises(AssertionError):
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

    State_Data.do_set_law = old_do_set_law
