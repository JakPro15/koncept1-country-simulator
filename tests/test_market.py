from ..sources.state.market import Market, SupportsTrade
from ..sources.state.state_data import State_Data
from ..sources.state.social_classes.nobles import Nobles
from ..sources.state.social_classes.artisans import Artisans
from ..sources.state.social_classes.peasants import Peasants
from ..sources.state.social_classes.others import Others
from ..sources.auxiliaries.resources import Resources
from ..sources.auxiliaries.enums import Resource, Month
from ..sources.auxiliaries.constants import DEFAULT_PRICES
from pytest import approx  # type: ignore


def test_constructor():
    state = State_Data()
    nobles = Nobles(state, 50)
    peasants = Peasants(state, 100)
    artisans = Artisans(state, 100)
    others = Others(state, 200)
    social_classes = [nobles, artisans, peasants, others]
    market = Market(social_classes, state)

    assert market.parent is state

    assert market.trading_objs[0] == nobles
    assert market.trading_objs[1] == artisans
    assert market.trading_objs[2] == peasants
    assert market.trading_objs[3] == others


class Fake_State_Data(State_Data):
    def __init__(self, available_employees: float,
                 month: Month = Month.January) -> None:
        self.month = month
        self.available_employees = available_employees

    def get_available_employees(self) -> float:
        return self.available_employees


class Trading_Obj(SupportsTrade):
    def __init__(self, resources: Resources, optimal_resources: Resources
                 ) -> None:
        self.resources = resources
        self._optimal_resources = optimal_resources
        self.market_res: Resources
        self.money: float

    @property
    def optimal_resources(self) -> Resources:
        return self._optimal_resources

    @optimal_resources.setter
    def optimal_resources(self, new: Resources) -> None:
        self._optimal_resources = new


def test_get_available_and_needed_resources():
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 100,
        Resource.stone: 100,
        Resource.iron: 100,
        Resource.tools: 100,
        Resource.land: 0
    })
    optimal_resources = Resources({
        Resource.food: 50,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50,
        Resource.land: 0
    })
    class1 = Trading_Obj(resources, optimal_resources)

    resources = Resources({
        Resource.food: 200,
        Resource.wood: 200,
        Resource.stone: 200,
        Resource.iron: 200,
        Resource.tools: 200,
        Resource.land: 0
    })
    optimal_resources = Resources({
        Resource.food: 50,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50,
        Resource.land: 0
    })
    class2 = Trading_Obj(resources, optimal_resources)

    resources = Resources({
        Resource.food: 10,
        Resource.wood: 20,
        Resource.stone: 30,
        Resource.iron: 40,
        Resource.tools: 50,
        Resource.land: 0
    })
    optimal_resources = Resources({
        Resource.food: 50,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50,
        Resource.land: 0
    })
    class3 = Trading_Obj(resources, optimal_resources)

    social_classes = [class1, class2, class3]
    state = State_Data()
    market = Market(social_classes, state)
    market._get_available_and_needed_resources()  # type: ignore
    assert market.available_resources == Resources({
        Resource.food: 310,
        Resource.wood: 320,
        Resource.stone: 330,
        Resource.iron: 340,
        Resource.tools: 350,
        Resource.land: 0
    })
    assert market.needed_resources == Resources({
        Resource.food: 150,
        Resource.wood: 150,
        Resource.stone: 150,
        Resource.iron: 0,
        Resource.tools: 150,
        Resource.land: 0
    })


def test_set_prices():  # EXCEL CALCULATIONS USED
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 100,
        Resource.stone: 100,
        Resource.iron: 100,
        Resource.tools: 100,
        Resource.land: 100
    })
    optimal_resources = Resources({
        Resource.food: 50,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50,
        Resource.land: 50
    })
    class1 = Trading_Obj(resources, optimal_resources)

    resources = Resources({
        Resource.food: 200,
        Resource.wood: 200,
        Resource.stone: 200,
        Resource.iron: 200,
        Resource.tools: 200,
        Resource.land: 200
    })
    optimal_resources = Resources({
        Resource.food: 50,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50,
        Resource.land: 0
    })
    class2 = Trading_Obj(resources, optimal_resources)

    resources = Resources({
        Resource.food: 1,
        Resource.wood: 2,
        Resource.stone: 3,
        Resource.iron: 4,
        Resource.tools: 5,
        Resource.land: 6
    })
    optimal_resources = Resources({
        Resource.food: 10,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50,
        Resource.land: 50
    })
    class3 = Trading_Obj(resources, optimal_resources)

    social_classes = [class1, class2, class3]
    state = State_Data()
    market = Market(social_classes, state)
    market._get_available_and_needed_resources()  # type: ignore
    market.old_avail_res = Resources({
        Resource.food: 300,
        Resource.wood: 300,
        Resource.stone: 305,
        Resource.iron: 305,
        Resource.tools: 300,
        Resource.land: 300,
    })
    market._set_prices()  # type: ignore
    assert market.prices == {
        Resource.food: approx(0.367 * DEFAULT_PRICES.food, abs=1e-2),
        Resource.wood: approx(0.316 * DEFAULT_PRICES.wood, abs=1e-2),
        Resource.stone: approx(3.942 * DEFAULT_PRICES.stone, abs=1e-2),
        Resource.iron: approx(1.859 * DEFAULT_PRICES.iron, abs=1e-2),
        Resource.tools: approx(0.249 * DEFAULT_PRICES.tools, abs=1e-2),
        Resource.land: approx(0.165 * DEFAULT_PRICES.land, abs=1e-2),
    }


def test_buy_needed_resources():
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 100,
        Resource.stone: 100,
        Resource.iron: 100,
        Resource.tools: 100,
        Resource.land: 0
    })
    optimal_resources = Resources({
        Resource.food: 50,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50,
        Resource.land: 0
    })
    class1 = Trading_Obj(resources, optimal_resources)

    resources = Resources({
        Resource.food: 200,
        Resource.wood: 200,
        Resource.stone: 200,
        Resource.iron: 200,
        Resource.tools: 200,
        Resource.land: 0
    })
    optimal_resources = Resources({
        Resource.food: 50,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50,
        Resource.land: 0
    })
    class2 = Trading_Obj(resources, optimal_resources)

    resources = Resources({
        Resource.food: 10,
        Resource.wood: 20,
        Resource.stone: 30,
        Resource.iron: 40,
        Resource.tools: 50,
        Resource.land: 0
    })
    optimal_resources = Resources({
        Resource.food: 50,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50,
        Resource.land: 0
    })
    class3 = Trading_Obj(resources, optimal_resources)

    social_classes = [class1, class2, class3]
    state = State_Data()
    market = Market(social_classes, state)
    market._get_available_and_needed_resources()  # type: ignore
    market.prices = Resources({
        Resource.food: 0.483,
        Resource.wood: 0.469,
        Resource.stone: 0.455,
        Resource.iron: 0,
        Resource.tools: 0.429,
        Resource.land: DEFAULT_PRICES.land
    })
    market._full_prices = market.prices  # type: ignore
    market._buy_needed_resources()  # type: ignore

    assert class1.money == approx(91.8, abs=0.1)
    assert class1.market_res == Resources({
        Resource.food: 50,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50,
        Resource.land: 0
    })
    assert class2.money == approx(275.4, abs=0.1)
    assert class2.market_res == Resources({
        Resource.food: 50,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50,
        Resource.land: 0
    })
    assert class3.money == 0
    assert class3.market_res == {
        Resource.food: approx(26.9, abs=0.1),
        Resource.wood: approx(26.9, abs=0.1),
        Resource.stone: approx(26.9, abs=0.1),
        Resource.iron: 0,
        Resource.tools: approx(26.9, abs=0.1),
        Resource.land: 0
    }

    assert market.available_resources == {
        Resource.food: approx(183.1, abs=0.1),
        Resource.wood: approx(193.1, abs=0.1),
        Resource.stone: approx(203.1, abs=0.1),
        Resource.iron: approx(340, abs=0.1),
        Resource.tools: approx(223.1, abs=0.1),
        Resource.land: 0
    }


def test_buy_other_resources():
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 100,
        Resource.stone: 100,
        Resource.iron: 100,
        Resource.tools: 100,
        Resource.land: 0
    })
    market_res = Resources({
        Resource.food: 50,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50,
        Resource.land: 0
    })
    optimal_resources = Resources({
        Resource.food: 50,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50,
        Resource.land: 0
    })
    class1 = Trading_Obj(resources, optimal_resources)
    class1.money = 91.8
    class1.market_res = Resources(market_res)

    resources = Resources({
        Resource.food: 200,
        Resource.wood: 200,
        Resource.stone: 200,
        Resource.iron: 200,
        Resource.tools: 200,
        Resource.land: 0
    })
    market_res = Resources({
        Resource.food: 50,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50,
        Resource.land: 0
    })
    optimal_resources = Resources({
        Resource.food: 50,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50,
        Resource.land: 0
    })
    class2 = Trading_Obj(resources, optimal_resources)
    class2.money = 275.4
    class2.market_res = Resources(market_res)

    resources = Resources({
        Resource.food: 10,
        Resource.wood: 20,
        Resource.stone: 30,
        Resource.iron: 40,
        Resource.tools: 50,
        Resource.land: 0
    })
    market_res = Resources({
        Resource.food: 26.9,
        Resource.wood: 26.9,
        Resource.stone: 26.9,
        Resource.iron: 0,
        Resource.tools: 26.9,
        Resource.land: 0
    })
    optimal_resources = Resources({
        Resource.food: 50,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50,
        Resource.land: 0
    })
    class3 = Trading_Obj(resources, optimal_resources)
    class3.money = 0
    class3.market_res = Resources(market_res)

    social_classes = [class1, class2, class3]
    state = State_Data()
    market = Market(social_classes, state)
    market.available_resources = Resources({
        Resource.food: 183.1,
        Resource.wood: 193.1,
        Resource.stone: 203.1,
        Resource.iron: 340,
        Resource.tools: 223.1,
        Resource.land: 0
    })
    market.needed_resources = Resources({
        Resource.food: 150,
        Resource.wood: 150,
        Resource.stone: 150,
        Resource.iron: 0,
        Resource.tools: 150,
        Resource.land: 0
    })
    market.prices = Resources({
        Resource.food: 0.483,
        Resource.wood: 0.469,
        Resource.stone: 0.455,
        Resource.iron: 0,
        Resource.tools: 0.429,
        Resource.land: DEFAULT_PRICES.land
    })
    market._buy_other_resources()  # type: ignore

    assert class1.money == 0
    assert class1.market_res == {
        Resource.food: approx(95.8, abs=0.1),
        Resource.wood: approx(98.3, abs=0.1),
        Resource.stone: approx(100.8, abs=0.1),
        Resource.iron: approx(85.0, abs=0.1),
        Resource.tools: approx(105.8, abs=0.1),
        Resource.land: 0
    }
    assert class2.money == 0
    assert class2.market_res == {
        Resource.food: approx(187.3, abs=0.1),
        Resource.wood: approx(194.8, abs=0.1),
        Resource.stone: approx(202.3, abs=0.1),
        Resource.iron: approx(255.0, abs=0.1),
        Resource.tools: approx(217.3, abs=0.1),
        Resource.land: 0
    }
    assert class3.money == 0
    assert class3.market_res == {
        Resource.food: approx(26.9, abs=0.1),
        Resource.wood: approx(26.9, abs=0.1),
        Resource.stone: approx(26.9, abs=0.1),
        Resource.iron: 0,
        Resource.tools: approx(26.9, abs=0.1),
        Resource.land: 0
    }

    assert market.available_resources == Resources({
        Resource.food: 0,
        Resource.wood: 0,
        Resource.stone: 0,
        Resource.iron: 0,
        Resource.tools: 0,
        Resource.land: 0
    })


def test_delete_trade_attributes():
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 100,
        Resource.stone: 100,
        Resource.iron: 100,
        Resource.tools: 100
    })
    optimal_resources = Resources({
        Resource.food: 50,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50
    })
    class1 = Trading_Obj(resources, optimal_resources)

    resources = Resources({
        Resource.food: 200,
        Resource.wood: 200,
        Resource.stone: 200,
        Resource.iron: 200,
        Resource.tools: 200
    })
    optimal_resources = Resources({
        Resource.food: 50,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50
    })
    class2 = Trading_Obj(resources, optimal_resources)

    social_classes = [class1, class2]
    state = State_Data()
    market = Market(social_classes, state)
    market._get_available_and_needed_resources()  # type: ignore
    market.prices = DEFAULT_PRICES
    market._full_prices = DEFAULT_PRICES  # type: ignore
    market._buy_needed_resources()  # type: ignore
    market._delete_trade_attributes()  # type: ignore

    assert not hasattr(market, "available_resources")
    assert not hasattr(market, "needed_resources")
    for social_class in social_classes:
        assert not hasattr(social_class, "money")
        assert not hasattr(social_class, "market_res")
        assert social_class.resources == Resources({
            Resource.food: 50,
            Resource.wood: 50,
            Resource.stone: 50,
            Resource.iron: 0,
            Resource.tools: 50
        })


def test_do_trade():  # EXCEL CALCULATIONS USED
    resources = Resources({
        Resource.food: 100,
        Resource.wood: 100,
        Resource.stone: 100,
        Resource.iron: 100,
        Resource.tools: 100,
        Resource.land: 0
    })
    optimal_resources = Resources({
        Resource.food: 150,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50,
        Resource.land: 0
    })
    class1 = Trading_Obj(resources, optimal_resources)

    resources = Resources({
        Resource.food: 200,
        Resource.wood: 200,
        Resource.stone: 200,
        Resource.iron: 200,
        Resource.tools: 200,
        Resource.land: 0
    })
    optimal_resources = Resources({
        Resource.food: 150,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 0,
        Resource.tools: 50,
        Resource.land: 0
    })
    class2 = Trading_Obj(resources, optimal_resources)

    resources = Resources({
        Resource.food: 10,
        Resource.wood: 20,
        Resource.stone: 30,
        Resource.iron: 40,
        Resource.tools: 50,
        Resource.land: 0
    })
    optimal_resources = Resources({
        Resource.food: 50,
        Resource.wood: 50,
        Resource.stone: 50,
        Resource.iron: 1,
        Resource.tools: 50,
        Resource.land: 0
    })
    class3 = Trading_Obj(resources, optimal_resources)

    social_classes = [class1, class2, class3]
    state = State_Data()
    market = Market(social_classes, state)
    market.old_avail_res = Resources({
        Resource.food: 310,
        Resource.wood: 320,
        Resource.stone: 335,
        Resource.iron: 345,
        Resource.tools: 345,
        Resource.land: 0,
    })
    market.do_trade()

    assert class1.resources == {
        Resource.food: approx(132.8, abs=0.15),
        Resource.wood: approx(99.0, abs=0.15),
        Resource.stone: approx(101.9, abs=0.15),
        Resource.iron: approx(97.8, abs=0.15),
        Resource.tools: approx(107.7, abs=0.15),
        Resource.land: 0
    }
    assert class2.resources == {
        Resource.food: approx(132.9, abs=0.15),
        Resource.wood: approx(164.9, abs=0.15),
        Resource.stone: approx(171.7, abs=0.15),
        Resource.iron: approx(229.2, abs=0.15),
        Resource.tools: approx(185.2, abs=0.15),
        Resource.land: 0
    }
    assert class3.resources == {
        Resource.food: approx(44.3, abs=0.15),
        Resource.wood: approx(56.0, abs=0.15),
        Resource.stone: approx(56.4, abs=0.15),
        Resource.iron: approx(13.0, abs=0.15),
        Resource.tools: approx(57.1, abs=0.15),
        Resource.land: 0
    }
