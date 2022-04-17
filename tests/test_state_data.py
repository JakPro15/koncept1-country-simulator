from ..sources.state.state_data import (
    State_Data, Nobles, Artisans, Peasants, Others
)
from ..sources.auxiliaries.constants import DEFAULT_PRICES
from ..sources.auxiliaries.arithmetic_dict import Arithmetic_Dict
from pytest import approx


def test_constructor():
    state = State_Data("August")
    assert state.month == "August"
    assert state.payments == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }
    assert state.prices == DEFAULT_PRICES


def test_default_constructor():
    state = State_Data()
    assert state.month == "January"
    assert state.payments == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }
    assert state.prices == DEFAULT_PRICES


def test_advance_month():
    state = State_Data("August")
    assert state.year == 0
    assert state.month == "August"
    state._advance_month()
    assert state.year == 0
    assert state.month == "September"
    state._advance_month()
    assert state.year == 0
    assert state.month == "October"
    state._advance_month()
    assert state.year == 0
    assert state.month == "November"
    state._advance_month()
    assert state.year == 0
    assert state.month == "December"
    state._advance_month()
    assert state.year == 1
    assert state.month == "January"


def test_create_market():
    state = State_Data()
    classes = [1, 2, 3]
    state._classes = [1, 2, 3]
    state._create_market()
    assert state._market.classes == classes


def test_from_dict():
    state = State_Data()
    data = {
        "year": 3,
        "month": "June",
        "classes": {
            "nobles": {
                "population": 20,
                "resources": {
                    "food": 21,
                    "wood": 22,
                    "stone": 23,
                    "iron": 24,
                    "tools": 25
                },
                "land": {
                    "fields": 26,
                    "woods": 27,
                    "stone_mines": 28,
                    "iron_mines": 29
                }
            },
            "artisans": {
                "population": 30,
                "resources": {
                    "food": 31,
                    "wood": 32,
                    "stone": 33,
                    "iron": 34,
                    "tools": 35
                },
                "land": {
                    "fields": 0,
                    "woods": 0,
                    "stone_mines": 0,
                    "iron_mines": 0
                }
            },
            "peasants": {
                "population": 40,
                "resources": {
                    "food": 41,
                    "wood": 42,
                    "stone": 43,
                    "iron": 44,
                    "tools": 45
                },
                "land": {
                    "fields": 46,
                    "woods": 47,
                    "stone_mines": 0,
                    "iron_mines": 0
                }
            },
            "others": {
                "population": 50,
                "resources": {
                    "food": 51,
                    "wood": 52,
                    "stone": 53,
                    "iron": 54,
                    "tools": 55
                },
                "land": {
                    "fields": 0,
                    "woods": 0,
                    "stone_mines": 0,
                    "iron_mines": 0
                }
            }
        },
        "prices": {
            "food": 0.1,
            "wood": 0.2,
            "stone": 0.3,
            "iron": 1.4,
            "tools": 0.5
        }
    }
    state.from_dict(data)
    assert state.year == 3
    assert state.month == "June"

    assert isinstance(state.classes[0], Nobles)
    assert state.classes[0].population == 20
    assert state.classes[0].resources == {
        "food": 21,
        "wood": 22,
        "stone": 23,
        "iron": 24,
        "tools": 25
    }
    assert state.classes[0].land == {
        "fields": 26,
        "woods": 27,
        "stone_mines": 28,
        "iron_mines": 29
    }

    assert isinstance(state.classes[1], Artisans)
    assert state.classes[1].population == 30
    assert state.classes[1].resources == {
        "food": 31,
        "wood": 32,
        "stone": 33,
        "iron": 34,
        "tools": 35
    }
    assert state.classes[1].land == {
        "fields": 0,
        "woods": 0,
        "stone_mines": 0,
        "iron_mines": 0
    }

    assert isinstance(state.classes[2], Peasants)
    assert state.classes[2].population == 40
    assert state.classes[2].resources == {
        "food": 41,
        "wood": 42,
        "stone": 43,
        "iron": 44,
        "tools": 45
    }
    assert state.classes[2].land == {
        "fields": 46,
        "woods": 47,
        "stone_mines": 0,
        "iron_mines": 0
    }

    assert isinstance(state.classes[3], Others)
    assert state.classes[3].population == 50
    assert state.classes[3].resources == {
        "food": 51,
        "wood": 52,
        "stone": 53,
        "iron": 54,
        "tools": 55
    }
    assert state.classes[3].land == {
        "fields": 0,
        "woods": 0,
        "stone_mines": 0,
        "iron_mines": 0
    }


def test_to_dict():
    state = State_Data("June", 3)
    data = {
        "year": 3,
        "month": "June",
        "classes": {
            "nobles": {
                "population": 20,
                "resources": {
                    "food": 21,
                    "wood": 22,
                    "stone": 23,
                    "iron": 24,
                    "tools": 25
                },
                "land": {
                    "fields": 26,
                    "woods": 27,
                    "stone_mines": 28,
                    "iron_mines": 29
                }
            },
            "artisans": {
                "population": 30,
                "resources": {
                    "food": 31,
                    "wood": 32,
                    "stone": 33,
                    "iron": 34,
                    "tools": 35
                },
                "land": {
                    "fields": 0,
                    "woods": 0,
                    "stone_mines": 0,
                    "iron_mines": 0
                }
            },
            "peasants": {
                "population": 40,
                "resources": {
                    "food": 41,
                    "wood": 42,
                    "stone": 43,
                    "iron": 44,
                    "tools": 45
                },
                "land": {
                    "fields": 46,
                    "woods": 47,
                    "stone_mines": 0,
                    "iron_mines": 0
                }
            },
            "others": {
                "population": 50,
                "resources": {
                    "food": 51,
                    "wood": 52,
                    "stone": 53,
                    "iron": 54,
                    "tools": 55
                },
                "land": {
                    "fields": 0,
                    "woods": 0,
                    "stone_mines": 0,
                    "iron_mines": 0
                }
            }
        },
        "prices": {
            "food": 0.1,
            "wood": 0.2,
            "stone": 0.3,
            "iron": 1.4,
            "tools": 0.5
        }
    }

    population = 20
    resources = {
        "food": 21,
        "wood": 22,
        "stone": 23,
        "iron": 24,
        "tools": 25
    }
    land = {
        "fields": 26,
        "woods": 27,
        "stone_mines": 28,
        "iron_mines": 29
    }
    nobles = Nobles(state, population, resources, land)

    population = 30
    resources = {
        "food": 31,
        "wood": 32,
        "stone": 33,
        "iron": 34,
        "tools": 35
    }
    land = {
        "fields": 0,
        "woods": 0,
        "stone_mines": 0,
        "iron_mines": 0
    }
    artisans = Artisans(state, population, resources, land)

    population = 40
    resources = {
        "food": 41,
        "wood": 42,
        "stone": 43,
        "iron": 44,
        "tools": 45
    }
    land = {
        "fields": 46,
        "woods": 47,
        "stone_mines": 0,
        "iron_mines": 0
    }
    peasants = Peasants(state, population, resources, land)

    population = 50
    resources = {
        "food": 51,
        "wood": 52,
        "stone": 53,
        "iron": 54,
        "tools": 55
    }
    land = {
        "fields": 0,
        "woods": 0,
        "stone_mines": 0,
        "iron_mines": 0
    }
    others = Others(state, population, resources, land)

    classes = [nobles, artisans, peasants, others]
    state.classes = classes

    state.prices = {
        "food": 0.1,
        "wood": 0.2,
        "stone": 0.3,
        "iron": 1.4,
        "tools": 0.5
    }

    assert state.to_dict() == data


def test_get_available_employees():
    state = State_Data()
    data = {
        "year": 0,
        "month": "June",
        "classes": {
            "nobles": {
                "population": 20,
                "resources": {
                    "food": 21,
                    "wood": 22,
                    "stone": 23,
                    "iron": 24,
                    "tools": 25
                },
                "land": {
                    "fields": 26,
                    "woods": 27,
                    "stone_mines": 28,
                    "iron_mines": 29
                }
            },
            "artisans": {
                "population": 30,
                "resources": {
                    "food": 31,
                    "wood": 32,
                    "stone": 33,
                    "iron": 34,
                    "tools": 35
                },
                "land": {
                    "fields": 0,
                    "woods": 0,
                    "stone_mines": 0,
                    "iron_mines": 0
                }
            },
            "peasants": {
                "population": 40,
                "resources": {
                    "food": 41,
                    "wood": 42,
                    "stone": 43,
                    "iron": 44,
                    "tools": 45
                },
                "land": {
                    "fields": 46,
                    "woods": 47,
                    "stone_mines": 0,
                    "iron_mines": 0
                }
            },
            "others": {
                "population": 50,
                "resources": {
                    "food": 51,
                    "wood": 52,
                    "stone": 53,
                    "iron": 54,
                    "tools": 55
                },
                "land": {
                    "fields": 0,
                    "woods": 0,
                    "stone_mines": 0,
                    "iron_mines": 0
                }
            }
        },
        "prices": {
            "food": 0.1,
            "wood": 0.2,
            "stone": 0.3,
            "iron": 1.4,
            "tools": 0.5
        }
    }
    state.from_dict(data)
    assert state.get_available_employees() == 50


class Fake_Class_1:
    pass


def test_get_available_employees_multiple_employable_classes():
    class1 = Fake_Class_1()
    class1.employable = True
    class1.population = 30
    class2 = Fake_Class_1()
    class2.employable = False
    class2.population = 40
    class3 = Fake_Class_1()
    class3.employable = True
    class3.population = 60
    classes = [class1, class2, class3]

    state = State_Data()
    state._classes = classes
    assert state.get_available_employees() == 90


class Fake_Class_2:
    def __init__(self, population, missing_resources):
        self.population = population
        self.missing_resources = missing_resources.copy()
        self.resources = {}

    def grow_population(self, modifier: float):
        grown = self.population * modifier
        self.population += grown
        return grown


def test_grow_populations():
    population = 360
    missing_resources = {
        "food": 0,
        "wood": 0
    }
    class1 = Fake_Class_2(population, missing_resources)

    population = 480
    missing_resources = {
        "food": 10,
        "wood": 12
    }
    class2 = Fake_Class_2(population, missing_resources)

    population = 240
    missing_resources = {
        "food": 5,
        "wood": 0
    }
    class3 = Fake_Class_2(population, missing_resources)

    classes = [class1, class2, class3]

    state = State_Data()
    state._classes = classes

    state._grow_populations()

    assert class1.population == approx(363, abs=0.1)
    assert class2.population == approx(478, abs=0.1)
    assert class3.population == approx(241, abs=0.1)


class Fake_Class_3:
    def __init__(self, overpop):
        self.class_overpopulation = overpop
        self.resources = {
            "food": 0,
            "wood": 0,
            "stone": 0,
            "iron": 0,
            "tools": 0
        }
        self.population = 1000
        self.population_change = 0

    def move_population(self, pop, demotion=False):
        self.population_change += pop


def test_safe_division():
    assert State_Data.safe_division(0, 0) == 0
    assert State_Data.safe_division(10, 0) == 9999
    assert State_Data.safe_division(-10, 0) == -9999
    assert State_Data.safe_division(100, 20) == 5
    assert State_Data.safe_division(10, 20) == 0.5
    assert State_Data.safe_division(1, 5) == 0.2
    assert State_Data.safe_division(-1, 5) == -0.2
    assert State_Data.safe_division(1000, 0.01) == 9999
    assert State_Data.safe_division(-1000, 0.01) == -9999


def test_do_demotions():
    state = State_Data()
    nobles = Fake_Class_3(1)
    artisans = Fake_Class_3(10)
    peasants = Fake_Class_3(100)
    others = Fake_Class_3(0)
    classes = [nobles, artisans, peasants, others]
    state._classes = classes
    demoted = state._do_demotions()
    assert demoted["nobles"] == approx(-0.001)
    assert nobles.population_change == -1
    assert nobles.resources == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }
    assert demoted["artisans"] == approx(-0.01)
    assert artisans.population_change == -10
    assert artisans.resources == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }
    assert demoted["peasants"] == approx(-0.099)
    assert peasants.population_change == -99
    assert peasants.resources == {
        "food": 0,
        "wood": 3,
        "stone": 0,
        "iron": 0,
        "tools": 3
    }
    assert demoted["others"] == approx(0.11)
    assert others.population_change == 110
    assert others.resources == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }


def test_get_max_increase_percent():
    assert State_Data._get_max_increase_percent(0.1) == 0.1
    assert State_Data._get_max_increase_percent(1) == 0.1
    assert State_Data._get_max_increase_percent(2) == \
        approx(0.2)
    assert State_Data._get_max_increase_percent(8) == \
        approx(0.275)
    assert State_Data._get_max_increase_percent(2000) == \
        approx(0.2999, abs=0.0001)


class Fake_Class_4:
    def __init__(self, resources):
        self.population = 100
        self.resources = Arithmetic_Dict(resources.copy())

    def move_population(self, pop):
        self.population += pop


def test_do_one_promotion_max_increase():
    resources = {
        "food": 1000,
        "wood": 1000,
        "stone": 1000,
        "iron": 1000,
        "tools": 1000
    }
    class_from = Fake_Class_4(resources)
    class_to = Fake_Class_4(resources)
    state = State_Data()
    state._classes = [class_from, class_to]
    state.prices = {
        "food": 1,
        "wood": 2,
        "stone": 3,
        "iron": 4,
        "tools": 5
    }
    state._do_one_promotion(class_from, class_to, 10, 15)

    assert class_from.population == 90
    assert class_from.resources == {
        "food": 990,
        "wood": 990,
        "stone": 990,
        "iron": 990,
        "tools": 990
    }
    assert class_to.population == 110
    assert class_to.resources == {
        "food": 1010,
        "wood": 1010,
        "stone": 1010,
        "iron": 1010,
        "tools": 1010
    }


def test_do_one_promotion_smaller_increase():
    resources = {
        "food": 100,
        "wood": 100,
        "stone": 100,
        "iron": 100,
        "tools": 70
    }
    class_from = Fake_Class_4(resources)
    class_to = Fake_Class_4(resources)
    state = State_Data()
    state._classes = [class_from, class_to]
    state.prices = {
        "food": 1,
        "wood": 2,
        "stone": 3,
        "iron": 4,
        "tools": 5
    }
    state._do_one_promotion(class_from, class_to, 100, 15)

    assert class_from.population == 10
    assert class_from.resources == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }
    assert class_to.population == 190
    assert class_to.resources == {
        "food": 200,
        "wood": 200,
        "stone": 200,
        "iron": 200,
        "tools": 140
    }


def test_do_promotions():
    a = DEFAULT_PRICES
    a["food"] = 1
    a["wood"] = 1
    a["stone"] = 1
    a["iron"] = 1
    a["tools"] = 1
    resources = {
        "food": 1000,
        "wood": 1000,
        "stone": 1000,
        "iron": 1000,
        "tools": 1000
    }
    nobles = Fake_Class_4(resources)
    artisans = Fake_Class_4(resources)
    peasants = Fake_Class_4(resources)
    others = Fake_Class_4(resources)
    state = State_Data()
    state.prices *= 1  # max_increase for peasants and artisans: 0.1
    state._classes = [nobles, artisans, peasants, others]
    promoted = state._do_promotions()

    assert nobles.population == 110
    assert nobles.resources == {
        "food": 1024,
        "wood": 1024,
        "stone": 1024,
        "iron": 1024,
        "tools": 1024
    }
    assert artisans.population == 105
    assert artisans.resources == {
        "food": 998,
        "wood": 998,
        "stone": 998,
        "iron": 998,
        "tools": 998
    }
    assert peasants.population == 105
    assert peasants.resources == {
        "food": 1000,
        "wood": 1000,
        "stone": 1000,
        "iron": 1000,
        "tools": 1000
    }
    assert others.population == 80
    assert others.resources == {
        "food": 978,
        "wood": 978,
        "stone": 978,
        "iron": 978,
        "tools": 978
    }

    assert promoted == {
        "nobles": 0.1,
        "artisans": 0.05,
        "peasants": 0.05,
        "others": -0.2
    }
