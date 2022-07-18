from ..auxiliaries.constants import (
    AVG_FOOD_PRODUCTION,
    FOOD_RATIOS,
    MAX_PRICES,
    MINER_TOOL_USAGE,
    NOBLES_CAP,
    DEFAULT_GROWTH_FACTOR,
    DEFAULT_PRICES,
    FOOD_CONSUMPTION,
    FREEZING_MORTALITY,
    INBUILT_RESOURCES,
    INCREASE_PRICE_FACTOR,
    STARVATION_MORTALITY,
    WOOD_CONSUMPTION,
    IRON_PRODUCTION,
    STONE_PRODUCTION,
    OTHERS_MINIMUM_WAGE,
    ARTISAN_IRON_USAGE,
    ARTISAN_TOOL_USAGE,
    ARTISAN_WOOD_USAGE,
    TOOLS_PRODUCTION,
    PEASANT_TOOL_USAGE,
    WOOD_PRODUCTION,
    WORKER_LAND_USAGE,
    TAX_RATES
)
from ..auxiliaries.arithmetic_dict import Arithmetic_Dict
from copy import deepcopy


class State_Modifiers:
    """
    Stores the modifiers defining how the State works. Can be changed
    mid-game by the player's actions.
    They start out as constants from auxiliaries/constants.py.
    """
    def __init__(self, parent):
        self.parent = parent

        # ALL DICT CONSTANTS HERE MUST BE COPIED, not just assigned
        self.miner_tool_usage = MINER_TOOL_USAGE
        self.iron_production = IRON_PRODUCTION
        self.stone_production = STONE_PRODUCTION
        self.others_minimum_wage = OTHERS_MINIMUM_WAGE

        self.artisan_wood_usage = ARTISAN_WOOD_USAGE
        self.artisan_iron_usage = ARTISAN_IRON_USAGE
        self.artisan_tool_usage = ARTISAN_TOOL_USAGE
        self.tools_production = TOOLS_PRODUCTION

        self.peasant_tool_usage = PEASANT_TOOL_USAGE
        self.avg_food_production = AVG_FOOD_PRODUCTION

        self.wood_production = WOOD_PRODUCTION

        self.increase_price_factor = INCREASE_PRICE_FACTOR
        self.nobles_cap = NOBLES_CAP

        self.default_growth_factor = DEFAULT_GROWTH_FACTOR
        self.starvation_mortality = STARVATION_MORTALITY
        self.freezing_mortality = FREEZING_MORTALITY

        self.max_prices = DEFAULT_PRICES * MAX_PRICES

        self.worker_land_usage = WORKER_LAND_USAGE

        self.tax_rates = deepcopy(TAX_RATES)

    @property
    def food_production(self):
        return FOOD_RATIOS * self.avg_food_production

    @property
    def optimal_resources(self):
        return {
            "nobles": Arithmetic_Dict({
                "food": 12 * FOOD_CONSUMPTION,
                "wood": sum(WOOD_CONSUMPTION.values()),
                "stone": 2 * INBUILT_RESOURCES["nobles"]["stone"],
                "iron": 0,
                "tools": 4 + (4 * self.parent.get_available_employees() /
                              self.parent.classes[0].population)
                if self.parent.classes[0].population > 0 else 4,
                "land": (self.worker_land_usage *
                         self.parent.get_available_employees() /
                         self.parent.classes[0].population)
                if self.parent.classes[0].population > 0 else 0,
            }),
            "artisans": Arithmetic_Dict({
                "food": 4 * FOOD_CONSUMPTION,
                "wood": sum(WOOD_CONSUMPTION.values()) / 3 +
                4 * self.artisan_wood_usage,
                "stone": 0,
                "iron": 20 * self.artisan_iron_usage,
                "tools": 4 * self.artisan_tool_usage,
                "land": 0
            }),
            "peasants": Arithmetic_Dict({
                "food": 4 * FOOD_CONSUMPTION,
                "wood": sum(WOOD_CONSUMPTION.values()) / 3,
                "stone": 0,
                "iron": 0,
                "tools": 4 * self.peasant_tool_usage,
                "land": 0.5 * self.worker_land_usage
            }),
            "others": Arithmetic_Dict({
                "food": 4 * FOOD_CONSUMPTION,
                "wood": sum(WOOD_CONSUMPTION.values()) / 3,
                "stone": 0,
                "iron": 0,
                "tools": 0,
                "land": 0
            }),
        }
