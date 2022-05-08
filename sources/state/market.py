from ..auxiliaries.arithmetic_dict import Arithmetic_Dict
from ..auxiliaries.constants import DEFAULT_PRICES, EMPTY_RESOURCES
from .social_classes.class_file import Class


class Market:
    """
    Handles trading between social classes.
    Attributes:
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
        self.needed_resources = EMPTY_RESOURCES.copy()
        self.available_resources = EMPTY_RESOURCES.copy()
        for social_class in self.classes:
            self.needed_resources += social_class.optimal_resources
            self.available_resources += social_class.resources

    def _set_prices(self):
        """
        Calculates the prices of the resources.
        """
        # If one of the available res is 0, arithmetic dict will make the
        # resulting price be float positive infinity
        self.prices = self.needed_resources / self.available_resources
        self.prices *= DEFAULT_PRICES
        for resource in self.prices:
            if self.prices[resource] == 0.0:
                self.prices[resource] = DEFAULT_PRICES[resource]

    def _buy_needed_resources(self):
        """
        Executes the classes purchasing resources they need.
        """
        for social_class in self.classes:
            if social_class.population > 0:
                corrected_optimal_resources = Arithmetic_Dict({})
                rel_prices = self.prices / DEFAULT_PRICES
                price_adjusted = {
                    resource: amount / (rel_prices[resource]
                                        if rel_prices[resource] > 0.1
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
                if needed_money > 0:
                    part_bought = min(social_class.money / needed_money, 1)
                    money_spent = min(social_class.money, needed_money)
                    social_class.money -= money_spent

                    social_class.market_res = \
                        corrected_optimal_resources * part_bought
                    self.available_resources -= social_class.market_res
                else:
                    social_class.market_res = EMPTY_RESOURCES.copy()

    def _buy_other_resources(self):
        """
        Executes the classes purchasing all remaining resources.
        """
        total_price = sum((self.available_resources * self.prices).values())
        if total_price > 0:
            for social_class in self.classes:
                if social_class.population > 0:
                    part_bought = social_class.money / total_price
                    social_class.market_res += \
                        self.available_resources * part_bought
                    social_class.money = 0
        else:
            classes_count = 0
            for social_class in self.classes:
                if social_class.population > 0:
                    classes_count += 1
            for social_class in self.classes:
                if social_class.population > 0:
                    social_class.market_res += \
                        self.available_resources / classes_count
        self.available_resources = EMPTY_RESOURCES.copy()

    def _delete_trade_attributes(self):
        """
        Finalizes trade and deletes attributes used during trade calculations.
        """
        for social_class in self.classes:
            if social_class.population > 0:
                del social_class.money
                social_class.new_resources = social_class.market_res
                social_class.flush()
                del social_class.market_res

        del self.available_resources
        del self.needed_resources

    def do_trade(self):
        """
        Executes trade between the classes.
        WARNING: Flushes all the classes.
        """
        for social_class in self.classes:
            social_class.flush()
        self._get_available_and_needed_resources()
        self._set_prices()
        self._buy_needed_resources()
        self._buy_other_resources()
        self._delete_trade_attributes()
