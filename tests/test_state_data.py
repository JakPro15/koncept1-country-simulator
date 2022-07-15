from sources.state.social_classes.class_file import Class
from ..sources.state.state_data import (
    State_Data, Nobles, Artisans, Peasants, Others, Government
)
from ..sources.auxiliaries.constants import (
    BRIGAND_STRENGTH,
    DEFAULT_GROWTH_FACTOR,
    DEFAULT_PRICES,
    EMPTY_RESOURCES,
    FOOD_CONSUMPTION,
    FREEZING_MORTALITY,
    INBUILT_RESOURCES,
    MAX_PRICES,
    OTHERS_MINIMUM_WAGE,
    RECRUITMENT_COST,
    RESOURCES,
    STARVATION_MORTALITY,
    TAX_RATES,
    WAGE_CHANGE,
    WOOD_CONSUMPTION,
    INCREASE_PRICE_FACTOR
)
from ..sources.auxiliaries.arithmetic_dict import Arithmetic_Dict
from ..sources.auxiliaries.testing import dict_eq
from pytest import approx, raises
from ..sources.auxiliaries.testing import replace


def test_constructor():
    state = State_Data("August", 3)
    assert state.month == "August"
    assert state.year == 3
    assert state.prices == DEFAULT_PRICES
    assert state.prices is not DEFAULT_PRICES


def test_default_constructor():
    state = State_Data()
    assert state.month == "January"
    assert state.year == 0
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
                },
                "happiness": -1
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
                },
                "happiness": 2
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
                },
                "happiness": 3
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
                },
                "happiness": -4
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
            },
            "secure_resources": {
                "food": 7,
                "wood": 2,
                "stone": 3,
                "iron": 7,
                "tools": 7,
                "land": 6
            }
        },
        "prices": {
            "food": 0.1,
            "wood": 0.2,
            "stone": 0.3,
            "iron": 1.4,
            "tools": 0.5,
            "land": 2.6
        },
        "laws": {
            "tax_personal": {
                "nobles": 2,
                "artisans": 3,
                "peasants": 1,
                "others": 4
            },
            "tax_property": {
                "nobles": 0.2,
                "artisans": 0.3,
                "peasants": 0.1,
                "others": 0.4
            },
            "tax_income": {
                "nobles": 0.1,
                "artisans": 0.1,
                "peasants": 0.1,
                "others": 0.1
            },
            "wage_minimum": 0.2,
            "wage_government": 0.4,
            "wage_autoregulation": False,
            "max_prices": {
                "food": 2,
                "wood": 3,
                "stone": 4,
                "iron": 5,
                "tools": 6,
                "land": 10
            }
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
    assert state.classes[0].happiness == -1

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
    assert state.classes[1].happiness == 2

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
    assert state.classes[2].happiness == 3

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
    assert state.classes[3].happiness == -4

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
    assert state.government.secure_resources == {
        "food": 7,
        "wood": 2,
        "stone": 3,
        "iron": 7,
        "tools": 7,
        "land": 6
    }

    assert state.sm.tax_rates["personal"] == {
        "nobles": 2,
        "artisans": 3,
        "peasants": 1,
        "others": 4
    }
    assert state.sm.tax_rates["property"] == {
        "nobles": 0.2,
        "artisans": 0.3,
        "peasants": 0.1,
        "others": 0.4
    }
    assert state.sm.tax_rates["income"] == {
        "nobles": 0.1,
        "artisans": 0.1,
        "peasants": 0.1,
        "others": 0.1
    }
    assert state.sm.others_minimum_wage == 0.2
    assert state.government.wage == 0.4
    assert state.government.wage_autoregulation is False
    assert state.sm.max_prices == {
        "food": 2,
        "wood": 3,
        "stone": 4,
        "iron": 5,
        "tools": 6,
        "land": 10
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
                },
                "happiness": 0
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
                },
                "happiness": 0
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
                },
                "happiness": 0
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
                },
                "happiness": 0
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
            },
            "secure_resources": {
                "food": 0,
                "wood": 0,
                "stone": 0,
                "iron": 0,
                "tools": 0,
                "land": 0
            }
        },
        "prices": {
            "food": 0.1,
            "wood": 0.2,
            "stone": 0.3,
            "iron": 1.4,
            "tools": 0.5,
            "land": 10
        },
        "laws": {
            "tax_personal": TAX_RATES["personal"],
            "tax_property": TAX_RATES["property"],
            "tax_income": TAX_RATES["income"],
            "wage_minimum": OTHERS_MINIMUM_WAGE,
            "wage_government": OTHERS_MINIMUM_WAGE,
            "wage_autoregulation": True,
            "max_prices": {
                resource: MAX_PRICES
                for resource
                in RESOURCES
            }
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
            },
            "secure_resources": {
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
            },
            "secure_resources": {
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
    assert state.classes[0].happiness == Class.starvation_happiness(1)

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
    assert state.classes[1].happiness == Class.starvation_happiness(
        dead_artisans / 50
    )

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
    assert state.classes[2].happiness == Class.starvation_happiness(
        dead_peasants / 100
    )

    assert state.classes[3].new_population == \
        50 - 30 * FREEZING_MORTALITY / WOOD_CONSUMPTION["January"]
    assert state.classes[3].new_resources == EMPTY_RESOURCES
    assert state.classes[3].population == 50
    assert not state.classes[3].starving
    assert state.classes[3].freezing
    assert state.classes[3].happiness == Class.starvation_happiness(
        (30 * FREEZING_MORTALITY / WOOD_CONSUMPTION["January"]) / 50
    )


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
    # entire class demoted - all their resources moved
    assert artisans.new_resources == EMPTY_RESOURCES - \
        INBUILT_RESOURCES["artisans"] * 50
    assert artisans.demoted_from
    assert not artisans.demoted_to

    assert peasants.new_population == 50
    assert peasants.new_resources == \
        HUNDREDS + INBUILT_RESOURCES["peasants"] * 10
    assert peasants.demoted_from
    assert peasants.demoted_to

    assert others.new_population == 110
    assert others.new_resources == HUNDREDS + \
        INBUILT_RESOURCES["artisans"] * 50 + HUNDREDS
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
        5000, 100, (increase_price_artisans + increase_price_peasants) / 2
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
        5000, 100, (increase_price_artisans + increase_price_peasants) / 2
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
            },
            "secure_resources": {
                "food": 71,
                "wood": 72,
                "stone": 73,
                "iron": 74,
                "tools": 75,
                "land": 76
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

    assert state.classes[0].happiness == \
        Class.resources_seized_happiness(rel_tax["nobles"])
    assert state.classes[1].happiness == \
        Class.resources_seized_happiness(1)
    assert state.classes[2].happiness == \
        Class.resources_seized_happiness(rel_tax["peasants"])
    assert state.classes[3].happiness == \
        Class.resources_seized_happiness(rel_tax["others"])


def test_get_crime_rate():
    happinesses = [(x - 50) / 1000 for x in range(3000)]
    old = 1
    for happiness in happinesses:
        flee_rate = State_Data._get_flee_rate(happiness)
        assert 0 <= flee_rate <= 1
        assert flee_rate <= old
        old = flee_rate


def test_add_brigands():
    state = State_Data()
    assert state.brigands == 0

    state._add_brigands(10, 1)
    assert state.brigands == 10
    assert state.brigand_strength == 1

    state._add_brigands(10, 0.5)
    assert state.brigands == 20
    assert state.brigand_strength == approx(0.75)

    state._add_brigands(10, 2)
    assert state.brigands == 30
    assert state.brigand_strength == approx(1.1667, abs=0.001)

    state._add_brigands(30, 0.8333333)
    assert state.brigands == 60
    assert state.brigand_strength == approx(1, abs=0.001)


def test_total_population():
    state = State_Data()
    state.government = Government(state, None, None, None,
                                  {"knights": 10, "footmen": 30})
    state.classes = [
        Nobles(state, 22),
        Artisans(state, 33),
        Peasants(state, 44),
        Others(state, 55)
    ]
    state.brigands = 15
    assert state.total_population == 209

    state.brigands = 6
    assert state.total_population == 200

    state.classes[2]._population = 54
    assert state.total_population == 210

    state.classes[0]._population = 20
    assert state.total_population == 208

    state.government.soldiers["footmen"] = 12
    assert state.total_population == 190


def test_do_theft():
    state = State_Data()
    res0 = EMPTY_RESOURCES.copy()
    res0["food"] = 10
    res0["land"] = 20
    res0["stone"] = 50
    state.government = Government(state, res0, None, res0,
                                  {"knights": 10, "footmen": 30})
    res1 = EMPTY_RESOURCES.copy()
    res1["food"] = 100
    res1["stone"] = 50
    res2 = EMPTY_RESOURCES.copy()
    res2["wood"] = 100
    res2["land"] = 50
    res3 = EMPTY_RESOURCES.copy()
    res3["iron"] = 10
    res3["tools"] = 500
    state.classes = [
        Nobles(state, 22, res1),
        Artisans(state, 33, res2),
        Peasants(state, 40, res3),
        Others(state, 50)
    ]
    state.brigands = 15

    res1 -= state.classes[0].real_resources * 0.0375
    res1["land"] = 0
    res2 -= state.classes[1].real_resources * 0.0375
    res2["land"] = 50
    res3 -= state.classes[2].real_resources * 0.0375
    res3["land"] = 0
    res0 *= 0.925
    res0["land"] = 20

    state._do_theft()
    assert state.government.new_resources == res0
    assert state.classes[0].new_resources == res1
    assert state.classes[0].happiness < 0
    assert state.classes[1].new_resources == res2
    assert state.classes[1].happiness < 0
    assert state.classes[2].new_resources == res3
    assert state.classes[2].happiness < 0
    assert state.classes[3].new_resources == EMPTY_RESOURCES
    assert state.classes[3].happiness == 0


def test_make_new_brigands():
    class Fake_Class:
        def __init__(self, happiness, population, name):
            self.happiness = happiness
            self.population = population
            self.new_population = population
            self.class_name = name

    def fake_add_brigands(self, number, strength):
        self.brigands_added.append([number, strength])

    with replace(State_Data, "_add_brigands", fake_add_brigands):
        state = State_Data()
        state.brigands_added = []
        state._classes = [
            Fake_Class(-20, 100, "nobles"),
            Fake_Class(10, 120, "artisans"),
            Fake_Class(-50, 200, "peasants"),
            Fake_Class(0, 12, "others")
        ]
        state.government = Government(state)
        state.government.soldiers = {
            "knights": 20,
            "footmen": 80
        }
        state.government.missing_food = 40

        flee_rate_1 = State_Data._get_flee_rate(-20)
        flee_rate_2 = State_Data._get_flee_rate(-50)
        flee_rate_3 = State_Data._get_flee_rate(-40)

        state._make_new_brigands()

        assert state.brigands_added == [
            [approx(100 * flee_rate_1), BRIGAND_STRENGTH["nobles"]],
            [approx(200 * flee_rate_2), BRIGAND_STRENGTH["peasants"]],
            [approx(20 * flee_rate_3), BRIGAND_STRENGTH["knights"]],
            [approx(80 * flee_rate_3), BRIGAND_STRENGTH["footmen"]]
        ]
        assert state.classes[0].new_population == 100 * (1 - flee_rate_1)
        assert state.classes[1].new_population == 120
        assert state.classes[2].new_population == 200 * (1 - flee_rate_2)
        assert state.classes[3].new_population == 12
        assert state.government.soldiers["knights"] == 20 * (1 - flee_rate_3)
        assert state.government.soldiers["footmen"] == 80 * (1 - flee_rate_3)


def test_do_crime():
    def fake_do_theft(self):
        self.did_theft = True

    def fake_make_new_brigands(self):
        self.made_new_brigands = True

    with replace(State_Data, "_do_theft", fake_do_theft), \
         replace(State_Data, "_make_new_brigands", fake_make_new_brigands):
        state = State_Data()
        state._do_crime()

    assert state.did_theft
    assert state.made_new_brigands


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
            },
            "secure_resources": {
                "food": 71,
                "wood": 72,
                "stone": 73,
                "iron": 74,
                "tools": 75,
                "land": 76
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
    part_seized = -10 / state.classes[0].net_worth
    state.do_transfer("nobles", "food", 10)
    assert state.classes[0].resources == {
        "food": 20,
        "wood": 10,
        "stone": 10,
        "iron": 10,
        "tools": 10,
        "land": 10
    }
    assert state.classes[0].happiness == Class.resources_seized_happiness(
        part_seized
    )
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
            },
            "secure_resources": {
                "food": 71,
                "wood": 72,
                "stone": 73,
                "iron": 74,
                "tools": 75,
                "land": 76
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
    part_seized = 75 / state.classes[1].net_worth
    state.do_transfer("artisans", "tools", -15)
    assert state.classes[1].resources == {
        "food": 20,
        "wood": 20,
        "stone": 20,
        "iron": 20,
        "tools": 5,
        "land": 20
    }
    assert state.classes[1].happiness == Class.resources_seized_happiness(
        part_seized
    )
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
            },
            "secure_resources": {
                "food": 71,
                "wood": 72,
                "stone": 73,
                "iron": 74,
                "tools": 75,
                "land": 76
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
    part_seized = 125 / state.classes[1].net_worth
    state.do_transfer("artisans", "tools", -25)
    assert state.classes[1].demoted_from
    assert state.classes[1].happiness == Class.resources_seized_happiness(
        part_seized
    )
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


def test_do_set_law():
    state = State_Data()
    assert state.sm.tax_rates["property"] == TAX_RATES["property"]
    state.do_set_law("tax_property", "artisans", 0.9)
    assert state.sm.tax_rates["property"]["nobles"] == \
        TAX_RATES["property"]["nobles"]
    assert state.sm.tax_rates["property"]["artisans"] == 0.9
    assert state.sm.tax_rates["property"]["peasants"] == \
        TAX_RATES["property"]["peasants"]
    assert state.sm.tax_rates["property"]["others"] == \
        TAX_RATES["property"]["others"]

    assert state.sm.tax_rates["income"] == TAX_RATES["income"]
    state.do_set_law("tax_income", "others", 0)
    assert state.sm.tax_rates["income"]["others"] == 0.0

    assert state.sm.others_minimum_wage == OTHERS_MINIMUM_WAGE
    state.do_set_law("wage_minimum", None, 0.4)
    assert state.sm.others_minimum_wage == 0.4


def test_set_wages_and_employers():
    class Fake_Class_6:
        def __init__(self, resources, wage=None):
            self.real_resources = resources
            if wage:
                self.wage = wage

    res_land = {"land": 1}
    res_no_land = {"land": 0}
    state = State_Data()
    state.sm.others_minimum_wage = 0.15
    classes = [
        Fake_Class_6(res_land, 0.8),
        Fake_Class_6(res_no_land),
        Fake_Class_6(res_land, 0.1),
        Fake_Class_6(res_land),
        Fake_Class_6(res_no_land, 0.2),
    ]
    state._classes = classes.copy()

    govt = Fake_Class_6(res_land, 0.5)
    state._government = govt

    employers = state._set_wages_and_employers()
    assert employers == [
        classes[0],
        classes[2],
        classes[3],
        govt
    ]
    assert classes[0].wage == 0.8
    assert not hasattr(classes[1], "wage")
    assert classes[2].wage == 0.15
    assert classes[3].wage == 0.15
    assert classes[4].wage == 0.2
    assert govt.wage == 0.5


def test_set_wage_shares_and_employees_no_employer_max():
    class Employer:
        def __init__(self, max_employees):
            self.max_employees = max_employees
            self.employable = False

    class Employee:
        def __init__(self, population):
            self.population = population
            self.employable = True

    employers = [
        Employer(200),
        Employer(50),
        Employer(80),
        Employer(100),
    ]

    classes = [
        employers[2],
        Employee(150),
        Employee(40),
        employers[0],
        Employee(100)
    ]
    state = State_Data()
    state._classes = classes

    employees_classes, employees = state._set_employees_and_wage_shares(
        employers
    )
    assert employees_classes == [
        classes[1], classes[2], classes[4]
    ]
    assert employees == 290
    assert classes[1].wage_share == 150 / 290
    assert classes[2].wage_share == 40 / 290
    assert classes[4].wage_share == 100 / 290


def test_set_wage_shares_and_employees_with_employer_max():
    class Employer:
        def __init__(self, max_employees):
            self.max_employees = max_employees
            self.employable = False

    class Employee:
        def __init__(self, population):
            self.population = population
            self.employable = True

    employers = [
        Employer(20),
        Employer(5),
        Employer(8),
        Employer(10),
    ]

    classes = [
        employers[2],
        Employee(150),
        Employee(40),
        employers[0],
        Employee(100)
    ]
    state = State_Data()
    state._classes = classes

    employees_classes, employees = state._set_employees_and_wage_shares(
        employers
    )
    assert employees_classes == [
        classes[1], classes[2], classes[4]
    ]
    assert employees == 43
    assert classes[1].wage_share == 150 / 290
    assert classes[2].wage_share == 40 / 290
    assert classes[4].wage_share == 100 / 290


def test_get_ratios():
    dicti = Arithmetic_Dict({
        "a": 3,
        "b": 3,
        "c": 3,
        "d": 1
    })
    result = State_Data._get_ratios(dicti)
    assert result == dicti / 10

    del dicti["c"]
    result = State_Data._get_ratios(dicti)
    assert result == dicti / 7

    dicti["nobles"] = 93
    result = State_Data._get_ratios(dicti)
    assert result == dicti / 100

    dicti = Arithmetic_Dict({
        "a": 0,
        "b": 0,
        "c": 0
    })
    result = State_Data._get_ratios(dicti)
    assert result == dicti


def test_get_tools_used():
    state = State_Data()
    state.sm.peasant_tool_usage = 0.5
    state.sm.miner_tool_usage = 1.5
    employees = {
        "food": 20,
        "wood": 30,
        "stone": 40,
        "iron": 60
    }
    assert state._get_tools_used(employees) == 175

    state.sm.peasant_tool_usage = 1
    state.sm.miner_tool_usage = 3
    employees = {
        "food": 2.5,
        "wood": 3.5,
        "stone": 4.5,
        "iron": 6.5
    }
    assert state._get_tools_used(employees) == 39


def test_add_employees():
    class Empty_Class:
        pass

    employers = [
        Empty_Class(),
        Empty_Class(),
        Empty_Class()
    ]
    employees = {
        employers[0]: 20,
        employers[1]: 30,
        employers[2]: 65,
    }
    State_Data._add_employees(employees)

    assert employers[0].employees == 20
    assert employers[1].employees == 30
    assert employers[2].employees == 65

    employers.append(Empty_Class())
    employees = {
        employers[0]: 20,
        employers[1]: 5,
        employers[2]: 15,
        employers[3]: 40
    }
    State_Data._add_employees(employees)

    assert employers[0].employees == 40
    assert employers[1].employees == 35
    assert employers[2].employees == 80
    assert employers[3].employees == 40


class Employer_Class:
    def __init__(self, wage, max_emps):
        self.wage = wage
        self.max_employees = max_emps


def test_set_employers_employees_no_max():
    employers = [
        Employer_Class(2, 500),
        Employer_Class(5, 500),
        Employer_Class(3, 500)
    ]
    employees = 400
    State_Data._set_employers_employees(employers, employees, 4/15)

    assert employers[0].employees == 80
    assert employers[1].employees == 200
    assert employers[2].employees == 120

    assert employers[0].increase_wage
    assert not employers[1].increase_wage
    assert employers[2].increase_wage

    employers = [
        Employer_Class(2, 500),
        Employer_Class(5, 500)
    ]
    employees = 700
    State_Data._set_employers_employees(employers, employees, 0.7)

    assert employers[0].employees == 200
    assert employers[1].employees == 500

    assert employers[0].increase_wage
    assert not employers[1].increase_wage


def test_set_employers_employees_with_max():
    employers = [
        Employer_Class(2, 50),
        Employer_Class(5, 500),
        Employer_Class(3, 500)
    ]
    employees = 850
    State_Data._set_employers_employees(employers, employees, 85/105)

    assert employers[0].employees == 50
    assert employers[1].employees == 500
    assert employers[2].employees == 300

    assert not employers[0].increase_wage
    assert not employers[1].increase_wage
    assert employers[2].increase_wage

    employers = [
        Employer_Class(2, 50),
        Employer_Class(5, 600),
        Employer_Class(3, 250),
        Employer_Class(0, 500)
    ]
    employees = 850
    State_Data._set_employers_employees(employers, employees, 85/140)

    assert employers[0].employees == 50
    assert employers[1].employees == 550
    assert employers[2].employees == 250
    assert employers[3].employees == 0

    assert not employers[0].increase_wage
    assert not employers[1].increase_wage
    assert not employers[2].increase_wage
    assert employers[3].increase_wage


def test_set_employers_employees_not_all_employed():
    employers = [
        Employer_Class(2, 50),
        Employer_Class(5, 100),
        Employer_Class(3, 150)
    ]
    employees = 850
    State_Data._set_employers_employees(employers, employees, 1)

    assert employers[0].employees == 50
    assert employers[1].employees == 100
    assert employers[2].employees == 150

    assert not employers[0].increase_wage
    assert not employers[1].increase_wage
    assert not employers[2].increase_wage

    employers = [
        Employer_Class(0, 50),
        Employer_Class(0, 600),
        Employer_Class(0, 250),
        Employer_Class(0, 500)
    ]
    employees = 850
    State_Data._set_employers_employees(employers, employees, 85/140)

    assert employers[0].employees == 0
    assert employers[1].employees == 0
    assert employers[2].employees == 0
    assert employers[3].employees == 0

    assert employers[0].increase_wage
    assert employers[1].increase_wage
    assert employers[2].increase_wage
    assert employers[3].increase_wage


def test_get_produced_and_used():
    ratioed_employees = {
        "food": 20,
        "wood": 40,
        "stone": 10,
        "iron": 30,
    }

    state = State_Data("June")
    food_production = state.sm.food_production["June"]
    state.sm.wood_production = 2
    state.sm.stone_production = 1.2
    state.sm.iron_production = 1.5

    produced, used = state._get_produced_and_used(ratioed_employees)
    assert produced == {
        "food": food_production * 20,
        "wood": 80,
        "stone": 12,
        "iron": 45
    }
    assert used == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": state._get_tools_used(ratioed_employees),
        "land": 0
    }


class Employer_Class_2:
    def __init__(self, employees):
        self.employees = employees


def test_employees_to_profit():
    employers = [
        Employer_Class_2(50),
        Employer_Class_2(150),
        Employer_Class_2(500),
        Employer_Class_2(300)
    ]
    State_Data._employees_to_profit(employers)

    assert employers[0].profit_share == 0.05
    assert employers[1].profit_share == 0.15
    assert employers[2].profit_share == 0.5
    assert employers[3].profit_share == 0.3

    employers = [
        Employer_Class_2(50),
        Employer_Class_2(150),
        Employer_Class_2(50)
    ]
    State_Data._employees_to_profit(employers)

    assert employers[0].profit_share == 0.2
    assert employers[1].profit_share == 0.6
    assert employers[2].profit_share == 0.2


def test_get_monetary_value():
    state = State_Data()
    state.prices = Arithmetic_Dict({
        "food": 1,
        "wood": 2,
        "stone": 3,
        "iron": 4,
        "tools": 5,
        "land": 6
    })
    resources = {
        "food": 1,
        "wood": 20,
        "stone": 300,
    }
    assert state._get_monetary_value(resources) == 941

    resources = {
        "food": 1,
        "wood": 10,
        "stone": 100,
        "iron": 1000,
        "tools": 10000,
        "land": 100000
    }
    assert state._get_monetary_value(resources) == 654321

    resources = {
        "food": 34,
        "wood": 10,
        "stone": 100,
        "iron": 0,
        "land": 10
    }
    assert state._get_monetary_value(resources) == 414


def test_distribute_produced_and_used():
    class Employer:
        def __init__(self, wage, profit_share, new_resources):
            self.wage = wage
            self.profit_share = profit_share
            self.new_resources = new_resources.copy()

    class Employee:
        def __init__(self, wage_share, new_resources):
            self.wage_share = wage_share
            self.new_resources = new_resources.copy()

    state = State_Data()
    state.prices = Arithmetic_Dict({
        "food": 1,
        "wood": 1,
        "stone": 1,
        "iron": 1,
        "tools": 1,
        "land": 1
    })

    resources = Arithmetic_Dict({
        "food": 100,
        "wood": 100,
        "stone": 100,
        "iron": 100,
        "tools": 100,
        "land": 100
    })
    employers = [
        Employer(0.2, 0.3, resources),
        Employer(0.3, 0.2, EMPTY_RESOURCES),
        Employer(0.5, 0.5, resources)
    ]
    employees = [
        Employee(0.4, resources),
        Employee(0.6, EMPTY_RESOURCES)
    ]
    produced = Arithmetic_Dict({
        "food": 100,
        "wood": 100,
        "stone": 100,
        "iron": 100
    })
    used = Arithmetic_Dict({
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 10,
        "land": 0
    })
    state._distribute_produced_and_used(employers, employees,
                                        produced, used)
    assert state.max_wage == 0.975

    assert employers[0].new_resources == {
        "food": 124,
        "wood": 124,
        "stone": 124,
        "iron": 124,
        "tools": 97,
        "land": 100
    }
    assert employers[1].new_resources == {
        "food": 14,
        "wood": 14,
        "stone": 14,
        "iron": 14,
        "tools": -2,
        "land": 0
    }
    assert employers[2].new_resources == {
        "food": 125,
        "wood": 125,
        "stone": 125,
        "iron": 125,
        "tools": 95,
        "land": 100
    }
    assert employees[0].new_resources == {
        "food": 114.8,
        "wood": 114.8,
        "stone": 114.8,
        "iron": 114.8,
        "tools": 100,
        "land": 100
    }
    assert employees[1].new_resources == {
        "food": 22.2,
        "wood": 22.2,
        "stone": 22.2,
        "iron": 22.2,
        "tools": 0,
        "land": 0
    }


def test_set_new_wages_no_max_wage():
    class Employer:
        def __init__(self, wage, increase_wage):
            self.wage = wage
            self.increase_wage = increase_wage

    state = State_Data()

    employers = [
        Employer(0.5, True),
        Employer(1 - WAGE_CHANGE, True),
        Employer(0.5, False),
        Employer(WAGE_CHANGE, False),
        Employer(WAGE_CHANGE / 2, False),
        Employer(1 - WAGE_CHANGE / 2, True),
    ]
    state._set_new_wages(employers)
    assert employers[0].wage == 0.5 + WAGE_CHANGE
    assert employers[1].wage == 1
    assert employers[2].wage == 0.5 - WAGE_CHANGE
    assert employers[3].wage == 0
    assert employers[4].wage == 0
    assert employers[5].wage == 1


def test_set_new_wages_with_max_wage():
    class Employer:
        def __init__(self, wage, increase_wage):
            self.wage = wage
            self.increase_wage = increase_wage

    state = State_Data()
    state.max_wage = 0.8

    employers = [
        Employer(0.4, True),
        Employer(1 - WAGE_CHANGE, True),
        Employer(0.4, False),
        Employer(WAGE_CHANGE, True),
        Employer(WAGE_CHANGE / 2, False),
        Employer(1 - WAGE_CHANGE / 2, False),
    ]
    state._set_new_wages(employers)
    assert employers[0].wage == 0.4 + WAGE_CHANGE
    assert employers[1].wage == 0.8
    assert employers[2].wage == 0.4 - WAGE_CHANGE
    assert employers[3].wage == 2 * WAGE_CHANGE
    assert employers[4].wage == 0
    assert employers[5].wage == 0.8


def test_do_force_promotion():
    data = {
        "year": 0,
        "month": "January",
        "classes": {
            "nobles": {
                "population": 20,
                "resources": {
                    "food": 0,
                    "wood": 240,
                    "stone": 0,
                    "iron": 50,
                    "tools": 0,
                    "land": 10
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
                "food": 1061,
                "wood": 1062,
                "stone": 1063,
                "iron": 1064,
                "tools": 1065,
                "land": 10200
            },
            "optimal_resources": {
                "food": 71,
                "wood": 72,
                "stone": 73,
                "iron": 74,
                "tools": 75,
                "land": 76
            },
            "secure_resources": {
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

    promotion_cost = (INBUILT_RESOURCES["nobles"] -
                      INBUILT_RESOURCES["peasants"]) * 5

    state.do_force_promotion("nobles", 5)
    assert state.classes[0].population == 25
    assert state.classes[1].population == 50
    assert state.classes[2].population == 95
    assert state.classes[3].population == 50

    dict_eq(state.classes[0].resources, {
        "food": 0,
        "wood": 240,
        "stone": 0,
        "iron": 50,
        "tools": 0,
        "land": 10
    })
    dict_eq(state.classes[1].resources, {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0,
        "land": 0
    })
    dict_eq(state.classes[2].resources, {
        "food": 20,
        "wood": 18,
        "stone": 0,
        "iron": 0,
        "tools": 0,
        "land": 0
    })
    dict_eq(state.classes[3].resources, {
        "food": 0,
        "wood": 30,
        "stone": 0,
        "iron": 0,
        "tools": 0,
        "land": 0
    })
    dict_eq(state.government.resources, Arithmetic_Dict({
        "food": 1061,
        "wood": 1062,
        "stone": 1063,
        "iron": 1064,
        "tools": 1065,
        "land": 10200
    }) - promotion_cost)


def test_do_recruit():
    class Fake_Class:
        def __init__(self):
            self.new_population = 50

        def handle_negative_resources(self):
            pass

        def handle_empty_class(self):
            pass

    state = State_Data()
    res = Arithmetic_Dict({
        "food": 1000,
        "wood": 1000,
        "stone": 1000,
        "iron": 1000,
        "tools": 1000,
        "land": 1000
    })
    state.government = Government(state, res)
    state._classes = [Fake_Class(), Fake_Class()]

    state.do_recruit("nobles", 10)
    assert state.classes[0].new_population == 40
    assert state.classes[1].new_population == 50
    assert state.government.resources == res - RECRUITMENT_COST["knights"] * 10
    assert state.government.soldiers == {
        "knights": 10,
        "footmen": 0
    }

    state.do_recruit("artisans", 40)
    assert state.classes[0].new_population == 40
    assert state.classes[1].new_population == 10
    assert state.government.resources == res - \
        RECRUITMENT_COST["knights"] * 10 - RECRUITMENT_COST["footmen"] * 40
    assert state.government.soldiers == {
        "knights": 10,
        "footmen": 40
    }


def test_execute_commands():
    def fake_do_month(self):
        self.did_month += 1

    def fake_transfer(self, class_name, resource, amount):
        self.transfers.append([class_name, resource, amount])

    def fake_secure(self, resource, amount):
        self.secures.append([resource, amount])

    def fake_optimal(self, resource, amount):
        self.optimals.append([resource, amount])

    def fake_set_law(self, law, social_class, value):
        self.setlaws.append([law, social_class, value])

    def fake_force_promotion(self, social_class, value):
        self.forcepromos.append([social_class, value])

    with replace(State_Data, "do_month", fake_do_month), \
         replace(State_Data, "do_transfer", fake_transfer), \
         replace(State_Data, "do_secure", fake_secure), \
         replace(State_Data, "do_optimal", fake_optimal), \
         replace(State_Data, "do_set_law", fake_set_law), \
         replace(State_Data, "do_force_promotion", fake_force_promotion):
        state = State_Data()
        state.did_month = 0
        state.transfers = []
        state.secures = []
        state.optimals = []
        state.setlaws = []
        state.forcepromos = []

        state.execute_commands(["next 2"])
        assert state.did_month == 2
        assert state.transfers == []
        assert state.secures == []
        assert state.optimals == []
        assert state.setlaws == []
        assert state.forcepromos == []

        state.execute_commands(["next 100", "transfer nobles food 100"])
        assert state.did_month == 102
        assert state.transfers == [
            ["nobles", "food", 100]
        ]
        assert state.secures == []
        assert state.optimals == []
        assert state.setlaws == []
        assert state.forcepromos == []

        state.execute_commands(["next 1", "next 1", "next 2",
                                "secure food 200",
                                "laws set tax_property nobles 0.4",
                                "promote artisans 50"])
        assert state.did_month == 106
        assert state.transfers == [
            ["nobles", "food", 100]
        ]
        assert state.secures == [
            ["food", 200]
        ]
        assert state.optimals == []
        assert state.setlaws == [
            ["tax_property", "nobles", 0.4]
        ]
        assert state.forcepromos == [
            ["artisans", 50]
        ]

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
        assert state.setlaws == [
            ["tax_property", "nobles", 0.4]
        ]
        assert state.forcepromos == [
            ["artisans", 50]
        ]

        state.execute_commands(["optimal iron 0",
                                "promote nobles 10",
                                "laws set wage_minimum None 0",
                                "laws set tax_income peasants 0.9",
                                "promote peasants 34"])
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
        assert state.setlaws == [
            ["tax_property", "nobles", 0.4],
            ["wage_minimum", None, 0.0],
            ["tax_income", "peasants", 0.9]
        ]
        assert state.forcepromos == [
            ["artisans", 50],
            ["nobles", 10],
            ["peasants", 34]
        ]
