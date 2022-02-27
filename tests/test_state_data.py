from ..classes.state_data import (
    State_Data, Nobles, Artisans, Peasants, Others
)
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
    assert state.prices == {
        "food": 0,
        "wood": 0,
        "iron": 0,
        "stone": 0,
        "tools": 0
    }


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
    assert state.prices == {
        "food": 0,
        "wood": 0,
        "iron": 0,
        "stone": 0,
        "tools": 0
    }


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


def test_do_demotions():
    state = State_Data()
    nobles = Fake_Class_3(1)
    artisans = Fake_Class_3(10)
    peasants = Fake_Class_3(100)
    others = Fake_Class_3(0)
    classes = [nobles, artisans, peasants, others]
    state._classes = classes
    state._do_demotions()
    assert nobles.population_change == -1
    assert nobles.resources == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }
    assert artisans.population_change == -10
    assert artisans.resources == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }
    assert peasants.population_change == -99
    assert peasants.resources == {
        "food": 0,
        "wood": 3,
        "stone": 0,
        "iron": 0,
        "tools": 3
    }
    assert others.population_change == 110
    assert others.resources == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }


# def test_do_month():
#     state = State_Data("March", starting_year=1)
#     population = 20
#     resources = {
#         "food": 200,
#         "wood": 150,
#         "stone": 150,
#         "iron": 0,
#         "tools": 400
#     }
#     land = {
#         "fields": 4000,
#         "woods": 2000,
#         "stone_mines": 1,
#         "iron_mines": 1
#     }
#     nobles = Nobles(state, population, resources, land)

#     population = 30
#     resources = {
#         "food": 100,
#         "wood": 100,
#         "stone": 0,
#         "iron": 50,
#         "tools": 40
#     }
#     artisans = Artisans(state, population, resources)

#     population = 50
#     resources = {
#         "food": 180,
#         "wood": 200,
#         "stone": 0,
#         "iron": 0,
#         "tools": 100
#     }
#     land = {
#         "fields": 1200,
#         "woods": 300,
#         "stone_mines": 0,
#         "iron_mines": 0
#     }
#     peasants = Peasants(state, population, resources, land)

#     population = 100
#     resources = {
#         "food": 300,
#         "wood": 200,
#         "stone": 0,
#         "iron": 0,
#         "tools": 0
#     }
#     others = Others(state, population, resources)

#     classes = [nobles, artisans, peasants, others]
#     state.classes = classes
#     month_data = state.do_month()
#     assert month_data["year"] == 1
#     assert month_data["month"] == "March"
#     assert month_data["produced"] == {
#         "nobles": {
#             "food": 40,
#             "wood": 20,
#             "stone": 20,
#             "iron": 20
#         },
#         "artisans": {
#             "tools": 30
#         },
#         "peasants": {
#             "food": 40,
#             "wood": 10
#         },
#         "others": {}
#     }
#     assert month_data["used"] == {
#         "nobles": {
#             "tools": 22
#         },
#         "artisans": {
#             "wood": 6,
#             "iron": 15,
#             "tools": approx(4.5)
#         },
#         "peasants": {
#             "tools": 5
#         },
#         "others": {}
#     }
#     assert month_data["trade_prices"] == {
#         "food": approx(1.116, 0.01),
#         "wood": approx(0.981, 0.01),
#         "stone": approx(0.941, 0.01),
#         "iron": approx(1.091, 0.01),
#         "tools": approx(0.971, 0.01)
#     }
#     assert month_data["growth_modifiers"] == {
#         "nobles": {
#             "Base": approx(0.00833, abs=1e-5)
#         },
#         "artisans": {
#             "Base": approx(0.00833, abs=1e-5)
#         },
#         "peasants": {
#             "Base": approx(0.00833, abs=1e-5)
#         },
#         "others": {
#             "Base": approx(0.00833, abs=1e-5)
#         }
#     }
#     assert month_data["grown"] == {
#         "nobles": approx(0.17, abs=0.01),
#         "artisans": approx(0.25, abs=0.01),
#         "peasants": approx(0.42, abs=0.01),
#         "others": approx(0.83, abs=0.01)
#     }
#     assert month_data["consumed"] == {
#         "nobles": {
#             "food": 20,
#             "wood": 6
#         },
#         "artisans": {
#             "food": 30,
#             "wood": 9
#         },
#         "peasants": {
#             "food": 50,
#             "wood": 15
#         },
#         "others": {
#             "food": 100,
#             "wood": 30
#         }
#     }
#     assert month_data["resources_after"] == {
#         "nobles": {
#             "food": approx(206.17, abs=0.1),
#             "wood": approx(144.51, abs=0.1),
#             "stone": approx(162.19, abs=0.1),
#             "iron": approx(1.4, abs=0.1),
#             "tools": approx(384.99, abs=0.1)
#         },
#         "artisans": {
#             "food": approx(67.96, abs=0.1),
#             "wood": approx(91.62, abs=0.1),
#             "stone": 0,
#             "iron": approx(50.11, abs=0.1),
#             "tools": approx(42.98, abs=0.1)
#         },
#         "peasants": {
#             "food": approx(156.84, abs=0.1),
#             "wood": approx(184.09, abs=0.1),
#             "stone": approx(7.19, abs=0.1),
#             "iron": approx(3.49, abs=0.1),
#             "tools": approx(107.84, abs=0.1)
#         },
#         "others": {
#             "food": approx(229.03, abs=0.1),
#             "wood": approx(190.32, abs=0.1),
#             "stone": 0,
#             "iron": 0,
#             "tools": 0
#         },
#     }
#     assert month_data["population_after"] == {
#         "nobles": approx(20.17, abs=0.01),
#         "artisans": approx(30.25, abs=0.01),
#         "peasants": approx(50.42, abs=0.01),
#         "others": approx(100.83, abs=0.01)
#     }
