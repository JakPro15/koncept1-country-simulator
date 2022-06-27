from ..sources.state.state_data import (
    State_Data, Nobles, Artisans, Peasants, Others, Government
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
    WOOD_CONSUMPTION,
    INCREASE_PRICE_FACTOR
)
from ..sources.auxiliaries.arithmetic_dict import Arithmetic_Dict
from ..sources.auxiliaries.testing import dict_eq
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
        "tools": 0,
        "land": 0
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
        "tools": 0,
        "land": 0
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
        "tools": 35,
        "land": 0
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
    with raises(Exception):
        state.year = 2
    state.year = 1
    state.year = 2
    assert state.year == 2
    with raises(Exception):
        state.year = 5
    with raises(Exception):
        state.year = 1


def test_create_market():
    state = State_Data()
    govt = Government(state)
    classes = [1, 2, 3]
    state._classes = [1, 2, 3]
    state._government = govt
    state._create_market()
    classes.append(govt)
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
                    "tools": 25,
                    "land": 26
                }
            },
            "artisans": {
                "population": 30,
                "resources": {
                    "food": 31,
                    "wood": 32,
                    "stone": 33,
                    "iron": 34,
                    "tools": 35,
                    "land": 36
                }
            },
            "peasants": {
                "population": 40,
                "resources": {
                    "food": 41,
                    "wood": 42,
                    "stone": 43,
                    "iron": 44,
                    "tools": 45,
                    "land": 46
                }
            },
            "others": {
                "population": 50,
                "resources": {
                    "food": 51,
                    "wood": 52,
                    "stone": 53,
                    "iron": 54,
                    "tools": 55,
                    "land": 56
                }
            }
        },
        "government": {
            "resources": {
                "food": 61,
                "wood": 62,
                "stone": 63,
                "iron": 64,
                "tools": 65,
                "land": 66
            },
            "optimal_resources": {
                "food": 71,
                "wood": 72,
                "stone": 73,
                "iron": 74,
                "tools": 75,
                "land": 76
            }
        },
        "prices": {
            "food": 0.1,
            "wood": 0.2,
            "stone": 0.3,
            "iron": 1.4,
            "tools": 0.5,
            "land": 2.6
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
        "tools": 25,
        "land": 26
    }

    assert isinstance(state.classes[1], Artisans)
    assert state.classes[1].population == 30
    assert state.classes[1].resources == {
        "food": 31,
        "wood": 32,
        "stone": 33,
        "iron": 34,
        "tools": 35,
        "land": 36
    }

    assert isinstance(state.classes[2], Peasants)
    assert state.classes[2].population == 40
    assert state.classes[2].resources == {
        "food": 41,
        "wood": 42,
        "stone": 43,
        "iron": 44,
        "tools": 45,
        "land": 46
    }

    assert isinstance(state.classes[3], Others)
    assert state.classes[3].population == 50
    assert state.classes[3].resources == {
        "food": 51,
        "wood": 52,
        "stone": 53,
        "iron": 54,
        "tools": 55,
        "land": 56
    }

    assert isinstance(state.prices, Arithmetic_Dict)
    assert state.prices == {
        "food": 0.1,
        "wood": 0.2,
        "stone": 0.3,
        "iron": 1.4,
        "tools": 0.5,
        "land": 2.6
    }

    assert isinstance(state.government, Government)
    assert state.government.resources == {
        "food": 61,
        "wood": 62,
        "stone": 63,
        "iron": 64,
        "tools": 65,
        "land": 66
    }
    assert state.government.optimal_resources == {
        "food": 71,
        "wood": 72,
        "stone": 73,
        "iron": 74,
        "tools": 75,
        "land": 76
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
                    "tools": 25,
                    "land": 0
                }
            },
            "artisans": {
                "population": 30,
                "resources": {
                    "food": 31,
                    "wood": 32,
                    "stone": 33,
                    "iron": 34,
                    "tools": 35,
                    "land": 0
                }
            },
            "peasants": {
                "population": 40,
                "resources": {
                    "food": 41,
                    "wood": 42,
                    "stone": 43,
                    "iron": 44,
                    "tools": 45,
                    "land": 0
                }
            },
            "others": {
                "population": 50,
                "resources": {
                    "food": 51,
                    "wood": 52,
                    "stone": 53,
                    "iron": 54,
                    "tools": 55,
                    "land": 0
                }
            }
        },
        "government": {
            "resources": {
                "food": 61,
                "wood": 62,
                "stone": 63,
                "iron": 64,
                "tools": 65,
                "land": 66
            },
            "optimal_resources": {
                "food": 71,
                "wood": 72,
                "stone": 73,
                "iron": 74,
                "tools": 75,
                "land": 76
            }
        },
        "prices": {
            "food": 0.1,
            "wood": 0.2,
            "stone": 0.3,
            "iron": 1.4,
            "tools": 0.5,
            "land": 10
        }
    }

    population = 20
    resources = {
        "food": 21,
        "wood": 22,
        "stone": 23,
        "iron": 24,
        "tools": 25,
        "land": 0
    }
    nobles = Nobles(state, population, resources)

    population = 30
    resources = {
        "food": 31,
        "wood": 32,
        "stone": 33,
        "iron": 34,
        "tools": 35,
        "land": 0
    }
    artisans = Artisans(state, population, resources)

    population = 40
    resources = {
        "food": 41,
        "wood": 42,
        "stone": 43,
        "iron": 44,
        "tools": 45,
        "land": 0
    }
    peasants = Peasants(state, population, resources)

    population = 50
    resources = {
        "food": 51,
        "wood": 52,
        "stone": 53,
        "iron": 54,
        "tools": 55,
        "land": 0
    }
    others = Others(state, population, resources)

    classes = [nobles, artisans, peasants, others]
    state.classes = classes

    resources = {
        "food": 61,
        "wood": 62,
        "stone": 63,
        "iron": 64,
        "tools": 65,
        "land": 66
    }
    opt_res = {
        "food": 71,
        "wood": 72,
        "stone": 73,
        "iron": 74,
        "tools": 75,
        "land": 76
    }
    govt = Government(state, resources, opt_res)
    state.government = govt

    state.prices = {
        "food": 0.1,
        "wood": 0.2,
        "stone": 0.3,
        "iron": 1.4,
        "tools": 0.5,
        "land": 10
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
                    "tools": 25,
                    "land": 0
                }
            },
            "artisans": {
                "population": 30,
                "resources": {
                    "food": 31,
                    "wood": 32,
                    "stone": 33,
                    "iron": 34,
                    "tools": 35,
                    "land": 0
                }
            },
            "peasants": {
                "population": 40,
                "resources": {
                    "food": 41,
                    "wood": 42,
                    "stone": 43,
                    "iron": 44,
                    "tools": 45,
                    "land": 0
                }
            },
            "others": {
                "population": 50,
                "resources": {
                    "food": 51,
                    "wood": 52,
                    "stone": 53,
                    "iron": 54,
                    "tools": 55,
                    "land": 0
                }
            }
        },
        "government": {
            "resources": {
                "food": 61,
                "wood": 62,
                "stone": 63,
                "iron": 64,
                "tools": 65,
                "land": 66
            },
            "optimal_resources": {
                "food": 71,
                "wood": 72,
                "stone": 73,
                "iron": 74,
                "tools": 75,
                "land": 76
            }
        },
        "prices": {
            "food": 0.1,
            "wood": 0.2,
            "stone": 0.3,
            "iron": 1.4,
            "tools": 0.5,
            "land": 10
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
        self.new_population = population
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
                    "food": 0,
                    "wood": 0,
                    "stone": 0,
                    "iron": 0,
                    "tools": 0,
                    "land": 0
                }
            },
            "artisans": {
                "population": 50,
                "resources": {
                    "food": 0,
                    "wood": 0,
                    "stone": 0,
                    "iron": 0,
                    "tools": 0,
                    "land": 0
                }
            },
            "peasants": {
                "population": 100,
                "resources": {
                    "food": 20,
                    "wood": 18,
                    "stone": 0,
                    "iron": 0,
                    "tools": 0,
                    "land": 0
                }
            },
            "others": {
                "population": 50,
                "resources": {
                    "food": 0,
                    "wood": 30,
                    "stone": 0,
                    "iron": 0,
                    "tools": 0,
                    "land": 0
                }
            }
        },
        "government": {
            "resources": {
                "food": 61,
                "wood": 62,
                "stone": 63,
                "iron": 64,
                "tools": 65,
                "land": 66
            },
            "optimal_resources": {
                "food": 71,
                "wood": 72,
                "stone": 73,
                "iron": 74,
                "tools": 75,
                "land": 76
            }
        },
        "prices": {
            "food": 0.1,
            "wood": 0.2,
            "stone": 0.3,
            "iron": 1.4,
            "tools": 0.5,
            "land": 10
        }
    }
    state = State_Data.from_dict(data)
    state.classes[0].new_resources = {
        "food": -2000,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0,
        "land": 0
    }
    state.classes[1].new_resources = {
        "food": -20,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0,
        "land": 0
    }
    state.classes[2].new_resources = {
        "food": -20,
        "wood": -18,
        "stone": 0,
        "iron": 0,
        "tools": 0,
        "land": 0
    }
    state.classes[3].new_resources = {
        "food": 0,
        "wood": -30,
        "stone": 0,
        "iron": 0,
        "tools": 0,
        "land": 0
    }

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
        "tools": 20 * INBUILT_RESOURCES["nobles"]["tools"],
        "land": 20 * INBUILT_RESOURCES["nobles"]["land"],
    }
    assert state.classes[0].population == 20
    assert state.classes[0].starving
    assert not state.classes[0].freezing

    dead_artisans = 20 * STARVATION_MORTALITY / FOOD_CONSUMPTION
    assert state.classes[1].new_population == 50 - dead_artisans
    assert state.classes[1].new_resources == {
        "food": 0,
        "wood": dead_artisans * INBUILT_RESOURCES["artisans"]["wood"],
        "stone": dead_artisans * INBUILT_RESOURCES["artisans"]["stone"],
        "iron": dead_artisans * INBUILT_RESOURCES["artisans"]["iron"],
        "tools": dead_artisans * INBUILT_RESOURCES["artisans"]["tools"],
        "land": dead_artisans * INBUILT_RESOURCES["artisans"]["land"],
    }
    assert state.classes[1].population == 50
    assert state.classes[1].starving
    assert not state.classes[1].freezing

    dead_peasants = 20 * STARVATION_MORTALITY / FOOD_CONSUMPTION + \
        18 * FREEZING_MORTALITY / WOOD_CONSUMPTION["January"]
    assert state.classes[2].new_population == 100 - dead_peasants
    assert state.classes[2].new_resources == {
        "food": 0,
        "wood": dead_peasants * INBUILT_RESOURCES["peasants"]["wood"],
        "stone": dead_peasants * INBUILT_RESOURCES["peasants"]["stone"],
        "iron": dead_peasants * INBUILT_RESOURCES["peasants"]["iron"],
        "tools": dead_peasants * INBUILT_RESOURCES["peasants"]["tools"],
        "land": dead_peasants * INBUILT_RESOURCES["peasants"]["land"],
    }
    assert state.classes[2].population == 100
    assert state.classes[2].starving
    assert state.classes[2].freezing

    assert state.classes[3].new_population == \
        50 - 30 * FREEZING_MORTALITY / WOOD_CONSUMPTION["January"]
    assert state.classes[3].new_resources == EMPTY_RESOURCES
    assert state.classes[3].population == 50
    assert not state.classes[3].starving
    assert state.classes[3].freezing


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
        "land": 0
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
            "tools": 100,
            "land": 0
        })
        self.population = 50
        self.new_population = 50


def test_reset_flags():
    state = State_Data()
    nobles = Fake_Class_3(10, "nobles")
    nobles.demoted_to = True
    artisans = Fake_Class_3(100, "artisans")
    artisans.promoted_to = True
    peasants = Fake_Class_3(10, "peasants")
    peasants.demoted_from = True
    others = Fake_Class_3(0, "others")
    others.promoted_from = False

    # normally done in classes setter
    nobles.lower_class = peasants
    artisans.lower_class = others
    peasants.lower_class = others
    others.lower_class = others

    classes = [nobles, artisans, peasants, others]
    state._classes = classes
    state._reset_flags()

    assert nobles.promoted_from is False
    assert nobles.promoted_to is False
    assert nobles.demoted_from is False
    assert nobles.demoted_to is False

    assert artisans.promoted_from is False
    assert artisans.promoted_to is False
    assert artisans.demoted_from is False
    assert artisans.demoted_to is False

    assert peasants.promoted_from is False
    assert peasants.promoted_to is False
    assert peasants.demoted_from is False
    assert peasants.demoted_to is False

    assert others.promoted_from is False
    assert others.promoted_to is False
    assert others.demoted_from is False
    assert others.demoted_to is False


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
    state._reset_flags()
    state._do_demotions()

    HUNDREDS = Arithmetic_Dict({
        "food": 100,
        "wood": 100,
        "stone": 100,
        "iron": 100,
        "tools": 100,
        "land": 0
    })

    assert nobles.new_population == 40
    assert nobles.new_resources == \
        HUNDREDS - INBUILT_RESOURCES["peasants"] * 10
    assert nobles.demoted_from
    assert not nobles.demoted_to

    assert artisans.new_population == 0
    # resources unchanged because new_population setter doesn't change them
    # in Fake_Class_3
    assert artisans.new_resources == HUNDREDS
    assert artisans.demoted_from
    assert not artisans.demoted_to

    assert peasants.new_population == 50
    assert peasants.new_resources == \
        HUNDREDS + INBUILT_RESOURCES["peasants"] * 10
    assert peasants.demoted_from
    assert peasants.demoted_to

    assert others.new_population == 110
    assert others.new_resources == HUNDREDS
    assert not others.demoted_from
    assert others.demoted_to


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
    govt = Government(state)
    nobles = Fake_Class_4()
    artisans = Fake_Class_4()
    peasants = Fake_Class_4()
    others = Fake_Class_4()

    classes = [nobles, artisans, peasants, others]
    state._classes = classes
    state._government = govt

    state._secure_classes()
    for social_class in classes:
        assert social_class.unnegatived
        assert social_class.unemptied


def test_promotion_math():
    from random import randint
    wealths = [randint(1, 10000) for _ in range(10000)]
    pops = [randint(1, 10000) for _ in range(10000)]
    incprices = [randint(1, 10000) for _ in range(10000)]
    for wealth, pop, incpr in zip(wealths, pops, incprices):
        part_paid, transferred = State_Data._promotion_math(wealth, pop, incpr)
        assert 0 <= part_paid <= 1
        assert 0 <= transferred <= pop


class Fake_Class_5:
    def __init__(self, resources, employable=False):
        self.population = 100
        self.resources = Arithmetic_Dict(resources.copy())
        self.new_population = 100
        self.new_resources = Arithmetic_Dict(resources.copy())
        self.starving = False
        self.freezing = False
        self.class_name = "fake"
        self.employable = employable


def test_do_one_promotion():
    resources = Arithmetic_Dict({
        "food": 1000,
        "wood": 1000,
        "stone": 1000,
        "iron": 1000,
        "tools": 1000
    })
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
    state._reset_flags()
    state._do_one_promotion(class_from, class_to, 10)
    part_paid, transferred = state._promotion_math(15000, 100, 10)

    assert class_from.new_population == approx(100 - transferred)
    dict_eq(class_from.new_resources, resources * (1 - part_paid))
    assert class_from.promoted_from
    assert not class_from.promoted_to

    assert class_to.new_population == approx(100 + transferred)
    dict_eq(class_to.new_resources, resources * (1 + part_paid))
    assert not class_to.promoted_from
    assert class_to.promoted_to


def test_do_double_promotion():
    resources = Arithmetic_Dict({
        "food": 1000,
        "wood": 1000,
        "stone": 1000,
        "iron": 1000,
        "tools": 1000
    })
    class_from = Fake_Class_5(resources)
    class_to_1 = Fake_Class_5(resources)
    class_to_2 = Fake_Class_5(resources)
    state = State_Data()
    state._classes = [class_from, class_to_1, class_to_2]
    state.prices = {
        "food": 1,
        "wood": 2,
        "stone": 3,
        "iron": 4,
        "tools": 5
    }
    state._reset_flags()
    state._do_double_promotion(class_from, class_to_1, 30, class_to_2, 10)

    part_paid, transferred = state._promotion_math(15000, 100, 20)
    part_paid_1 = 0.75 * part_paid
    part_paid_2 = 0.25 * part_paid

    assert class_from.new_population == approx(100 - transferred)
    dict_eq(class_from.new_resources, resources * (1 - part_paid))
    assert class_from.promoted_from
    assert not class_from.promoted_to

    assert class_to_1.new_population == approx(100 + transferred / 2)
    dict_eq(class_to_1.new_resources, resources * (1 + part_paid_1))
    assert not class_to_1.promoted_from
    assert class_to_1.promoted_to

    assert class_to_2.new_population == approx(100 + transferred / 2)
    dict_eq(class_to_2.new_resources, resources * (1 + part_paid_2))
    assert not class_to_2.promoted_from
    assert class_to_2.promoted_to


def test_do_promotions_no_starvation():
    # force default prices to all be equal to 1
    saved_defaults = DEFAULT_PRICES.copy()
    a = DEFAULT_PRICES
    a["food"] = 1
    a["wood"] = 1
    a["stone"] = 1
    a["iron"] = 1
    a["tools"] = 1

    resources = Arithmetic_Dict({
        "food": 1000,
        "wood": 1000,
        "stone": 1000,
        "iron": 1000,
        "tools": 1000
    })
    nobles = Fake_Class_5(resources)
    nobles.population = 10
    nobles.new_population = 10
    artisans = Fake_Class_5(resources)
    peasants = Fake_Class_5(resources)
    others = Fake_Class_5(resources, True)
    state = State_Data()
    state._classes = [nobles, artisans, peasants, others]
    state._reset_flags()
    state._do_promotions()

    increase_price_peasants = INCREASE_PRICE_FACTOR * \
        sum((INBUILT_RESOURCES["peasants"] * state.prices).values())
    increase_price_artisans = INCREASE_PRICE_FACTOR * \
        sum((INBUILT_RESOURCES["artisans"] * state.prices).values())
    increase_price_nobles = INCREASE_PRICE_FACTOR * \
        sum((INBUILT_RESOURCES["nobles"] * state.prices).values())

    part_paid_nobles, transferred_nobles = State_Data._promotion_math(
        5000, 100, increase_price_nobles
    )
    part_paid_others, transferred_others = State_Data._promotion_math(
        5000, 100, increase_price_artisans
    )
    part_paid_artisans = part_paid_others * increase_price_artisans / \
        (increase_price_artisans + increase_price_peasants)
    part_paid_peasants = part_paid_others * increase_price_peasants / \
        (increase_price_artisans + increase_price_peasants)

    assert nobles.new_population == 10 + transferred_nobles * 2
    dict_eq(nobles.new_resources,
            resources * (1 + part_paid_nobles * 2))
    assert not nobles.promoted_from
    assert nobles.promoted_to == (transferred_nobles > 0)

    assert artisans.new_population == \
        100 + transferred_others / 2 - transferred_nobles
    dict_eq(artisans.new_resources,
            resources * (1 + part_paid_artisans - part_paid_nobles))
    assert artisans.promoted_from == (transferred_nobles > 0)
    assert artisans.promoted_to == (transferred_others > 0)

    assert peasants.new_population == \
        100 + transferred_others / 2 - transferred_nobles
    dict_eq(peasants.new_resources,
            resources * (1 + part_paid_peasants - part_paid_nobles))
    assert peasants.promoted_from == (transferred_nobles > 0)
    assert peasants.promoted_to == (transferred_others > 0)

    assert others.new_population == 100 - transferred_others
    dict_eq(others.new_resources,
            resources * (1 - part_paid_others))
    assert others.promoted_from == (transferred_others > 0)
    assert not others.promoted_to

    for key in saved_defaults:
        a[key] = saved_defaults[key]


def test_do_promotions_with_starvation():
    # force default prices to all be equal to 1
    saved_defaults = DEFAULT_PRICES.copy()
    a = DEFAULT_PRICES
    a["food"] = 1
    a["wood"] = 1
    a["stone"] = 1
    a["iron"] = 1
    a["tools"] = 1

    resources = Arithmetic_Dict({
        "food": 1000,
        "wood": 1000,
        "stone": 1000,
        "iron": 1000,
        "tools": 1000
    })
    nobles = Fake_Class_5(resources)
    nobles.population = 10
    nobles.new_population = 10
    artisans = Fake_Class_5(resources)
    peasants = Fake_Class_5(resources)
    peasants.starving = True
    others = Fake_Class_5(resources, True)
    others.freezing = True
    state = State_Data()
    state._classes = [nobles, artisans, peasants, others]
    state._reset_flags()
    state._do_promotions()

    increase_price_nobles = INCREASE_PRICE_FACTOR * \
        sum((INBUILT_RESOURCES["nobles"] * state.prices).values())

    part_paid_nobles, transferred_nobles = State_Data._promotion_math(
        5000, 100, increase_price_nobles
    )

    assert nobles.new_population == 10 + transferred_nobles
    dict_eq(nobles.new_resources, resources * (1 + part_paid_nobles))
    assert not nobles.promoted_from
    assert nobles.promoted_to == (transferred_nobles > 0)

    assert artisans.new_population == 100 - transferred_nobles
    dict_eq(artisans.new_resources, resources * (1 - part_paid_nobles))
    assert artisans.promoted_from == (transferred_nobles > 0)
    assert not artisans.promoted_to

    assert peasants.new_population == 100
    dict_eq(peasants.new_resources, resources)
    assert not peasants.promoted_from
    assert not peasants.promoted_to

    assert others.new_population == 100
    dict_eq(others.new_resources, resources)
    assert not others.promoted_from
    assert not others.promoted_to

    for key in saved_defaults:
        a[key] = saved_defaults[key]


def test_do_promotions_with_nobles_cap():
    # force default prices to all be equal to 1
    saved_defaults = DEFAULT_PRICES.copy()
    a = DEFAULT_PRICES
    a["food"] = 1
    a["wood"] = 1
    a["stone"] = 1
    a["iron"] = 1
    a["tools"] = 1

    resources = Arithmetic_Dict({
        "food": 1000,
        "wood": 1000,
        "stone": 1000,
        "iron": 1000,
        "tools": 1000
    })
    nobles = Fake_Class_5(resources)
    nobles.population = 10000
    nobles.new_population = 10000
    artisans = Fake_Class_5(resources)
    peasants = Fake_Class_5(resources)
    others = Fake_Class_5(resources, True)
    state = State_Data()
    state._classes = [nobles, artisans, peasants, others]
    state._reset_flags()
    state._do_promotions()

    increase_price_peasants = INCREASE_PRICE_FACTOR * \
        sum((INBUILT_RESOURCES["peasants"] * state.prices).values())
    increase_price_artisans = INCREASE_PRICE_FACTOR * \
        sum((INBUILT_RESOURCES["artisans"] * state.prices).values())

    part_paid_others, transferred_others = State_Data._promotion_math(
        5000, 100, increase_price_artisans
    )
    part_paid_artisans = part_paid_others * increase_price_artisans / \
        (increase_price_artisans + increase_price_peasants)
    part_paid_peasants = part_paid_others * increase_price_peasants / \
        (increase_price_artisans + increase_price_peasants)

    assert nobles.new_population == 10000
    dict_eq(nobles.new_resources, resources)
    assert not nobles.promoted_from
    assert not nobles.promoted_to

    assert artisans.new_population == 100 + transferred_others / 2
    dict_eq(artisans.new_resources,
            resources * (1 + part_paid_artisans))
    assert not artisans.promoted_from
    assert artisans.promoted_to == (transferred_others > 0)

    assert peasants.new_population == 100 + transferred_others / 2
    dict_eq(peasants.new_resources,
            resources * (1 + part_paid_peasants))
    assert not peasants.promoted_from
    assert peasants.promoted_to == (transferred_others > 0)

    assert others.new_population == 100 - transferred_others
    dict_eq(others.new_resources,
            resources * (1 - part_paid_others))
    assert others.promoted_from == (transferred_others > 0)
    assert not others.promoted_to

    for key in saved_defaults:
        a[key] = saved_defaults[key]


def test_get_personal_taxes():
    state = State_Data()
    populations = {
        "nobles": 10,
        "artisans": 20,
        "peasants": 30,
        "others": 40
    }
    net_worths = Arithmetic_Dict({
        "nobles": 150,
        "artisans": 200,
        "peasants": 900,
        "others": 100
    })
    state.sm.tax_rates["personal"] = Arithmetic_Dict({
        "nobles": 0,
        "artisans": 1,
        "peasants": 1.5,
        "others": 2
    })
    rel_tax = state._get_personal_taxes(populations, net_worths)
    dict_eq(rel_tax, {
        "nobles": 0,
        "artisans": 0.1,
        "peasants": 0.05,
        "others": 0.8
    })


def test_get_property_taxes():
    state = State_Data()
    state.sm.tax_rates["property"] = Arithmetic_Dict({
        "nobles": 0,
        "artisans": 0.1,
        "peasants": 0.15,
        "others": 0.8
    })
    assert state._get_property_taxes() == \
        state.sm.tax_rates["property"]


def test_get_income_taxes():
    state = State_Data()
    state.sm.tax_rates["income"] = Arithmetic_Dict({
        "nobles": 0.2,
        "artisans": 0.5,
        "peasants": 0.8,
        "others": 1
    })
    net_worths_change = {
        "nobles": 0,
        "artisans": 80,
        "peasants": 100,
        "others": 160
    }
    net_worths = Arithmetic_Dict({
        "nobles": 2000,
        "artisans": 400,
        "peasants": 400,
        "others": 320
    })
    rel_tax = state._get_income_taxes(net_worths_change, net_worths)
    dict_eq(rel_tax, {
        "nobles": 0,
        "artisans": 0.1,
        "peasants": 0.2,
        "others": 0.5
    })


def test_do_taxes():
    data = {
        "year": 3,
        "month": "June",
        "classes": {
            "nobles": {
                "population": 20,
                "resources": {
                    "food": 10,
                    "wood": 10,
                    "stone": 10,
                    "iron": 10,
                    "tools": 10,
                    "land": 10
                }
            },
            "artisans": {
                "population": 30,
                "resources": {
                    "food": 20,
                    "wood": 20,
                    "stone": 20,
                    "iron": 20,
                    "tools": 20,
                    "land": 20
                }
            },
            "peasants": {
                "population": 40,
                "resources": {
                    "food": 40,
                    "wood": 40,
                    "stone": 40,
                    "iron": 40,
                    "tools": 40,
                    "land": 40
                }
            },
            "others": {
                "population": 50,
                "resources": {
                    "food": 50,
                    "wood": 100,
                    "stone": 50,
                    "iron": 50,
                    "tools": 100,
                    "land": 50
                }
            }
        },
        "government": {
            "resources": {
                "food": 10,
                "wood": 10,
                "stone": 10,
                "iron": 10,
                "tools": 10,
                "land": 10
            },
            "optimal_resources": {
                "food": 0,
                "wood": 0,
                "stone": 0,
                "iron": 0,
                "tools": 0,
                "land": 0
            }
        },
        "prices": {
            "food": 1,
            "wood": 2,
            "stone": 3,
            "iron": 4,
            "tools": 5,
            "land": 5
        }
    }
    state = State_Data.from_dict(data)
    state.sm.tax_rates = {
        "property": Arithmetic_Dict({
            "nobles": 0,
            "artisans": 0.2,
            "peasants": 0.3,
            "others": 0.3
        }),
        "income": Arithmetic_Dict({
            "nobles": 0.2,
            "artisans": 0.1,
            "peasants": 0.1,
            "others": 0.2
        }),
        "personal": Arithmetic_Dict({
            "nobles": 0.5,
            "artisans": 2,
            "peasants": 4,
            "others": 1
        })
    }
    net_worths = Arithmetic_Dict({
        "nobles": 200 + sum(
            (INBUILT_RESOURCES["nobles"] * 20 * state.prices).values()
        ),
        "artisans": 400 + sum(
            (INBUILT_RESOURCES["artisans"] * 30 * state.prices).values()
        ),
        "peasants": 800 + sum(
            (INBUILT_RESOURCES["peasants"] * 40 * state.prices).values()
        ),
        "others": 1350 + sum(
            (INBUILT_RESOURCES["others"] * 50 * state.prices).values()
        )
    })
    populations = Arithmetic_Dict({
        "nobles": 20,
        "artisans": 30,
        "peasants": 40,
        "others": 50
    })
    net_worths_change = Arithmetic_Dict({
        "nobles": 60,
        "artisans": 30000,
        "peasants": 40,
        "others": 60
    })
    rel_tax = state._get_personal_taxes(populations, net_worths) + \
        state._get_property_taxes() + \
        state._get_income_taxes(net_worths_change, net_worths)

    noble_tax = state.classes[0].real_resources * rel_tax["nobles"]
    artisan_tax = state.classes[1].real_resources
    peasant_tax = state.classes[2].real_resources * rel_tax["peasants"]
    other_tax = state.classes[3].real_resources * rel_tax["others"]

    noble_after = state.classes[0].resources - noble_tax
    artisan_after = state.classes[1].resources - artisan_tax
    peasant_after = state.classes[2].resources - peasant_tax
    other_after = state.classes[3].resources - other_tax
    govt_after = state.government.resources + noble_tax + artisan_tax + \
        peasant_tax + other_tax

    state._do_taxes(net_worths - net_worths_change)

    assert state.classes[0].new_resources == noble_after
    assert state.classes[1].new_resources == artisan_after
    assert state.classes[2].new_resources == peasant_after
    assert state.classes[3].new_resources == other_after
    assert state.government.new_resources == govt_after


def test_do_transfer_from_government():
    data = {
        "year": 3,
        "month": "June",
        "classes": {
            "nobles": {
                "population": 20,
                "resources": {
                    "food": 10,
                    "wood": 10,
                    "stone": 10,
                    "iron": 10,
                    "tools": 10,
                    "land": 10
                }
            },
            "artisans": {
                "population": 30,
                "resources": {
                    "food": 20,
                    "wood": 20,
                    "stone": 20,
                    "iron": 20,
                    "tools": 20,
                    "land": 20
                }
            },
            "peasants": {
                "population": 40,
                "resources": {
                    "food": 40,
                    "wood": 40,
                    "stone": 40,
                    "iron": 40,
                    "tools": 40,
                    "land": 40
                }
            },
            "others": {
                "population": 50,
                "resources": {
                    "food": 50,
                    "wood": 100,
                    "stone": 50,
                    "iron": 50,
                    "tools": 100,
                    "land": 50
                }
            }
        },
        "government": {
            "resources": {
                "food": 10,
                "wood": 10,
                "stone": 10,
                "iron": 10,
                "tools": 10,
                "land": 10
            },
            "optimal_resources": {
                "food": 0,
                "wood": 0,
                "stone": 0,
                "iron": 0,
                "tools": 0,
                "land": 0
            }
        },
        "prices": {
            "food": 1,
            "wood": 2,
            "stone": 3,
            "iron": 4,
            "tools": 5,
            "land": 5
        }
    }
    state = State_Data.from_dict(data)
    state.do_transfer("nobles", "food", 10)
    assert state.classes[0].resources == {
        "food": 20,
        "wood": 10,
        "stone": 10,
        "iron": 10,
        "tools": 10,
        "land": 10
    }
    assert state.government.resources == {
        "food": 0,
        "wood": 10,
        "stone": 10,
        "iron": 10,
        "tools": 10,
        "land": 10
    }


def test_do_transfer_to_government():
    data = {
        "year": 3,
        "month": "June",
        "classes": {
            "nobles": {
                "population": 20,
                "resources": {
                    "food": 10,
                    "wood": 10,
                    "stone": 10,
                    "iron": 10,
                    "tools": 10,
                    "land": 10
                }
            },
            "artisans": {
                "population": 30,
                "resources": {
                    "food": 20,
                    "wood": 20,
                    "stone": 20,
                    "iron": 20,
                    "tools": 20,
                    "land": 20
                }
            },
            "peasants": {
                "population": 40,
                "resources": {
                    "food": 40,
                    "wood": 40,
                    "stone": 40,
                    "iron": 40,
                    "tools": 40,
                    "land": 40
                }
            },
            "others": {
                "population": 50,
                "resources": {
                    "food": 50,
                    "wood": 100,
                    "stone": 50,
                    "iron": 50,
                    "tools": 100,
                    "land": 50
                }
            }
        },
        "government": {
            "resources": {
                "food": 10,
                "wood": 10,
                "stone": 10,
                "iron": 10,
                "tools": 10,
                "land": 10
            },
            "optimal_resources": {
                "food": 0,
                "wood": 0,
                "stone": 0,
                "iron": 0,
                "tools": 0,
                "land": 0
            }
        },
        "prices": {
            "food": 1,
            "wood": 2,
            "stone": 3,
            "iron": 4,
            "tools": 5,
            "land": 5
        }
    }
    state = State_Data.from_dict(data)
    state.do_transfer("artisans", "tools", -15)
    assert state.classes[1].resources == {
        "food": 20,
        "wood": 20,
        "stone": 20,
        "iron": 20,
        "tools": 5,
        "land": 20
    }
    assert state.government.resources == {
        "food": 10,
        "wood": 10,
        "stone": 10,
        "iron": 10,
        "tools": 25,
        "land": 10
    }


def test_do_transfer_to_government_demotion():
    data = {
        "year": 3,
        "month": "June",
        "classes": {
            "nobles": {
                "population": 20,
                "resources": {
                    "food": 10,
                    "wood": 10,
                    "stone": 10,
                    "iron": 10,
                    "tools": 10,
                    "land": 10
                }
            },
            "artisans": {
                "population": 30,
                "resources": {
                    "food": 20,
                    "wood": 20,
                    "stone": 20,
                    "iron": 20,
                    "tools": 20,
                    "land": 20
                }
            },
            "peasants": {
                "population": 40,
                "resources": {
                    "food": 40,
                    "wood": 40,
                    "stone": 40,
                    "iron": 40,
                    "tools": 40,
                    "land": 40
                }
            },
            "others": {
                "population": 50,
                "resources": {
                    "food": 50,
                    "wood": 100,
                    "stone": 50,
                    "iron": 50,
                    "tools": 100,
                    "land": 50
                }
            }
        },
        "government": {
            "resources": {
                "food": 10,
                "wood": 10,
                "stone": 10,
                "iron": 10,
                "tools": 10,
                "land": 10
            },
            "optimal_resources": {
                "food": 0,
                "wood": 0,
                "stone": 0,
                "iron": 0,
                "tools": 0,
                "land": 0
            }
        },
        "prices": {
            "food": 1,
            "wood": 2,
            "stone": 3,
            "iron": 4,
            "tools": 5,
            "land": 5
        }
    }
    state = State_Data.from_dict(data)
    state.do_transfer("artisans", "tools", -25)
    assert state.classes[1].demoted_from
    assert state.classes[3].demoted_to
    assert state.government.resources == {
        "food": 10,
        "wood": 10,
        "stone": 10,
        "iron": 10,
        "tools": 35,
        "land": 10
    }


def test_do_secure_make_secure():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 100,
        "stone": 100,
        "iron": 100,
        "tools": 350,
        "land": 100
    }
    state.government = Government(state, resources)
    assert state.government.resources == resources
    assert state.government.secure_resources == EMPTY_RESOURCES

    state.do_secure("wood", 80)
    assert state.government.resources == {
        "food": 100,
        "wood": 20,
        "stone": 100,
        "iron": 100,
        "tools": 350,
        "land": 100
    }
    assert state.government.secure_resources == {
        "food": 0,
        "wood": 80,
        "stone": 0,
        "iron": 0,
        "tools": 0,
        "land": 0
    }

    state.do_secure("tools", 350)
    assert state.government.resources == {
        "food": 100,
        "wood": 20,
        "stone": 100,
        "iron": 100,
        "tools": 0,
        "land": 100
    }
    assert state.government.secure_resources == {
        "food": 0,
        "wood": 80,
        "stone": 0,
        "iron": 0,
        "tools": 350,
        "land": 0
    }


def test_do_secure_make_insecure():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 100,
        "stone": 100,
        "iron": 100,
        "tools": 350,
        "land": 100
    }
    secure_res = {
        "food": 100,
        "wood": 100,
        "stone": 0,
        "iron": 100,
        "tools": 350,
        "land": 0
    }
    state.government = Government(state, resources, secure_res=secure_res)
    assert state.government.resources == resources
    assert state.government.secure_resources == secure_res

    state.do_secure("wood", -80)
    assert state.government.resources == {
        "food": 100,
        "wood": 180,
        "stone": 100,
        "iron": 100,
        "tools": 350,
        "land": 100
    }
    assert state.government.secure_resources == {
        "food": 100,
        "wood": 20,
        "stone": 0,
        "iron": 100,
        "tools": 350,
        "land": 0
    }

    state.do_secure("iron", -100)
    assert state.government.resources == {
        "food": 100,
        "wood": 180,
        "stone": 100,
        "iron": 200,
        "tools": 350,
        "land": 100
    }
    assert state.government.secure_resources == {
        "food": 100,
        "wood": 20,
        "stone": 0,
        "iron": 0,
        "tools": 350,
        "land": 0
    }


def test_do_optimal():
    state = State_Data()
    resources = {
        "food": 100,
        "wood": 100,
        "stone": 100,
        "iron": 100,
        "tools": 350,
        "land": 100
    }
    opt_res = {
        "food": 100,
        "wood": 100,
        "stone": 0,
        "iron": 100,
        "tools": 350,
        "land": 0
    }
    state.government = Government(state, resources, opt_res)
    assert state.government.resources == resources
    assert state.government.optimal_resources == opt_res
    assert state.government.optimal_resources is not opt_res

    opt_res = {
        "food": 100,
        "wood": 150,
        "stone": 0,
        "iron": 100,
        "tools": 350,
        "land": 0
    }
    state.do_optimal("wood", 150)
    assert state.government.optimal_resources == opt_res

    opt_res = {
        "food": 100,
        "wood": 150,
        "stone": 0,
        "iron": 100,
        "tools": 200,
        "land": 0
    }
    state.do_optimal("tools", 200)
    assert state.government.optimal_resources == opt_res


def test_execute_commands():
    def fake_do_month(self):
        self.did_month += 1

    def fake_transfer(self, class_name, resource, amount):
        self.transfers.append([class_name, resource, amount])

    def fake_secure(self, resource, amount):
        self.secures.append([resource, amount])

    def fake_optimal(self, resource, amount):
        self.optimals.append([resource, amount])

    old_do_month = State_Data.do_month
    old_transfer = State_Data.do_transfer
    old_secure = State_Data.do_secure
    old_optimal = State_Data.do_optimal
    State_Data.do_month = fake_do_month
    State_Data.do_transfer = fake_transfer
    State_Data.do_secure = fake_secure
    State_Data.do_optimal = fake_optimal

    state = State_Data()
    state.did_month = 0
    state.transfers = []
    state.secures = []
    state.optimals = []

    state.execute_commands(["next 2"])
    assert state.did_month == 2
    assert state.transfers == []
    assert state.secures == []
    assert state.optimals == []

    state.execute_commands(["next 100", "transfer nobles food 100"])
    assert state.did_month == 102
    assert state.transfers == [
        ["nobles", "food", 100]
    ]
    assert state.secures == []
    assert state.optimals == []

    state.execute_commands(["next 1", "next 1", "next 2",
                            "secure food 200"])
    assert state.did_month == 106
    assert state.transfers == [
        ["nobles", "food", 100]
    ]
    assert state.secures == [
        ["food", 200]
    ]
    assert state.optimals == []

    state.execute_commands(["transfer nobles food -100",
                            "transfer artisans land 50",
                            "secure tools 340",
                            "optimal wood 1000"])
    assert state.did_month == 106
    assert state.transfers == [
        ["nobles", "food", 100],
        ["nobles", "food", -100],
        ["artisans", "land", 50]
    ]
    assert state.secures == [
        ["food", 200],
        ["tools", 340]
    ]
    assert state.optimals == [
        ["wood", 1000]
    ]

    state.execute_commands(["optimal iron 0"])
    assert state.did_month == 106
    assert state.transfers == [
        ["nobles", "food", 100],
        ["nobles", "food", -100],
        ["artisans", "land", 50]
    ]
    assert state.secures == [
        ["food", 200],
        ["tools", 340]
    ]
    assert state.optimals == [
        ["wood", 1000],
        ["iron", 0]
    ]

    State_Data.do_month = old_do_month
    State_Data.do_transfer = old_transfer
    State_Data.do_secure = old_secure
    State_Data.do_optimal = old_optimal
