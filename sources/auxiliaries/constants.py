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
    'Base', 'Starving', 'Freezing', 'Mobility'
]
CLASSES = [
    "nobles", "artisans", "peasants", "others"
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
    'March': 2,
    'April': 3,
    'May': 3,
    'June': 2.5,
    'July': 4,
    'August': 8.5,
    'September': 4.5,
    'October': 2.5,
    'November': 0,
    'December': 0
}
WOOD_PRODUCTION = 1.5
IRON_PRODUCTION = 1
STONE_PRODUCTION = 1
TOOLS_PRODUCTION = 1.2

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
    "wood": 1.5,
    "stone": 2.5,
    "iron": 2.5,
    "tools": 3.5
})

OTHERS_WAGE = 0.5
