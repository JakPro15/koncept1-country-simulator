from .arithmetic_dict import Arithmetic_Dict


# NAME CONSTANTS
RESOURCES = [
    "food", "wood", "stone", "iron", "tools"
]
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
ARTISAN_TOOL_USAGE = 0.1
TOOLS_PRODUCTION = 1.2

PEASANT_TOOL_USAGE = 0.1
FOOD_PRODUCTION = {
    'January': 0, 'February': 0, 'March': 2,
    'April': 3, 'May': 3, 'June': 2.5, 'July': 4, 'August': 8.5,
    'September': 4.5, 'October': 2.5, 'November': 0, 'December': 0
}
WOOD_PRODUCTION = 1.5

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
        "tools": 1
    }),
    "artisans": Arithmetic_Dict({
        "food": 0,
        "wood": 2,
        "stone": 0,
        "iron": 1,
        "tools": 3
    }),
    "peasants": Arithmetic_Dict({
        "food": 0,
        "wood": 3,
        "stone": 0,
        "iron": 0,
        "tools": 3
    }),
    "others": Arithmetic_Dict({
        "food": 0,
        "wood": 0,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }),
}

# TRADE CONSTANTS
OPTIMAL_RESOURCES = {
    "nobles": Arithmetic_Dict({
        "food": 12 * FOOD_CONSUMPTION,
        "wood": sum(WOOD_CONSUMPTION.values()),
        "stone": 2 * INBUILT_RESOURCES["nobles"]["stone"],
        "iron": 0,
        "tools": 4  # Possibly more, depending on number of employees
    }),
    "artisans": Arithmetic_Dict({
        "food": 4 * FOOD_CONSUMPTION,
        "wood": sum(WOOD_CONSUMPTION.values()) / 3 + 4 * ARTISAN_WOOD_USAGE,
        "stone": 0,
        "iron": 4 * ARTISAN_IRON_USAGE,
        "tools": 4 * ARTISAN_TOOL_USAGE
    }),
    "peasants": Arithmetic_Dict({
        "food": 4 * FOOD_CONSUMPTION,
        "wood": sum(WOOD_CONSUMPTION.values()) / 3,
        "stone": 0,
        "iron": 0,
        "tools": 4 * PEASANT_TOOL_USAGE
    }),
    "others": Arithmetic_Dict({
        "food": 4 * FOOD_CONSUMPTION,
        "wood": sum(WOOD_CONSUMPTION.values()) / 3,
        "stone": 0,
        "iron": 0,
        "tools": 0
    }),
}
DEFAULT_PRICES = Arithmetic_Dict({
    "food": 1,
    "wood": 1.5,
    "stone": 2.5,
    "iron": 2.5,
    "tools": 3.5
})
