from math import inf
from typing import Any

from pytest import approx  # type: ignore

from ..sources.auxiliaries.constants import (BASE_BATTLE_LOSSES,
                                             INBUILT_RESOURCES,
                                             KNIGHT_FIGHTING_STRENGTH,
                                             OTHERS_MINIMUM_WAGE,
                                             PLUNDER_FACTOR, RECRUITMENT_COST,
                                             TAX_RATES)
from ..sources.auxiliaries.enums import Class_Name, Resource, Soldier
from ..sources.auxiliaries.resources import Resources
from ..sources.auxiliaries.soldiers import Soldiers
from ..sources.auxiliaries.testing import replace
from ..sources.state.government import Government
from ..sources.state.social_classes.artisans import Artisans
from ..sources.state.social_classes.class_file import Class
from ..sources.state.social_classes.nobles import Nobles
from ..sources.state.social_classes.others import Others
from ..sources.state.social_classes.peasants import Peasants
from ..sources.state.state_data import State_Data


def test_generate_empty_state():
    state = State_Data.generate_empty_state()
    empties = [
        Nobles(state),
        Artisans(state),
        Peasants(state),
        Others(state)
    ]
    empties[0].lower_class = state.peasants
    empties[1].lower_class = state.others
    empties[2].lower_class = state.others
    empties[3].lower_class = state.others
    assert state.market is not None
    assert vars(state.nobles) == vars(empties[0])
    assert vars(state.artisans) == vars(empties[1])
    assert vars(state.peasants) == vars(empties[2])
    assert vars(state.others) == vars(empties[3])
    assert vars(state.government) == vars(Government(state))


def test_demote_now():
    demotions = 0
    secures = 0

    def fake_do_demotions(self: State_Data):
        nonlocal demotions
        demotions += 1

    def fake_secure_classes(self: State_Data):
        nonlocal secures
        secures += 1

    with replace(State_Data, "_do_demotions", fake_do_demotions), \
         replace(State_Data, "_secure_classes", fake_secure_classes):
        State_Data().demote_now()
        assert demotions == 1
        assert secures == 1

        State_Data().demote_now()
        assert demotions == 2
        assert secures == 2


def test_do_transfer_from_government():
    state = State_Data.generate_empty_state()
    state.nobles.population = 20
    state.nobles.resources = Resources(10)
    state.government.resources = Resources(10)
    state.prices = Resources({
        Resource.food: 1,
        Resource.wood: 2,
        Resource.stone: 3,
        Resource.iron: 4,
        Resource.tools: 5,
        Resource.land: 5
    })

    state.do_transfer(Class_Name.nobles, Resource.food, 10)
    assert state.nobles.resources == {
        Resource.food: 20,
        Resource.wood: 10,
        Resource.stone: 10,
        Resource.iron: 10,
        Resource.tools: 10,
        Resource.land: 10
    }
    assert state.nobles.happiness == Class.resources_seized_happiness(
        -0.5
    )
    assert state.government.resources == {
        Resource.food: 0,
        Resource.wood: 10,
        Resource.stone: 10,
        Resource.iron: 10,
        Resource.tools: 10,
        Resource.land: 10
    }


def test_do_transfer_to_government():
    state = State_Data.generate_empty_state()
    state.artisans.population = 30
    state.artisans.resources = Resources(20)
    state.government.resources = Resources(10)
    state.prices = Resources({
        Resource.food: 1,
        Resource.wood: 2,
        Resource.stone: 3,
        Resource.iron: 4,
        Resource.tools: 5,
        Resource.land: 5
    })

    state.do_transfer(Class_Name.artisans, Resource.tools, -15)
    assert state.artisans.resources == {
        Resource.food: 20,
        Resource.wood: 20,
        Resource.stone: 20,
        Resource.iron: 20,
        Resource.tools: 5,
        Resource.land: 20
    }
    assert state.artisans.happiness == Class.resources_seized_happiness(
        75 / 30
    )
    assert state.government.resources == {
        Resource.food: 10,
        Resource.wood: 10,
        Resource.stone: 10,
        Resource.iron: 10,
        Resource.tools: 25,
        Resource.land: 10
    }


def test_do_transfer_to_government_demotion():
    state = State_Data.generate_empty_state()
    state.artisans.population = 30
    state.artisans.resources = Resources(20)
    state.government.resources = Resources(10)
    state.prices = Resources({
        Resource.food: 1,
        Resource.wood: 2,
        Resource.stone: 3,
        Resource.iron: 4,
        Resource.tools: 5,
        Resource.land: 5
    })

    state.do_transfer(Class_Name.artisans, Resource.tools, -25)
    assert state.artisans.demoted_from
    assert state.artisans.happiness == Class.resources_seized_happiness(
        125 / 30
    )
    assert state.others.demoted_to
    assert state.government.resources == {
        Resource.food: 10,
        Resource.wood: 10,
        Resource.stone: 10,
        Resource.iron: 10,
        Resource.tools: 35,
        Resource.land: 10
    }


def test_do_secure_make_secure():
    state = State_Data()
    resources = Resources(100)
    resources.tools = 350

    state.government = Government(state, resources)
    assert state.government.resources == resources
    assert state.government.secure_resources == {}

    state.do_secure(Resource.wood, 80)
    assert state.government.resources == {
        Resource.food: 100,
        Resource.wood: 20,
        Resource.stone: 100,
        Resource.iron: 100,
        Resource.tools: 350,
        Resource.land: 100
    }
    assert state.government.secure_resources == {
        Resource.wood: 80
    }

    state.do_secure(Resource.tools, 350)
    assert state.government.resources == {
        Resource.food: 100,
        Resource.wood: 20,
        Resource.stone: 100,
        Resource.iron: 100,
        Resource.land: 100
    }
    assert state.government.secure_resources == {
        Resource.wood: 80,
        Resource.tools: 350
    }


def test_do_secure_make_insecure():
    state = State_Data()
    resources = Resources(100)
    resources.tools = 350
    secure_res = Resources({
        Resource.food: 100,
        Resource.wood: 100,
        Resource.iron: 100,
        Resource.tools: 350
    })

    state.government = Government(state, resources, secure_res=secure_res)
    assert state.government.resources == resources
    assert state.government.secure_resources == secure_res

    state.do_secure(Resource.wood, -80)
    assert state.government.resources == {
        Resource.food: 100,
        Resource.wood: 180,
        Resource.stone: 100,
        Resource.iron: 100,
        Resource.tools: 350,
        Resource.land: 100
    }
    assert state.government.secure_resources == {
        Resource.food: 100,
        Resource.wood: 20,
        Resource.iron: 100,
        Resource.tools: 350
    }

    state.do_secure(Resource.iron, -100)
    assert state.government.resources == {
        Resource.food: 100,
        Resource.wood: 180,
        Resource.stone: 100,
        Resource.iron: 200,
        Resource.tools: 350,
        Resource.land: 100
    }
    assert state.government.secure_resources == {
        Resource.food: 100,
        Resource.wood: 20,
        Resource.tools: 350
    }


def test_do_optimal():
    state = State_Data()
    resources = Resources(100)
    resources.tools = 350
    opt_res = Resources({
        Resource.food: 100,
        Resource.wood: 100,
        Resource.iron: 100,
        Resource.tools: 350
    })

    state.government = Government(state, resources, opt_res)
    assert state.government.resources == resources
    assert state.government.optimal_resources == opt_res

    state.do_optimal(Resource.wood, 150)
    assert state.government.optimal_resources == {
        Resource.food: 100,
        Resource.wood: 150,
        Resource.iron: 100,
        Resource.tools: 350,
    }

    state.do_optimal(Resource.tools, 200)
    assert state.government.optimal_resources == {
        Resource.food: 100,
        Resource.wood: 150,
        Resource.iron: 100,
        Resource.tools: 200
    }


def test_do_set_law():
    state = State_Data()
    assert state.sm.tax_rates["property"] == TAX_RATES["property"]
    state.do_set_law("tax_property", "artisans", 0.9)
    assert state.sm.tax_rates["property"][Class_Name.nobles] == \
        TAX_RATES["property"][Class_Name.nobles]
    assert state.sm.tax_rates["property"][Class_Name.artisans] == 0.9
    assert state.sm.tax_rates["property"][Class_Name.peasants] == \
        TAX_RATES["property"][Class_Name.peasants]
    assert state.sm.tax_rates["property"][Class_Name.others] == \
        TAX_RATES["property"][Class_Name.others]

    assert state.sm.tax_rates["income"] == TAX_RATES["income"]
    state.do_set_law("tax_income", "others", 0)
    assert state.sm.tax_rates["income"][Class_Name.others] == 0.0

    assert state.sm.others_minimum_wage == OTHERS_MINIMUM_WAGE
    state.do_set_law("wage_minimum", None, 0.4)
    assert state.sm.others_minimum_wage == 0.4


def test_do_force_promotion():
    state = State_Data.generate_empty_state()
    state.nobles.population = 20
    state.nobles.resources = Resources({
        Resource.wood: 240,
        Resource.iron: 50,
        Resource.land: 10
    })
    state.artisans.population = 50
    state.artisans.resources = Resources()
    state.peasants.population = 100
    state.peasants.resources = Resources({
        Resource.food: 20,
        Resource.wood: 18
    })
    state.others.population = 50
    state.others.resources = Resources({
        Resource.wood: 30
    })
    state.government.resources = Resources({
        Resource.food: 1061,
        Resource.wood: 1062,
        Resource.stone: 1063,
        Resource.iron: 1064,
        Resource.tools: 1065,
        Resource.land: 10200
    })

    promotion_cost = (INBUILT_RESOURCES[Class_Name.nobles] -
                      INBUILT_RESOURCES[Class_Name.peasants]) * 5

    state.do_force_promotion(Class_Name.nobles, 5)
    assert state.nobles.population == 25
    assert state.artisans.population == 50
    assert state.peasants.population == 95
    assert state.others.population == 50

    assert state.nobles.resources == {
        Resource.wood: 240,
        Resource.iron: 50,
        Resource.land: 10
    }
    assert state.artisans.resources == {}
    assert state.peasants.resources == {
        Resource.food: 20,
        Resource.wood: 18
    }
    assert state.others.resources == {
        Resource.wood: 30
    }
    assert state.government.resources == Resources({
        Resource.food: 1061,
        Resource.wood: 1062,
        Resource.stone: 1063,
        Resource.iron: 1064,
        Resource.tools: 1065,
        Resource.land: 10200
    }) - promotion_cost


def test_do_recruit():
    state = State_Data.generate_empty_state()
    state.nobles.population = 50
    state.nobles.resources = Resources()
    state.artisans.population = 50
    state.artisans.resources = Resources()
    state.government.resources = Resources(1000)

    state.do_recruit(Class_Name.nobles, 10)
    assert state.nobles.population == 40
    assert state.nobles.resources == INBUILT_RESOURCES[Class_Name.nobles] * 10
    assert state.artisans.population == 50
    assert state.artisans.resources == {}
    assert state.government.resources == \
        Resources(1000) - RECRUITMENT_COST[Soldier.knights] * 10
    assert state.government.soldiers == {
        Soldier.knights: 10
    }

    state.do_recruit(Class_Name.artisans, 40)
    assert state.nobles.population == 40
    assert state.nobles.resources == INBUILT_RESOURCES[Class_Name.nobles] * 10
    assert state.artisans.population == 10
    assert state.artisans.resources == \
        INBUILT_RESOURCES[Class_Name.artisans] * 40
    assert state.government.resources == Resources(1000) \
        - RECRUITMENT_COST[Soldier.knights] * 10 \
        - RECRUITMENT_COST[Soldier.footmen] * 40
    assert state.government.soldiers == {
        Soldier.knights: 10,
        Soldier.footmen: 40
    }


def test_get_battle_losses():
    assert State_Data._get_battle_losses(1) == (  # type: ignore
        BASE_BATTLE_LOSSES, BASE_BATTLE_LOSSES)
    assert State_Data._get_battle_losses(0) == (1, 0)  # type: ignore
    assert State_Data._get_battle_losses(inf) == (0, 1)  # type: ignore
    old_ally_rate, old_enemy_rate = 1, 0
    for i in range(1, 1000):
        ally_rate, enemy_rate = \
            State_Data._get_battle_losses(i)  # type: ignore
        assert 0 < ally_rate < old_ally_rate <= 1
        assert 0 <= old_enemy_rate < enemy_rate < 1
        old_ally_rate = ally_rate
        old_enemy_rate = enemy_rate


def test_do_fight_crime():
    state = State_Data()
    soldiers = Soldiers({
        Soldier.knights: 60 / KNIGHT_FIGHTING_STRENGTH,
        Soldier.footmen: 60
    })
    state.government = Government(state, soldiers=soldiers)
    state.brigands = 50
    state.brigands_strength = 1.2

    vict, loss, gain = state.do_fight("crime")
    assert vict

    ally_loss, enemy_loss = State_Data._get_battle_losses(2)  # type: ignore
    assert loss == soldiers * ally_loss
    assert gain == approx(50 * enemy_loss)

    assert state.government.soldiers == soldiers * (1 - ally_loss)
    assert state.brigands == 50 * (1 - enemy_loss)


def test_do_fight_conquest_defeat():
    state = State_Data()
    soldiers = Soldiers({
        Soldier.knights: 30 / KNIGHT_FIGHTING_STRENGTH,
        Soldier.footmen: 30
    })
    state.government = Government(state, Resources(100), soldiers=soldiers)

    vict, loss, gain = state.do_fight("conquest", 120)
    assert vict is False

    ally_loss, enemy_loss = State_Data._get_battle_losses(0.5)  # type: ignore
    assert loss == soldiers * ally_loss
    assert gain == 0

    assert state.government.soldiers == soldiers * (1 - ally_loss)
    assert state.government.resources == Resources(100)


def test_do_fight_conquest_victory():
    state = State_Data()
    soldiers = Soldiers({
        Soldier.knights: 60 / KNIGHT_FIGHTING_STRENGTH,
        Soldier.footmen: 60
    })
    state.government = Government(state, Resources(100), soldiers=soldiers)

    vict, loss, gain = state.do_fight("conquest", 60)
    assert vict

    ally_loss, enemy_loss = State_Data._get_battle_losses(2)  # type: ignore
    assert loss == soldiers * ally_loss
    assert gain == enemy_loss * PLUNDER_FACTOR

    assert state.government.soldiers == soldiers * (1 - ally_loss)
    assert state.government.resources == Resources(100) + {Resource.land: gain}


def test_do_fight_plunder_defeat():
    state = State_Data()
    soldiers = Soldiers({
        Soldier.knights: 30 / KNIGHT_FIGHTING_STRENGTH,
        Soldier.footmen: 30
    })
    state.government = Government(state, Resources(100), soldiers=soldiers)

    vict, loss, gain = state.do_fight("plunder", 120)
    assert vict is False

    ally_loss, enemy_loss = State_Data._get_battle_losses(0.5)  # type: ignore
    assert loss == soldiers * ally_loss
    assert gain == enemy_loss * PLUNDER_FACTOR

    gains = Resources(enemy_loss * PLUNDER_FACTOR)
    del gains.land

    assert state.government.soldiers == soldiers * (1 - ally_loss)
    assert state.government.resources == Resources(100) + gains


def test_do_fight_plunder_victory():
    state = State_Data()
    soldiers = Soldiers({
        Soldier.knights: 60 / KNIGHT_FIGHTING_STRENGTH,
        Soldier.footmen: 60
    })
    state.government = Government(state, Resources(100), soldiers=soldiers)

    vict, loss, gain = state.do_fight("plunder", 60)
    assert vict

    ally_loss, enemy_loss = State_Data._get_battle_losses(2)  # type: ignore
    assert loss == soldiers * ally_loss
    assert gain == enemy_loss * PLUNDER_FACTOR

    gains = Resources(enemy_loss * PLUNDER_FACTOR)
    del gains.land

    assert state.government.soldiers == soldiers * (1 - ally_loss)
    assert state.government.resources == Resources(100) + gains


def test_execute_commands():
    did_month = 0
    transfers: list[Any] = []
    secures: list[Any] = []
    optimals: list[Any] = []
    setlaws: list[Any] = []
    forcepromos: list[Any] = []
    recruits: list[Any] = []
    fights: list[Any] = []

    def fake_do_month(self: State_Data):
        nonlocal did_month
        did_month += 1

    def fake_transfer(self: State_Data, *args: Any) -> None:
        transfers.append(args)

    def fake_secure(self: State_Data, *args: Any) -> None:
        secures.append(args)

    def fake_optimal(self: State_Data, *args: Any) -> None:
        optimals.append(args)

    def fake_set_law(self: State_Data, *args: Any) -> None:
        setlaws.append(args)

    def fake_force_promotion(self: State_Data, *args: Any) -> None:
        forcepromos.append(args)

    def fake_recruit(self: State_Data, *args: Any) -> None:
        recruits.append(args)

    def fake_fight(self: State_Data, *args: Any) -> None:
        fights.append(args)

    with replace(State_Data, "do_month", fake_do_month), \
         replace(State_Data, "do_transfer", fake_transfer), \
         replace(State_Data, "do_secure", fake_secure), \
         replace(State_Data, "do_optimal", fake_optimal), \
         replace(State_Data, "do_set_law", fake_set_law), \
         replace(State_Data, "do_force_promotion", fake_force_promotion), \
         replace(State_Data, "do_recruit", fake_recruit), \
         replace(State_Data, "do_fight", fake_fight):
        state = State_Data()

        state.execute_commands(["next 2"])
        assert did_month == 2
        assert transfers == []
        assert secures == []
        assert optimals == []
        assert setlaws == []
        assert forcepromos == []
        assert recruits == []
        assert fights == []

        state.execute_commands(["next 100", "transfer nobles food 100",
                                "fight conquer 123"])
        assert did_month == 102
        assert transfers == [
            (Class_Name.nobles, Resource.food, 100)
        ]
        assert secures == []
        assert optimals == []
        assert setlaws == []
        assert forcepromos == []
        assert recruits == []
        assert fights == [
            ("conquer", 123)
        ]

        state.execute_commands(["next 1", "next 1", "next 2",
                                "secure food 200",
                                "laws set tax_property nobles 0.4",
                                "promote artisans 50"])
        assert did_month == 106
        assert transfers == [
            (Class_Name.nobles, Resource.food, 100)
        ]
        assert secures == [
            (Resource.food, 200)
        ]
        assert optimals == []
        assert setlaws == [
            ("tax_property", "nobles", 0.4)
        ]
        assert forcepromos == [
            (Class_Name.artisans, 50)
        ]
        assert recruits == []
        assert fights == [
            ("conquer", 123)
        ]

        state.execute_commands(["transfer nobles food -100",
                                "transfer artisans land 50",
                                "secure tools 340",
                                "optimal wood 1000",
                                "fight crime None",
                                "recruit artisans 30"])
        assert did_month == 106
        assert transfers == [
            (Class_Name.nobles, Resource.food, 100),
            (Class_Name.nobles, Resource.food, -100),
            (Class_Name.artisans, Resource.land, 50)
        ]
        assert secures == [
            (Resource.food, 200),
            (Resource.tools, 340)
        ]
        assert optimals == [
            (Resource.wood, 1000)
        ]
        assert setlaws == [
            ("tax_property", "nobles", 0.4)
        ]
        assert forcepromos == [
            (Class_Name.artisans, 50)
        ]
        assert recruits == [
            (Class_Name.artisans, 30)
        ]
        assert fights == [
            ("conquer", 123),
            ("crime", None)
        ]

        state.execute_commands(["optimal iron 0",
                                "promote nobles 10",
                                "laws set wage_minimum None 0",
                                "laws set tax_income peasants 0.9",
                                "promote peasants 34",
                                "recruit nobles 2"])
        assert did_month == 106
        assert transfers == [
            (Class_Name.nobles, Resource.food, 100),
            (Class_Name.nobles, Resource.food, -100),
            (Class_Name.artisans, Resource.land, 50)
        ]
        assert secures == [
            (Resource.food, 200),
            (Resource.tools, 340)
        ]
        assert optimals == [
            (Resource.wood, 1000),
            (Resource.iron, 0)
        ]
        assert setlaws == [
            ("tax_property", "nobles", 0.4),
            ("wage_minimum", None, 0.0),
            ("tax_income", "peasants", 0.9)
        ]
        assert forcepromos == [
            (Class_Name.artisans, 50),
            (Class_Name.nobles, 10),
            (Class_Name.peasants, 34)
        ]
        assert recruits == [
            (Class_Name.artisans, 30),
            (Class_Name.nobles, 2)
        ]
        assert fights == [
            ("conquer", 123),
            ("crime", None)
        ]
