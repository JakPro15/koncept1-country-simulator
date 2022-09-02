from ...auxiliaries.constants import DEFAULT_PRICES, INBUILT_RESOURCES
from ...auxiliaries.enums import Class_Name, Resource
from ...auxiliaries.resources import Resources
from .class_file import Class


class Peasants(Class):
    """
    Represents the Peasants of the country.
    Peasants make food and wood.
    They cannot work as employees.
    They promote to Nobles.
    They demote to Others.
    """
    @property
    def class_name(self) -> Class_Name:
        return Class_Name.peasants

    @property
    def max_employees(self) -> float:
        land_owned = self.resources.land + \
            INBUILT_RESOURCES[self.class_name].land * self.population
        return max(min(
            self.resources.tools / 3,
            land_owned / self.parent.sm.worker_land_usage,
        ) - self.population, 0)

    def produce(self) -> None:
        """
        Adds resources the class produced in the current month.
        """
        month = self.parent.month
        relative_prices = self.parent.prices / DEFAULT_PRICES

        total_price = relative_prices.food + relative_prices.wood
        food_peasants = self.population * relative_prices.food / total_price
        wood_peasants = self.population * relative_prices.wood / total_price

        changes = Resources({
            Resource.food:
                self.parent.sm.food_production[month] * food_peasants,
            Resource.wood: self.parent.sm.wood_production * wood_peasants,
            Resource.tools:
                -self.parent.sm.peasant_tool_usage * self.population
        })

        self.resources += changes
