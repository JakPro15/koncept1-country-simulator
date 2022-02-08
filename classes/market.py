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

    @staticmethod
    def operation_on_dict(dict1, dict2, operation):
        """
        Adds/multiplies/divides etc. the values in dict1 and dict2, then
        returns the resulting dict. The 2 dicts need to have (the same keys)
        and (numeric values), resulting dict will also fulfil these conditions.
        """
        result = {}
        for key in dict1:
            result[key] = operation(dict1[key], dict2[key])
        return result

    def _get_available_and_needed_resources(self):
        """
        Calculates how much resources are available and needed.
        """
        self.needed_resources = {
            "food": 0,
            "wood": 0,
            "stone": 0,
            "iron": 0,
            "tools": 0
        }
        self.available_resources = {
            "food": 0,
            "wood": 0,
            "stone": 0,
            "iron": 0,
            "tools": 0
        }
        for social_class in self.classes:
            self.needed_resources = Market.operation_on_dict(
                self.needed_resources,
                social_class.optimal_resources,
                lambda a, b: a + b
            )
            self.available_resources = Market.operation_on_dict(
                self.available_resources,
                social_class.resources,
                lambda a, b: a + b
            )

    def _set_prices(self):
        """
        Calculates the prices of the resources.
        """
        self.prices = Market.operation_on_dict(
            self.needed_resources,
            self.available_resources,
            lambda a, b: a / b
        )

    def _buy_needed_resources(self):
        """
        Executes the classes purchasing resources they need.
        """
        for social_class in self.classes:
            corrected_optimal_resources = Market.operation_on_dict(
                social_class.optimal_resources,
                {
                    resource: amount / (self.prices[resource]
                                        if self.prices[resource] > 0
                                        else 0.1)
                    for resource, amount
                    in social_class.optimal_resources.items()
                },
                lambda a, b: min(a, b)
            )

            social_class.money = sum(Market.operation_on_dict(
                social_class.resources,
                self.prices,
                lambda a, b: a * b
            ).values())
            needed_money = sum(Market.operation_on_dict(
                corrected_optimal_resources,
                self.prices,
                lambda a, b: a * b
            ).values())
            part_bought = min(social_class.money / needed_money, 1)
            money_spent = min(social_class.money, needed_money)
            social_class.money -= money_spent

            social_class.new_resources = {
                resource: amount * part_bought
                for resource, amount
                in corrected_optimal_resources.items()
            }
            self.available_resources = Market.operation_on_dict(
                self.available_resources,
                social_class.new_resources,
                lambda a, b: a - b
            )

    def _buy_other_resources(self):
        """
        Executes the classes purchasing all remaining resources.
        """
        total_price = sum(Market.operation_on_dict(
            self.available_resources,
            self.prices,
            lambda a, b: a * b
        ).values())
        for social_class in self.classes:
            part_bought = social_class.money / total_price
            for resource in social_class.new_resources:
                social_class.new_resources[resource] += \
                    self.available_resources[resource] * part_bought
            social_class.money = 0
        self.available_resources = {
            "food": 0,
            "wood": 0,
            "stone": 0,
            "iron": 0,
            "tools": 0
        }

    def _delete_trade_attributes(self):
        """
        Finalizes trade and deletes attributes used during trade calculations.
        """
        for social_class in self.classes:
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
