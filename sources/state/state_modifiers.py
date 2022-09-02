from copy import deepcopy
from typing import TYPE_CHECKING

from ..auxiliaries.enums import Class_Name, Resource

from ..auxiliaries.constants import (ARTISAN_IRON_USAGE, ARTISAN_TOOL_USAGE,
                                     ARTISAN_WOOD_USAGE, AVG_FOOD_PRODUCTION,
                                     DEFAULT_GROWTH_FACTOR, DEFAULT_PRICES,
                                     FOOD_CONSUMPTION, FOOD_RATIOS,
                                     FREEZING_MORTALITY, INBUILT_RESOURCES,
                                     INCREASE_PRICE_FACTOR, IRON_PRODUCTION,
                                     MAX_PRICES, MINER_TOOL_USAGE, NOBLES_CAP,
                                     OTHERS_MINIMUM_WAGE, PEASANT_TOOL_USAGE,
                                     STARVATION_MORTALITY, STONE_PRODUCTION,
                                     TAX_RATES, TOOLS_PRODUCTION,
                                     WOOD_CONSUMPTION, WOOD_PRODUCTION,
                                     WORKER_LAND_USAGE)
from ..auxiliaries.enums import Month
from ..auxiliaries.resources import Resources

if TYPE_CHECKING:
    from .state_data import State_Data


class State_Modifiers:
    """
    Stores the modifiers defining how the State works. Can be changed
    mid-game by the player's actions.
    They start out as constants from auxiliaries/constants.py.
    """
    def __init__(self, parent: State_Data) -> None:
        self.parent: State_Data = parent

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
    def food_production(self) -> dict[Month, float]:
        return FOOD_RATIOS * self.avg_food_production

    @property
    def optimal_resources(self) -> dict[Class_Name, Resources]:
        return {
            Class_Name.nobles: Resources({
                Resource.food: 12 * FOOD_CONSUMPTION,
                Resource.wood: sum(WOOD_CONSUMPTION.values()),
                Resource.stone: 2 * INBUILT_RESOURCES[Class_Name.nobles].stone,
                Resource.iron: 0,
                Resource.tools:
                (4 * self.parent.get_available_employees() /
                 self.parent.classes[Class_Name.nobles].population) + 4
                if self.parent.classes[Class_Name.nobles].population > 0
                else 4,
                Resource.land:
                (self.worker_land_usage *
                 self.parent.get_available_employees() /
                 self.parent.classes[Class_Name.nobles].population)
                if self.parent.classes[Class_Name.nobles].population > 0
                else 0,
            }),
            Class_Name.artisans: Resources({
                Resource.food: 4 * FOOD_CONSUMPTION,
                Resource.wood: (sum(WOOD_CONSUMPTION.values()) / 3 +
                                4 * self.artisan_wood_usage),
                Resource.stone: 0,
                Resource.iron: 20 * self.artisan_iron_usage,
                Resource.tools: 4 * self.artisan_tool_usage,
                Resource.land: 0
            }),
            Class_Name.peasants: Resources({
                Resource.food: 4 * FOOD_CONSUMPTION,
                Resource.wood: sum(WOOD_CONSUMPTION.values()) / 3,
                Resource.stone: 0,
                Resource.iron: 0,
                Resource.tools: 4 * self.peasant_tool_usage,
                Resource.land: 0.5 * self.worker_land_usage
            }),
            Class_Name.others: Resources({
                Resource.food: 4 * FOOD_CONSUMPTION,
                Resource.wood: sum(WOOD_CONSUMPTION.values()) / 3,
                Resource.stone: 0,
                Resource.iron: 0,
                Resource.tools: 0,
                Resource.land: 0
            }),
        }
