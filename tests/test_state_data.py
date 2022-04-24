from ..sources.state.state_data import (
    State_Data, Nobles, Artisans, Peasants, Others
)
from ..sources.auxiliaries.constants import (
    DEFAULT_GROWTH_FACTOR,
    DEFAULT_PRICES,
    EMPTY_RESOURCES,
    FOOD_CONSUMPTION,
    FREEZING_MORTALITY,
    INBUILT_RESOURCES,
    RESOURCES,
    STARVATION_MORTALITY,
    WOOD_CONSUMPTION
)
from ..sources.auxiliaries.arithmetic_dict import Arithmetic_Dict
from pytest import approx, raises


def test_constructor():
    state = State_Data("August", 3)
    assert state.month == "August"
    assert state.year == 3
    assert state.payments == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }
    assert isinstance(state.payments, Arithmetic_Dict)
    assert state.prices == DEFAULT_PRICES
    assert state.prices is not DEFAULT_PRICES


def test_default_constructor():
    state = State_Data()
    assert state.month == "January"
    assert state.year == 0
    assert state.payments == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }
    assert isinstance(state.payments, Arithmetic_Dict)
    assert state.prices == DEFAULT_PRICES
    assert state.prices is not DEFAULT_PRICES


def test_classes_setter():
    state = State_Data()
    resources = {
        "food": 31,
        "wood": 32,
        "stone": 33,
        "iron": 34,
        "tools": 35
    }

    nobles = Nobles(state, 20)
    artisans = Artisans(state, 30, resources)
    peasants = Peasants(state, 40)
    others = Others(state, 50)

    classes = [nobles, artisans, peasants, others]
    state.classes = classes

    assert not nobles.is_temp
    assert nobles.lower_class == peasants
    assert nobles.temp == {"population": 0, "resources": EMPTY_RESOURCES}
    assert not nobles.starving
    assert not nobles.freezing

    assert not artisans.is_temp
    assert artisans.lower_class == others
    assert artisans.temp == {"population": 0, "resources": EMPTY_RESOURCES}
    assert not artisans.starving
    assert not artisans.freezing

    assert not peasants.is_temp
    assert peasants.lower_class == others
    assert peasants.temp == {"population": 0, "resources": EMPTY_RESOURCES}
    assert not peasants.starving
    assert not peasants.freezing

    assert not others.is_temp
    assert others.lower_class == others
    assert others.temp == {"population": 0, "resources": EMPTY_RESOURCES}
    assert not others.starving
    assert not others.freezing

    assert state.classes == classes
    assert state.classes is not classes


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


def test_year_setter():
    state = State_Data("August")
    with raises(AssertionError):
        state.year = 2
    state.year = 1
    state.year = 2
    assert state.year == 2
    with raises(AssertionError):
        state.year = 5
    with raises(AssertionError):
        state.year = 1


def test_create_market():
    state = State_Data()
    classes = [1, 2, 3]
    state._classes = [1, 2, 3]
    state._create_market()
    assert state._market.classes == classes
    assert state._market.classes is not classes


def test_from_dict():
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
    state = State_Data.from_dict(data)
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

    assert isinstance(state.classes[1], Artisans)
    assert state.classes[1].population == 30
    assert state.classes[1].resources == {
        "food": 31,
        "wood": 32,
        "stone": 33,
        "iron": 34,
        "tools": 35
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

    assert isinstance(state.classes[3], Others)
    assert state.classes[3].population == 50
    assert state.classes[3].resources == {
        "food": 51,
        "wood": 52,
        "stone": 53,
        "iron": 54,
        "tools": 55
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
    nobles = Nobles(state, population, resources)

    population = 30
    resources = {
        "food": 31,
        "wood": 32,
        "stone": 33,
        "iron": 34,
        "tools": 35
    }
    artisans = Artisans(state, population, resources)

    population = 40
    resources = {
        "food": 41,
        "wood": 42,
        "stone": 43,
        "iron": 44,
        "tools": 45
    }
    peasants = Peasants(state, population, resources)

    population = 50
    resources = {
        "food": 51,
        "wood": 52,
        "stone": 53,
        "iron": 54,
        "tools": 55
    }
    others = Others(state, population, resources)

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
    state = State_Data.from_dict(data)
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


def test_do_growth():
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

    state._do_growth()

    assert class1.population == approx(
        360 * (1 + DEFAULT_GROWTH_FACTOR / 12), abs=0.1
    )
    assert class2.population == approx(
        480 * (1 + DEFAULT_GROWTH_FACTOR / 12), abs=0.1
    )
    assert class3.population == approx(
        240 * (1 + DEFAULT_GROWTH_FACTOR / 12), abs=0.1
    )


def test_do_starvation():
    data = {
        "year": 0,
        "month": "January",
        "classes": {
            "nobles": {
                "population": 20,
                "resources": {
                    "food": -2000,
                    "wood": 0,
                    "stone": 0,
                    "iron": 0,
                    "tools": 0
                }
            },
            "artisans": {
                "population": 50,
                "resources": {
                    "food": -20,
                    "wood": 0,
                    "stone": 0,
                    "iron": 0,
                    "tools": 0
                }
            },
            "peasants": {
                "population": 100,
                "resources": {
                    "food": -20,
                    "wood": -18,
                    "stone": 0,
                    "iron": 0,
                    "tools": 0
                }
            },
            "others": {
                "population": 50,
                "resources": {
                    "food": 0,
                    "wood": -30,
                    "stone": 0,
                    "iron": 0,
                    "tools": 0
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
    state = State_Data.from_dict(data)
    state._do_starvation()
    for social_class in state.classes:
        for res in RESOURCES:
            assert social_class.new_resources[res] >= 0

    assert state.classes[0].new_population == 0
    assert state.classes[0].new_resources == {
        "food": 0,
        "wood": 20 * INBUILT_RESOURCES["nobles"]["wood"],
        "stone": 20 * INBUILT_RESOURCES["nobles"]["stone"],
        "iron": 20 * INBUILT_RESOURCES["nobles"]["iron"],
        "tools": 20 * INBUILT_RESOURCES["nobles"]["tools"]
    }
    assert state.classes[0].population == 20
    assert state.classes[0].resources == {
        "food": -2000,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }

    dead_artisans = 20 * STARVATION_MORTALITY / FOOD_CONSUMPTION
    assert state.classes[1].new_population == 50 - dead_artisans
    assert state.classes[1].new_resources == {
        "food": 0,
        "wood": dead_artisans * INBUILT_RESOURCES["artisans"]["wood"],
        "stone": dead_artisans * INBUILT_RESOURCES["artisans"]["stone"],
        "iron": dead_artisans * INBUILT_RESOURCES["artisans"]["iron"],
        "tools": dead_artisans * INBUILT_RESOURCES["artisans"]["tools"]
    }
    assert state.classes[1].population == 50
    assert state.classes[1].resources == {
        "food": -20,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }

    dead_peasants = 20 * STARVATION_MORTALITY / FOOD_CONSUMPTION + \
        18 * FREEZING_MORTALITY / WOOD_CONSUMPTION["January"]
    assert state.classes[2].new_population == 100 - dead_peasants
    assert state.classes[2].new_resources == {
        "food": 0,
        "wood": dead_peasants * INBUILT_RESOURCES["peasants"]["wood"],
        "stone": dead_peasants * INBUILT_RESOURCES["peasants"]["stone"],
        "iron": dead_peasants * INBUILT_RESOURCES["peasants"]["iron"],
        "tools": dead_peasants * INBUILT_RESOURCES["peasants"]["tools"]
    }
    assert state.classes[2].population == 100
    assert state.classes[2].resources == {
        "food": -20,
        "wood": -18,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }

    assert state.classes[3].new_population == \
        50 - 30 * FREEZING_MORTALITY / WOOD_CONSUMPTION["January"]
    assert state.classes[3].new_resources == EMPTY_RESOURCES
    assert state.classes[3].population == 50
    assert state.classes[3].resources == {
        "food": 0,
        "wood": -30,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }


def test_do_payments():
    state = State_Data()

    nobles = Nobles(state, 20)
    artisans = Artisans(state, 30)
    peasants = Peasants(state, 40)
    others = Others(state, 50)

    classes = [nobles, artisans, peasants, others]
    state.classes = classes
    payments = {
        "food": 1,
        "wood": 2,
        "stone": 3,
        "iron": 4,
        "tools": 5,
    }
    state.payments += payments
    state._do_payments()

    assert state.payments == EMPTY_RESOURCES
    assert others.new_resources == payments
    assert others.resources == EMPTY_RESOURCES


class Fake_Class_3:
    def __init__(self, overpop, name):
        self.class_overpopulation = overpop
        self.class_name = name
        self.new_resources = Arithmetic_Dict({
            "food": 100,
            "wood": 100,
            "stone": 100,
            "iron": 100,
            "tools": 100
        })
        self.population = 50
        self.new_population = 50


def test_do_demotions():
    state = State_Data()
    nobles = Fake_Class_3(10, "nobles")
    artisans = Fake_Class_3(100, "artisans")
    peasants = Fake_Class_3(10, "peasants")
    others = Fake_Class_3(0, "others")

    # normally done in classes setter
    nobles.lower_class = peasants
    artisans.lower_class = others
    peasants.lower_class = others
    others.lower_class = others

    classes = [nobles, artisans, peasants, others]
    state._classes = classes
    state._do_demotions()

    HUNDREDS = Arithmetic_Dict({
        "food": 100,
        "wood": 100,
        "stone": 100,
        "iron": 100,
        "tools": 100
    })

    assert nobles.new_population == 40
    assert nobles.new_resources == \
        HUNDREDS - INBUILT_RESOURCES["peasants"] * 10

    assert artisans.new_population == 0
    assert artisans.new_resources == HUNDREDS

    assert peasants.new_population == 50
    assert peasants.new_resources == \
        HUNDREDS + INBUILT_RESOURCES["peasants"] * 10

    assert others.new_population == 110
    assert others.new_resources == HUNDREDS


class Fake_Class_4:
    def __init__(self):
        self.unnegatived = False
        self.unemptied = False

    def handle_negative_resources(self):
        self.unnegatived = True

    def handle_empty_class(self):
        self.unemptied = True


def test_secure_classes():
    state = State_Data()
    nobles = Fake_Class_4()
    artisans = Fake_Class_4()
    peasants = Fake_Class_4()
    others = Fake_Class_4()

    classes = [nobles, artisans, peasants, others]
    state._classes = classes

    state._secure_classes()
    for social_class in classes:
        assert social_class.unnegatived
        assert social_class.unemptied


class Fake_Class_5:
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
    class_from = Fake_Class_5(resources)
    class_to = Fake_Class_5(resources)
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
    class_from = Fake_Class_5(resources)
    class_to = Fake_Class_5(resources)
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
    nobles = Fake_Class_5(resources)
    artisans = Fake_Class_5(resources)
    peasants = Fake_Class_5(resources)
    others = Fake_Class_5(resources)
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
