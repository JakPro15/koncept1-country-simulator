from ..sources.state.market import Market
from ..sources.state.state_data import State_Data
from ..sources.state.social_classes.nobles import Nobles
from ..sources.state.social_classes.artisans import Artisans
from ..sources.state.social_classes.peasants import Peasants
from ..sources.state.social_classes.others import Others
from ..sources.auxiliaries.arithmetic_dict import Arithmetic_Dict
from ..sources.auxiliaries.constants import DEFAULT_PRICES
from pytest import approx


def test_constructor():
    state = State_Data()
    nobles = Nobles(state, 50)
    peasants = Peasants(state, 100)
    artisans = Artisans(state, 100)
    others = Others(state, 200)
    social_classes = [nobles, artisans, peasants, others]
    market = Market(social_classes)

    assert market.classes[0] == nobles
    assert market.classes[1] == artisans
    assert market.classes[2] == peasants
    assert market.classes[3] == others


class Fake_State_Data(State_Data):
    def __init__(self, available_employees, month="January"):
        self._month = month
        self.available_employees = available_employees
        self.payments = Arithmetic_Dict({
            "food": 0,
            "wood": 0,
            "iron": 0,
            "stone": 0,
            "tools": 0
        })

    def get_available_employees(self):
        return self.available_employees


class Fake_Social_Class:
    def __init__(self, resources, optimal_resources):
        self.resources = Arithmetic_Dict(resources)
        self.optimal_resources = Arithmetic_Dict(optimal_resources)
        self.population = 1
        self.flushed = False

    def flush(self):
        self.flushed = True


def test_get_available_and_needed_resources():
    resources = {
        "food": 100,
        "wood": 100,
        "stone": 100,
        "iron": 100,
        "tools": 100
    }
    optimal_resources = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    class1 = Fake_Social_Class(resources, optimal_resources)

    resources = {
        "food": 200,
        "wood": 200,
        "stone": 200,
        "iron": 200,
        "tools": 200
    }
    optimal_resources = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    class2 = Fake_Social_Class(resources, optimal_resources)

    resources = {
        "food": 10,
        "wood": 20,
        "stone": 30,
        "iron": 40,
        "tools": 50
    }
    optimal_resources = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    class3 = Fake_Social_Class(resources, optimal_resources)

    social_classes = [class1, class2, class3]
    market = Market(social_classes)
    market._get_available_and_needed_resources()
    assert market.available_resources == {
        "food": 310,
        "wood": 320,
        "stone": 330,
        "iron": 340,
        "tools": 350
    }
    assert market.needed_resources == {
        "food": 150,
        "wood": 150,
        "stone": 150,
        "iron": 0,
        "tools": 150
    }


def test_set_prices():
    resources = {
        "food": 100,
        "wood": 100,
        "stone": 100,
        "iron": 100,
        "tools": 100
    }
    optimal_resources = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    class1 = Fake_Social_Class(resources, optimal_resources)

    resources = {
        "food": 200,
        "wood": 200,
        "stone": 200,
        "iron": 200,
        "tools": 200
    }
    optimal_resources = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    class2 = Fake_Social_Class(resources, optimal_resources)

    resources = {
        "food": 10,
        "wood": 20,
        "stone": 30,
        "iron": 40,
        "tools": 50
    }
    optimal_resources = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    class3 = Fake_Social_Class(resources, optimal_resources)

    social_classes = [class1, class2, class3]
    market = Market(social_classes)
    market._get_available_and_needed_resources()
    market._set_prices()
    assert market.prices == {
        "food": approx(0.483 * DEFAULT_PRICES["food"], abs=1e-2),
        "wood": approx(0.469 * DEFAULT_PRICES["wood"], abs=1e-2),
        "stone": approx(0.455 * DEFAULT_PRICES["stone"], abs=1e-2),
        "iron": DEFAULT_PRICES["iron"],
        "tools": approx(0.429 * DEFAULT_PRICES["tools"], abs=1e-2)
    }


def test_buy_needed_resources():
    resources = {
        "food": 100,
        "wood": 100,
        "stone": 100,
        "iron": 100,
        "tools": 100
    }
    optimal_resources = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    class1 = Fake_Social_Class(resources, optimal_resources)

    resources = {
        "food": 200,
        "wood": 200,
        "stone": 200,
        "iron": 200,
        "tools": 200
    }
    optimal_resources = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    class2 = Fake_Social_Class(resources, optimal_resources)

    resources = {
        "food": 10,
        "wood": 20,
        "stone": 30,
        "iron": 40,
        "tools": 50
    }
    optimal_resources = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    class3 = Fake_Social_Class(resources, optimal_resources)

    social_classes = [class1, class2, class3]
    market = Market(social_classes)
    market._get_available_and_needed_resources()
    market.prices = Arithmetic_Dict({
        "food": 0.483,
        "wood": 0.469,
        "stone": 0.455,
        "iron": 0,
        "tools": 0.429
    })
    market._buy_needed_resources()

    assert class1.money == approx(91.8, abs=0.1)
    assert class1.market_res == {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    assert class2.money == approx(275.4, abs=0.1)
    assert class2.market_res == {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    assert class3.money == 0
    assert class3.market_res == {
        "food": approx(26.9, abs=0.1),
        "wood": approx(26.9, abs=0.1),
        "stone": approx(26.9, abs=0.1),
        "iron": 0,
        "tools": approx(26.9, abs=0.1)
    }

    assert market.available_resources == {
        "food": approx(183.1, abs=0.1),
        "wood": approx(193.1, abs=0.1),
        "stone": approx(203.1, abs=0.1),
        "iron": approx(340, abs=0.1),
        "tools": approx(223.1, abs=0.1)
    }


def test_buy_other_resources():
    resources = {
        "food": 100,
        "wood": 100,
        "stone": 100,
        "iron": 100,
        "tools": 100
    }
    market_res = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    optimal_resources = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    class1 = Fake_Social_Class(resources, optimal_resources)
    class1.money = 91.8
    class1.market_res = Arithmetic_Dict(market_res)

    resources = {
        "food": 200,
        "wood": 200,
        "stone": 200,
        "iron": 200,
        "tools": 200
    }
    market_res = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    optimal_resources = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    class2 = Fake_Social_Class(resources, optimal_resources)
    class2.money = 275.4
    class2.market_res = Arithmetic_Dict(market_res)

    resources = {
        "food": 10,
        "wood": 20,
        "stone": 30,
        "iron": 40,
        "tools": 50
    }
    market_res = {
        "food": 26.9,
        "wood": 26.9,
        "stone": 26.9,
        "iron": 0,
        "tools": 26.9
    }
    optimal_resources = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    class3 = Fake_Social_Class(resources, optimal_resources)
    class3.money = 0
    class3.market_res = Arithmetic_Dict(market_res)

    social_classes = [class1, class2, class3]
    market = Market(social_classes)
    market.available_resources = Arithmetic_Dict({
        "food": 183.1,
        "wood": 193.1,
        "stone": 203.1,
        "iron": 340,
        "tools": 223.1
    })
    market.needed_resources = Arithmetic_Dict({
        "food": 150,
        "wood": 150,
        "stone": 150,
        "iron": 0,
        "tools": 150
    })
    market.prices = Arithmetic_Dict({
        "food": 0.483,
        "wood": 0.469,
        "stone": 0.455,
        "iron": 0,
        "tools": 0.429
    })
    market._buy_other_resources()

    assert class1.money == 0
    assert class1.market_res == {
        "food": approx(95.8, abs=0.1),
        "wood": approx(98.3, abs=0.1),
        "stone": approx(100.8, abs=0.1),
        "iron": approx(85.0, abs=0.1),
        "tools": approx(105.8, abs=0.1)
    }
    assert class2.money == 0
    assert class2.market_res == {
        "food": approx(187.3, abs=0.1),
        "wood": approx(194.8, abs=0.1),
        "stone": approx(202.3, abs=0.1),
        "iron": approx(255.0, abs=0.1),
        "tools": approx(217.3, abs=0.1)
    }
    assert class3.money == 0
    assert class3.market_res == {
        "food": approx(26.9, abs=0.1),
        "wood": approx(26.9, abs=0.1),
        "stone": approx(26.9, abs=0.1),
        "iron": 0,
        "tools": approx(26.9, abs=0.1)
    }

    assert market.available_resources == {
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }


def test_delete_trade_attributes():
    resources = {
        "food": 100,
        "wood": 100,
        "stone": 100,
        "iron": 100,
        "tools": 100
    }
    optimal_resources = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    class1 = Fake_Social_Class(resources, optimal_resources)

    resources = {
        "food": 200,
        "wood": 200,
        "stone": 200,
        "iron": 200,
        "tools": 200
    }
    optimal_resources = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    class2 = Fake_Social_Class(resources, optimal_resources)

    social_classes = [class1, class2]
    market = Market(social_classes)
    market._get_available_and_needed_resources()
    market.prices = DEFAULT_PRICES
    market._buy_needed_resources()
    market._delete_trade_attributes()

    assert not hasattr(market, "available_resources")
    assert not hasattr(market, "needed_resources")
    for social_class in social_classes:
        assert social_class.flushed
        assert not hasattr(social_class, "money")
        assert not hasattr(social_class, "market_res")
        assert social_class.resources == {
            "food": 50,
            "wood": 50,
            "stone": 50,
            "iron": 0,
            "tools": 50
        }


def test_do_trade():  # EXCEL CALCULATIONS USED
    resources = {
        "food": 100,
        "wood": 100,
        "stone": 100,
        "iron": 100,
        "tools": 100
    }
    optimal_resources = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    class1 = Fake_Social_Class(resources, optimal_resources)

    resources = {
        "food": 200,
        "wood": 200,
        "stone": 200,
        "iron": 200,
        "tools": 200
    }
    optimal_resources = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    class2 = Fake_Social_Class(resources, optimal_resources)

    resources = {
        "food": 10,
        "wood": 20,
        "stone": 30,
        "iron": 40,
        "tools": 50
    }
    optimal_resources = {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 1,
        "tools": 50
    }
    class3 = Fake_Social_Class(resources, optimal_resources)

    social_classes = [class1, class2, class3]
    market = Market(social_classes)
    market.do_trade()

    assert class1.resources == {
        "food": approx(94.2, abs=0.1),
        "wood": approx(96.7, abs=0.1),
        "stone": approx(99.2, abs=0.1),
        "iron": approx(84.9, abs=0.1),
        "tools": approx(104.2, abs=0.1)
    }
    assert class2.resources == {
        "food": approx(182.3, abs=0.1),
        "wood": approx(189.8, abs=0.1),
        "stone": approx(197.3, abs=0.1),
        "iron": approx(254.4, abs=0.1),
        "tools": approx(212.3, abs=0.1)
    }
    assert class3.resources == {
        "food": approx(33.6, abs=0.1),
        "wood": approx(33.6, abs=0.1),
        "stone": approx(33.6, abs=0.1),
        "iron": approx(0.7, abs=0.1),
        "tools": approx(33.6, abs=0.1)
    }
