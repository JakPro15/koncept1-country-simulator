from sources.auxiliaries.constants import EMPTY_RESOURCES
from sources.state.government import Government
from ..sources.abstract_interface.interface import Interface
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
    state.government = Government(state, resources)
    nobles = Nobles(state, 100, EMPTY_RESOURCES)
    state._classes = [nobles]

    history = History({}, ["next 6"])

    interface = Interface()
    interface.state = state
    interface.history = history

    interface.transfer_resources("nobles", "food", 100)

    assert state.transfers == [["nobles", "food", 100]]
    assert history.history_lines == [
        "next 6",
        "transfer nobles food 100"
    ]

    State_Data.do_transfer = old_do_transfer
