from ..classes.market import Market
from ..classes.state_data import State_Data
from ..classes.nobles import Nobles
from ..classes.artisans import Artisans
from ..classes.peasants import Peasants
from ..classes.others import Others
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


def test_operation_on_dict_addition():
    resources = {
        "food": 400,
        "wood": 300,
        "stone": 200,
        "iron": 100,
        "tools": 50
    }
    resources1 = {
        "food": 40,
        "wood": 30,
        "stone": 20,
        "iron": 100,
        "tools": 50
    }
    assert Market.operation_on_dict(
        resources,
        resources1,
        lambda a, b: a + b
    ) == {
        "food": 440,
        "wood": 330,
        "stone": 220,
        "iron": 200,
        "tools": 100
    }


def test_operation_on_dict_division():
    resources = {
        "food": 400,
        "wood": 300,
        "stone": 200,
        "iron": 100,
        "tools": 5
    }
    resources1 = {
        "food": 40,
        "wood": 30,
        "stone": 20,
        "iron": 100,
        "tools": 50
    }
    assert Market.operation_on_dict(
        resources,
        resources1,
        lambda a, b: a / b
    ) == {
        "food": 10,
        "wood": 10,
        "stone": 10,
        "iron": 1,
        "tools": approx(0.1)
    }


class Fake_State_Data(State_Data):
    def __init__(self, available_employees, month="January"):
        self._month = month
        self.available_employees = available_employees
        self.payments = {
            "food": 0,
            "wood": 0,
            "iron": 0,
            "stone": 0,
            "tools": 0
        }

    def get_available_employees(self):
        return self.available_employees


class Fake_Social_Class:
    def __init__(self, resources, optimal_resources):
        self.resources = resources
        self.optimal_resources = optimal_resources


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
        "food": approx(0.483, abs=1e-3),
        "wood": approx(0.469, abs=1e-3),
        "stone": approx(0.455, abs=1e-3),
        "iron": 0,
        "tools": approx(0.429, abs=1e-3)
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
    market._set_prices()
    market._buy_needed_resources()

    assert class1.money == approx(91.8, abs=0.1)
    assert class1.new_resources == {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    assert class2.money == approx(275.4, abs=0.1)
    assert class2.new_resources == {
        "food": 50,
        "wood": 50,
        "stone": 50,
        "iron": 0,
        "tools": 50
    }
    assert class3.money == 0
    assert class3.new_resources == {
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
    market._buy_needed_resources()
    market._buy_other_resources()

    assert class1.money == 0
    assert class1.new_resources == {
        "food": approx(95.8, abs=0.1),
        "wood": approx(98.3, abs=0.1),
        "stone": approx(100.8, abs=0.1),
        "iron": approx(85.0, abs=0.1),
        "tools": approx(105.8, abs=0.1)
    }
    assert class2.money == 0
    assert class2.new_resources == {
        "food": approx(187.3, abs=0.1),
        "wood": approx(194.8, abs=0.1),
        "stone": approx(202.3, abs=0.1),
        "iron": approx(255.0, abs=0.1),
        "tools": approx(217.3, abs=0.1)
    }
    assert class3.money == 0
    assert class3.new_resources == {
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
    market._set_prices()
    market._buy_needed_resources()
    market._delete_trade_attributes()

    assert not hasattr(market, "available_resources")
    assert not hasattr(market, "needed_resources")
    for social_class in social_classes:
        assert not hasattr(social_class, "money")
        assert not hasattr(social_class, "new_resources")
        assert social_class.resources == {
            "food": 50,
            "wood": 50,
            "stone": 50,
            "iron": 0,
            "tools": 50
        }


def test_do_trade():
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
    market.do_trade()

    assert class1.resources == {
        "food": approx(95.8, abs=0.1),
        "wood": approx(98.3, abs=0.1),
        "stone": approx(100.8, abs=0.1),
        "iron": approx(85.0, abs=0.1),
        "tools": approx(105.8, abs=0.1)
    }
    assert class2.resources == {
        "food": approx(187.3, abs=0.1),
        "wood": approx(194.8, abs=0.1),
        "stone": approx(202.3, abs=0.1),
        "iron": approx(255.0, abs=0.1),
        "tools": approx(217.3, abs=0.1)
    }
    assert class3.resources == {
        "food": approx(26.9, abs=0.1),
        "wood": approx(26.9, abs=0.1),
        "stone": approx(26.9, abs=0.1),
        "iron": 0,
        "tools": approx(26.9, abs=0.1)
    }
