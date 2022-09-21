from ..sources.abstract_interface.history import History
from ..sources.state.state_data import State_Data
from ..sources.auxiliaries.testing import replace


def test_constructor():
    a = {"a": 1}
    b = ["a", "b", "c"]
    history = History(a, b)

    assert history.starting_state_dict == a
    assert history.starting_state_dict is not a
    assert history.history_lines == b
    assert history.history_lines is not b


def test_obtain_whole_history():
    commands_done: list[str] = []
    month = 0

    def fake_execute_commands(self: State_Data, commands: list[str]) -> None:
        commands_done.extend(commands)

    def fake_do_month(self: State_Data) -> int:
        nonlocal month
        month += 1
        commands_done.append(f"did_month {month}")
        return month

    with replace(State_Data, "execute_commands", fake_execute_commands), \
         replace(State_Data, "do_month", fake_do_month):
        history = History(State_Data.generate_empty_state().to_dict(),
                          ["next 2", "abcde", "next 1", "ex"])
        data = history.obtain_whole_history()
        assert data == [1, 2, 3]
        assert commands_done == ["did_month 1", "did_month 2", "abcde",
                                 "did_month 3", "ex"]


def test_population():
    def fake_whole_history(self: History) -> list[dict[str, int]]:
        return [{"population_after": i} for i in range(4)]

    with replace(History, "obtain_whole_history", fake_whole_history):
        history = History({}, [])
        assert history.population() == [0, 1, 2, 3]


def test_resources():
    def fake_whole_history(self: History) -> list[dict[str, int]]:
        return [{"resources_after": i} for i in range(4)]

    with replace(History, "obtain_whole_history", fake_whole_history):
        history = History({}, [])
        assert history.resources() == [0, 1, 2, 3]


def test_population_change():
    def fake_whole_history(self: History) -> list[dict[str, int]]:
        return [{"change_population": i} for i in range(4)]

    with replace(History, "obtain_whole_history", fake_whole_history):
        history = History({}, [])
        assert history.population_change() == [0, 1, 2, 3]


def test_resources_change():
    def fake_whole_history(self: History) -> list[dict[str, int]]:
        return [{"change_resources": i} for i in range(4)]

    with replace(History, "obtain_whole_history", fake_whole_history):
        history = History({}, [])
        assert history.resources_change() == [0, 1, 2, 3]


def test_prices():
    def fake_whole_history(self: History) -> list[dict[str, int]]:
        return [{"prices": i} for i in range(4)]

    with replace(History, "obtain_whole_history", fake_whole_history):
        history = History({}, [])
        assert history.prices() == [0, 1, 2, 3]


def test_total_resources():
    def fake_whole_history(self: History
                           ) -> list[dict[str, dict[str, dict[str, float]]]]:
        return [
            {"resources_after": {
                f"class{j}": {
                    "food": i,
                    "wood": j * i,
                    "stone": j * i * i,
                    "iron": j + i,
                    "tools": j
                }
                for j in range(3)
            }}
            for i in range(4)
        ]

    with replace(History, "obtain_whole_history", fake_whole_history):
        history = History({}, [])
        assert history.total_resources() == [{
            "food": 0, "wood": 0, "stone": 0,
            "iron": 3, "tools": 3, "land": 0
        }, {
            "food": 3, "wood": 3, "stone": 3,
            "iron": 6, "tools": 3, "land": 0
        }, {
            "food": 6, "wood": 6, "stone": 12,
            "iron": 9, "tools": 3, "land": 0
        }, {
            "food": 9, "wood": 9, "stone": 27,
            "iron": 12, "tools": 3, "land": 0
        }
        ]


def test_growth_modifiers():
    def fake_whole_history(self: History) -> list[dict[str, int]]:
        return [{"growth_modifiers": i} for i in range(4)]

    with replace(History, "obtain_whole_history", fake_whole_history):
        history = History({}, [])
        assert history.growth_modifiers() == [0, 1, 2, 3]


def test_employment():
    def fake_whole_history(self: History) -> list[dict[str, dict[str, int]]]:
        return [{"employees": {"class1": i, "class2": i + 2},
                 "wages": {"class1": 3 - i, "class2": 5 - i}}
                for i in range(4)]

    with replace(History, "obtain_whole_history", fake_whole_history):
        history = History({}, [])
        assert history.employment() == [{"class1": (i, 3 - i),
                                         "class2": (i + 2, 5 - i)}
                                        for i in range(4)]


def test_happiness():
    def fake_whole_history(self: History) -> list[dict[str, int]]:
        return [{"happiness": i} for i in range(4)]

    with replace(History, "obtain_whole_history", fake_whole_history):
        history = History({}, [])
        assert history.happiness() == [0, 1, 2, 3]


def test_add_history_line():
    history = History({}, [])
    history.add_history_line("next")
    assert history.history_lines == [
        "next 1"
    ]
    history.add_history_line("next")
    assert history.history_lines == [
        "next 2"
    ]
    history.add_history_line("transfer nobles food 100")
    assert history.history_lines == [
        "next 2",
        "transfer nobles food 100"
    ]
    history.add_history_line("next")
    assert history.history_lines == [
        "next 2",
        "transfer nobles food 100",
        "next 1"
    ]
