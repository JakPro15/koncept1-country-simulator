from .arithmetic_dict import Arithmetic_Dict


RESOURCES = [
    "food", "wood", "stone", "iron", "tools"
]
LAND_TYPES = [
    "fields", "woods", "stone_mines", "iron_mines"
]
MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]
MODIFIERS = [
    'Base', 'Starving', 'Freezing'
]
CLASSES = [
    "Nobles", "Artisans", "Peasants", "Others"
]

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

FOOD_PRODUCTION = {
    # Per fully working peasant or employee (20 ha of land), per month.
    'January': 0,
    'February': 0,
    'March': 1,
    'April': 2,
    'May': 1.5,
    'June': 1,
    'July': 2.5,
    'August': 6,
    'September': 3,
    'October': 1,
    'November': 0,
    'December': 0
}
WOOD_PRODUCTION = 1.2
IRON_PRODUCTION = 1
STONE_PRODUCTION = 1
TOOLS_PRODUCTION = 1

PEASANT_TOOL_USAGE = {
    # Per fully working peasant or serf-peasant (20 ha of land), per month.
    'January': 0,
    'February': 0,
    'March': 0.1,
    'April': 0.1,
    'May': 0.1,
    'June': 0.1,
    'July': 0.1,
    'August': 0.4,
    'September': 0.2,
    'October': 0.1,
    'November': 0,
    'December': 0
}
ARTISAN_TOOL_USAGE = 0.1
MINER_TOOL_USAGE = 0.3
ARTISAN_WOOD_USAGE = 0.2
ARTISAN_IRON_USAGE = 0.5

DEFAULT_GROWTH_FACTOR = 0.1  # monthly is 1/12 of that
STARVATION_MORTALITY = 0.2
FREEZING_MORTALITY = 0.2

INDEX_TO_CLASS_NAME = {
    0: "nobles",
    1: "artisans",
    2: "peasants",
    3: "others"
}

DEFAULT_PRICES = Arithmetic_Dict({
    "food": 1,
    "wood": 1,
    "stone": 2.044444,
    "iron": 2.044444,
    "tools": 2.722222
})

OTHERS_WAGE = 0.5
