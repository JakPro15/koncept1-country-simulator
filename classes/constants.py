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
    # IF MODIFYING, MODIFY ALSO PEASANT_FOOD_NEEDED
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
WOOD_PRODUCTION = 1
IRON_PRODUCTION = 1
STONE_PRODUCTION = 1
TOOLS_PRODUCTION = 1


PEASANT_FOOD_NEEDED = {
    'January': 1,
    'August': 2,
    'September': 4,
    'October': 4,
    'November': 3,
    'December': 2,
}


PEASANT_TOOL_USAGE = {
    # Per fully working peasant or serf-peasant (20 ha of land), per month.
    'January': 0,
    'February': 0,
    'March': 0.1,
    'April': 0.2,
    'May': 0.15,
    'June': 0.1,
    'July': 0.25,
    'August': 0.6,
    'September': 0.3,
    'October': 0.1,
    'November': 0,
    'December': 0
}
ARTISAN_TOOL_USAGE = 0.15
ARTISAN_WOOD_USAGE = 0.2
ARTISAN_IRON_USAGE = 0.5
