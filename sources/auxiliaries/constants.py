from math import inf

from .arithmetic_dict import Arithmetic_Dict
from .resources import Resources
from .enums import Month, Class_Name, Resource, Soldier


# NAME CONSTANTS
MODIFIERS = [
    'Base', 'Starving', 'Freezing', 'Mobility'
]

# CONSUMPTION CONSTANTS
FOOD_CONSUMPTION = 1
WOOD_CONSUMPTION = {
    # Per person, per month.
    Month.January: 0.6,
    Month.February: 0.6,
    Month.March: 0.3,
    Month.April: 0.0,
    Month.May: 0.0,
    Month.June: 0.0,
    Month.July: 0.0,
    Month.August: 0.0,
    Month.September: 0.0,
    Month.October: 0.0,
    Month.November: 0.3,
    Month.December: 0.6
}

# PRODUCTION CONSTANTS
MINER_TOOL_USAGE = 0.3
IRON_PRODUCTION = 1.0
STONE_PRODUCTION = 1.0
OTHERS_MINIMUM_WAGE = 0.5
WAGE_CHANGE = 0.05

ARTISAN_WOOD_USAGE = 0.2
ARTISAN_IRON_USAGE = 0.5
ARTISAN_TOOL_USAGE = 0.2
TOOLS_PRODUCTION = 0.9

WORKER_LAND_USAGE = 20.0

PEASANT_TOOL_USAGE = 0.1
FOOD_RATIOS = Arithmetic_Dict({
    Month.January: 0,
    Month.February: 0,
    Month.March: 0.5,
    Month.April: 1,
    Month.May: 1,
    Month.June: 0.5,
    Month.July: 1.5,
    Month.August: 5,
    Month.September: 2,
    Month.October: 1,
    Month.November: 0,
    Month.December: 0
})
AVG_FOOD_PRODUCTION = 2.2
FOOD_PRODUCTION = FOOD_RATIOS * AVG_FOOD_PRODUCTION
WOOD_PRODUCTION = 1.4

# PROMOTIONS CONSTANTS
INCREASE_PRICE_FACTOR = 5.0
NOBLES_CAP = 1.0  # max ratio of nobles to employees

# POPULATION CONSTANTS
DEFAULT_GROWTH_FACTOR = 0.1  # monthly is 1/12 of that
STARVATION_MORTALITY = 0.2
FREEZING_MORTALITY = 0.2

# RESOURCES CONSTANTS
INBUILT_RESOURCES = {
    Class_Name.nobles: Resources({
        Resource.wood: 7,
        Resource.stone: 4,
        Resource.tools: 5,
        Resource.land: 60
    }),
    Class_Name.artisans: Resources({
        Resource.wood: 2,
        Resource.iron: 1,
        Resource.tools: 3,
    }),
    Class_Name.peasants: Resources({
        Resource.wood: 3,
        Resource.tools: 3,
        Resource.land: 20
    }),
    Class_Name.others: Resources()
}

# TRADE CONSTANTS
DEFAULT_PRICES = Resources({
    Resource.food: 1.0,
    Resource.wood: 1.5,
    Resource.stone: 2.5,
    Resource.iron: 2.5,
    Resource.tools: 3.5,
    Resource.land: 10.0
})

MAX_PRICES = Resources(inf)

TAX_RATES = {
    "property": Arithmetic_Dict({
        Class_Name.nobles: 0.0,
        Class_Name.artisans: 0.0,
        Class_Name.peasants: 0.0,
        Class_Name.others: 0.0
    }),
    "income": Arithmetic_Dict({
        Class_Name.nobles: 0.0,
        Class_Name.artisans: 0.0,
        Class_Name.peasants: 0.0,
        Class_Name.others: 0.0
    }),
    "personal": Arithmetic_Dict({
        Class_Name.nobles: 0.0,
        Class_Name.artisans: 0.0,
        Class_Name.peasants: 0.0,
        Class_Name.others: 0.0
    })
}

# MILITARY CONSTANTS
REBELLION_THRESHOLD = -100

CLASS_TO_SOLDIER = {
    Class_Name.nobles: Soldier.knights,
    Class_Name.artisans: Soldier.footmen,
    Class_Name.peasants: Soldier.footmen,
    Class_Name.others: Soldier.footmen
}
RECRUITMENT_COST = {
    Soldier.knights: Resources({
        Resource.wood: 1,
        Resource.iron: 2,
        Resource.tools: 6
    }),
    Soldier.footmen: Resources({
        Resource.tools: 2
    })
}
BRIGAND_STRENGTH_CLASS = {
    Class_Name.nobles: 1.0,
    Class_Name.artisans: 0.8,
    Class_Name.peasants: 0.8,
    Class_Name.others: 0.7
}
BRIGAND_STRENGTH_SOLDIER = {
    Soldier.knights: 2.0,
    Soldier.footmen: 1.0
}

KNIGHT_FOOD_CONSUMPTION = 2.5
KNIGHT_FIGHTING_STRENGTH = 3.0
BASE_BATTLE_LOSSES = 0.2

PLUNDER_FACTOR = 500

GOVT_LEFT_LABELS = [
    "Tradeable resources:",
    "Secure resources:",
    "Optimal resources:"
]

HAPPINESS_DECAY = 0.2

RECRUITABLE_PART = 0.2
