from ..sources.abstract_interface.interface import Interface
from ..sources.abstract_interface.history import History
from ..sources.state.state_data import State_Data


def test_next_month_first():
    def fake_do_month(self):
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
    def fake_do_month(self):
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
