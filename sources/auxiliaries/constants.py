from math import inf
from .arithmetic_dict import Arithmetic_Dict


DEBUG_MODE = True

# NAME CONSTANTS
RESOURCES = [
    "food", "wood", "stone", "iron", "tools", "land"
]
EMPTY_RESOURCES = Arithmetic_Dict({
    "food": 0,
    "wood": 0,
    "stone": 0,
    "iron": 0,
    "tools": 0,
    "land": 0
})

MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]
MODIFIERS = [
    'Base', 'Starving', 'Freezing', 'Mobility'
]
CLASSES = [
    "nobles", "artisans", "peasants", "others"
]
CLASS_NAME_TO_INDEX = {
    "nobles": 0,
    "artisans": 1,
    "peasants": 2,
    "others": 3
}

# CONSUMPTION CONSTANTS
FOOD_CONSUMPTION = 1
WOOD_CONSUMPTION = {
    # Per person, per month.
    'January': 0.6,
    'February': 0.6,
    'March': 0.3,
    'April': 0,
    'May': 0,
    'June': 0,
    'July': 0,
    'August': 0,
    'September': 0,
    'October': 0,
    'November': 0.3,
    'December': 0.6
}

# PRODUCTION CONSTANTS
MINER_TOOL_USAGE = 0.3
IRON_PRODUCTION = 1
STONE_PRODUCTION = 1
OTHERS_WAGE = 0.5

ARTISAN_WOOD_USAGE = 0.2
ARTISAN_IRON_USAGE = 0.5
ARTISAN_TOOL_USAGE = 0.2
TOOLS_PRODUCTION = 0.9

WORKER_LAND_USAGE = 20

PEASANT_TOOL_USAGE = 0.1
FOOD_RATIOS = Arithmetic_Dict({
    'January': 0, 'February': 0, 'March': 0.5,
    'April': 1, 'May': 1, 'June': 0.5, 'July': 1.5, 'August': 5,
    'September': 2, 'October': 1, 'November': 0, 'December': 0
})
AVG_FOOD_PRODUCTION = 2.2
FOOD_PRODUCTION = FOOD_RATIOS * AVG_FOOD_PRODUCTION
WOOD_PRODUCTION = 1.4

# PROMOTIONS CONSTANTS
INCREASE_PRICE_FACTOR = 5
NOBLES_CAP = 1  # max ratio of nobles to employees

# POPULATION CONSTANTS
DEFAULT_GROWTH_FACTOR = 0.1  # monthly is 1/12 of that
STARVATION_MORTALITY = 0.2
FREEZING_MORTALITY = 0.2

# RESOURCES CONSTANTS
INBUILT_RESOURCES = {
    "nobles": Arithmetic_Dict({
        "food": 0,
        "wood": 7,
        "stone": 4,
        "iron": 0,
        "tools": 5,
        "land": 60
    }),
    "artisans": Arithmetic_Dict({
        "food": 0,
        "wood": 2,
        "stone": 0,
        "iron": 1,
        "tools": 3,
        "land": 0
    }),
    "peasants": Arithmetic_Dict({
        "food": 0,
        "wood": 3,
        "stone": 0,
        "iron": 0,
        "tools": 3,
        "land": 20
    }),
    "others": Arithmetic_Dict({
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0,
        "land": 0
    }),
}

# TRADE CONSTANTS
DEFAULT_PRICES = Arithmetic_Dict({
    "food": 1,
    "wood": 1.5,
    "stone": 2.5,
    "iron": 2.5,
    "tools": 3.5,
    "land": 10
})

MAX_PRICES = inf

TAX_RATES = {
    "property": Arithmetic_Dict({
        "nobles": 0.2,
        "artisans": 0.2,
        "peasants": 0.2,
        "others": 0.2
    }),
    "income": Arithmetic_Dict({
        "nobles": 0.2,
        "artisans": 0.2,
        "peasants": 0.2,
        "others": 0.2
    }),
    "personal": Arithmetic_Dict({
        "nobles": 0.2,
        "artisans": 0.2,
        "peasants": 0.2,
        "others": 0.2
    })
}
