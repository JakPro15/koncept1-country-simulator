from ..sources.abstract_interface.history import History
from ..sources.state.state_data import State_Data
from ..sources.auxiliaries.constants import EMPTY_RESOURCES


def test_constructor():
    a = {"a": 1}
    b = ["a", "b", "c"]
    history = History(a, b)

    assert history.starting_state_dict == a
    assert history.starting_state_dict is not a
    assert history.history_lines == b
    assert history.history_lines is not b


class Fake_State_Data:
    def __init__(self):
        pass

    def do_month(self):
        return {
            "population_after": {
                "a": 3.4635635,
                "b": -13.4563544524,
                "c": 4.45324
            },
            "resources_after": {
                "nobles": {
                    "food": 2.3564755,
                    "wood": 4.57462335656
                },
                "artisans": EMPTY_RESOURCES.copy(),
                "peasants": {
                    "food": 4.3554,
                    "a": 3636.363636
                },
                "others": EMPTY_RESOURCES.copy()
            },
            "population_change": {
                "a": 3.4635635,
                "b": -13.4563544524,
                "c": 4.45324,
                "d": 0
            },
            "resources_change": {
                "nobles": EMPTY_RESOURCES.copy(),
                "artisans": EMPTY_RESOURCES.copy(),
                "peasants": {"a": 3636.363636},
                "others": EMPTY_RESOURCES.copy()
            },
            "prices": {
                "a": 3.4635635,
                "b": -13.4563544524,
                "c": 4.45324,
                "d": 0.00000001
            },
            "abc": {
                "a": 3.4635635,
                "b": -13.4563544524,
                "c": 4.45324
            }
        }


def test_obtain_data_1():
    def fake_from_dict(dict):
        return Fake_State_Data()

    old_from_dict = State_Data.from_dict
    State_Data.from_dict = fake_from_dict

    a = {}
    b = ["next 11", "next 1"]
    history = History(a, b)
    data = history.obtain_data("resources_after", True, 3)

    assert len(data) == 12
    for month_data in data:
        assert month_data == {
            "nobles": {
                "food": 2.356,
                "wood": 4.575
            },
            "artisans": EMPTY_RESOURCES.copy(),
            "peasants": {
                "food": 4.355,
                "a": 3636.364
            },
            "others": EMPTY_RESOURCES.copy()
        }

    State_Data.from_dict = old_from_dict


def test_obtain_data_2():
    def fake_from_dict(dict):
        return Fake_State_Data()

    old_from_dict = State_Data.from_dict
    State_Data.from_dict = fake_from_dict

    a = {}
    b = ["next 100"]
    history = History(a, b)
    data = history.obtain_data("abc", False)

    assert len(data) == 100
    for month_data in data:
        assert month_data == {
            "a": 3,
            "b": -13,
            "c": 4
        }

    State_Data.from_dict = old_from_dict


def test_round_dict_values():
    dicti = {
        "a": 34545.435346,
        "b": 67.4356,
        "c": -214.2,
        "d": 0
    }
    assert History.round_dict_values(dicti, 2) == {
        "a": 34545.44,
        "b": 67.44,
        "c": -214.2,
        "d": 0
    }


def test_round_dict_values_default_precision():
    dicti = {
        "a": 34545.435346,
        "b": 67.4356,
        "c": -214.2,
        "d": 0
    }
    assert History.round_dict_values(dicti) == {
        "a": 34545,
        "b": 67,
        "c": -214,
        "d": 0
    }


def test_round_dict_of_dicts_values():
    dicti = {
        "ab": {
            "a": 34545.435346,
            "b": 67.4356
        },
        "cd": {
            "c": -214.2,
            "d": 0.009
        }
    }
    assert History.round_dict_of_dicts_values(dicti, 2) == {
        "ab": {
            "a": 34545.44,
            "b": 67.44
        },
        "cd": {
            "c": -214.2,
            "d": 0.01
        }
    }


def test_round_dict_of_dicts_values_default_precision():
    dicti = {
        "ab": {
            "a": 34545.435346,
            "b": 67.4356
        },
        "cd": {
            "c": -214.2,
            "d": 0.009
        }
    }
    assert History.round_dict_of_dicts_values(dicti) == {
        "ab": {
            "a": 34545,
            "b": 67
        },
        "cd": {
            "c": -214,
            "d": 0
        }
    }


def test_population():
    def fake_from_dict(dict):
        return Fake_State_Data()

    old_from_dict = State_Data.from_dict
    State_Data.from_dict = fake_from_dict

    a = {}
    b = ["next 100"]
    history = History(a, b)
    data = history.population()

    assert len(data) == 100
    for month_data in data:
        assert month_data == {
            "a": 3,
            "b": -13,
            "c": 4
        }

    State_Data.from_dict = old_from_dict


def test_resources():
    def fake_from_dict(dict):
        return Fake_State_Data()

    old_from_dict = State_Data.from_dict
    State_Data.from_dict = fake_from_dict

    a = {}
    b = ["next 100"]
    history = History(a, b)
    data = history.resources()

    assert len(data) == 100
    for month_data in data:
        assert month_data == {
            "nobles": {
                "food": 2.4,
                "wood": 4.6
            },
            "artisans": EMPTY_RESOURCES.copy(),
            "peasants": {
                "food": 4.4,
                "a": 3636.4
            },
            "others": EMPTY_RESOURCES.copy()
        }

    State_Data.from_dict = old_from_dict


def test_population_change():
    def fake_from_dict(dict):
        return Fake_State_Data()

    old_from_dict = State_Data.from_dict
    State_Data.from_dict = fake_from_dict

    a = {}
    b = ["next 100"]
    history = History(a, b)
    data = history.population_change()

    assert len(data) == 100
    for month_data in data:
        assert month_data == {
            "a": 3,
            "b": -13,
            "c": 4,
            "d": 0
        }

    State_Data.from_dict = old_from_dict


def test_resources_change():
    def fake_from_dict(dict):
        return Fake_State_Data()

    old_from_dict = State_Data.from_dict
    State_Data.from_dict = fake_from_dict

    a = {}
    b = ["next 100"]
    history = History(a, b)
    data = history.resources_change()

    assert len(data) == 100
    for month_data in data:
        assert month_data == {
            "nobles": EMPTY_RESOURCES.copy(),
            "artisans": EMPTY_RESOURCES.copy(),
            "peasants": {"a": 3636.4},
            "others": EMPTY_RESOURCES.copy()
        }

    State_Data.from_dict = old_from_dict


def test_prices():
    def fake_from_dict(dict):
        return Fake_State_Data()

    old_from_dict = State_Data.from_dict
    State_Data.from_dict = fake_from_dict

    a = {}
    b = ["next 100"]
    history = History(a, b)
    data = history.prices()

    assert len(data) == 100
    for month_data in data:
        assert month_data == {
            "a": 3.4636,
            "b": -13.4564,
            "c": 4.4532,
            "d": 0.0000
        }

    State_Data.from_dict = old_from_dict


def test_total_resources():
    def fake_from_dict(dict):
        return Fake_State_Data()

    old_from_dict = State_Data.from_dict
    State_Data.from_dict = fake_from_dict

    a = {}
    b = ["next 100"]
    history = History(a, b)
    data = history.total_resources()

    assert len(data) == 100
    for month_data in data:
        assert month_data == {
            "food": 6.7,
            "wood": 4.6,
            "stone": 0,
            "iron": 0,
            "tools": 0,
            "land": 0,
            "a": 3636.4
        }

    State_Data.from_dict = old_from_dict
