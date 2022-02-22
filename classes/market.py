from .arithmetic_dict import Arithmetic_Dict
from .constants import DEFAULT_PRICES
from .class_file import Class


class Market:
    """
    Handles trading between social classes.
    Properties:
    classes - objects between which trade is done
    prices - prices of resources in the last done trade
    """
    def __init__(self, classes: "list[Class]"):
        """
        Instead of Class, can accept any object that has properties:
        resources, optimal_resources
        """
        self.classes = classes.copy()

    def _get_available_and_needed_resources(self):
        """
        Calculates how much resources are available and needed.
        """
        self.needed_resources = Arithmetic_Dict({
            "food": 0,
            "wood": 0,
            "stone": 0,
            "iron": 0,
            "tools": 0
        })
        self.available_resources = Arithmetic_Dict({
            "food": 0,
            "wood": 0,
            "stone": 0,
            "iron": 0,
            "tools": 0
        })
        for social_class in self.classes:
            self.needed_resources += social_class.optimal_resources
            self.available_resources += social_class.resources

    def _set_prices(self):
        """
        Calculates the prices of the resources.
        """
        self.prices = self.needed_resources / self.available_resources
        self.prices *= DEFAULT_PRICES

    def _buy_needed_resources(self):
        """
        Executes the classes purchasing resources they need.
        """
        for social_class in self.classes:
            if social_class.population > 0:
                corrected_optimal_resources = Arithmetic_Dict({})
                price_adjusted = {
                    resource: amount / (self.prices[resource]
                                        if self.prices[resource] > 0
                                        else 0.1)
                    for resource, amount
                    in social_class.optimal_resources.items()
                }
                for key in social_class.optimal_resources:
                    corrected_optimal_resources[key] = min(
                        social_class.optimal_resources[key],
                        price_adjusted[key]
                    )

                social_class.money = sum(
                    (social_class.resources * self.prices).values()
                )
                needed_money = sum(
                    (corrected_optimal_resources * self.prices).values()
                )
                part_bought = min(social_class.money / needed_money, 1)
                money_spent = min(social_class.money, needed_money)
                social_class.money -= money_spent

                social_class.new_resources = \
                    corrected_optimal_resources * part_bought
                self.available_resources -= social_class.new_resources

    def _buy_other_resources(self):
        """
        Executes the classes purchasing all remaining resources.
        """
        total_price = sum((self.available_resources * self.prices).values())
        for social_class in self.classes:
            if social_class.population > 0:
                part_bought = social_class.money / total_price
                social_class.new_resources += \
                    self.available_resources * part_bought
                social_class.money = 0
        self.available_resources = Arithmetic_Dict({
            "food": 0,
            "wood": 0,
            "stone": 0,
            "iron": 0,
            "tools": 0
        })

    def _delete_trade_attributes(self):
        """
        Finalizes trade and deletes attributes used during trade calculations.
        """
        for social_class in self.classes:
            if social_class.population > 0:
                del social_class.money
                social_class.resources = social_class.new_resources
                del social_class.new_resources

        del self.available_resources
        del self.needed_resources

    def do_trade(self):
        """
        Executes trade between the classes.
        """
        self._get_available_and_needed_resources()
        self._set_prices()
        self._buy_needed_resources()
        self._buy_other_resources()
        self._delete_trade_attributes()
