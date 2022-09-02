from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol, Sequence

from ..auxiliaries.constants import DEFAULT_PRICES
from ..auxiliaries.resources import Resources

if TYPE_CHECKING:
    from .state_data import State_Data


class SupportsTrade(Protocol):
    resources: Resources
    market_res: Resources
    money: float

    @property
    @abstractmethod
    def optimal_resources(self) -> Resources:
        """
        Should return optimal resources for the given object, for trade
        purposes.
        """


class Market:
    """
    Handles trading between social classes.
    Attributes:
    classes - objects between which trade is done
    prices - prices of resources in the last done trade
    """
    def __init__(self, classes: Sequence[SupportsTrade], parent: State_Data):
        self.classes: list[SupportsTrade] = list(classes)
        self.parent: State_Data = parent

    def _get_available_and_needed_resources(self):
        """
        Calculates how much resources are available and needed.
        """
        self.needed_resources: Resources = Resources()
        self.available_resources: Resources = Resources()
        for social_class in self.classes:
            self.needed_resources += social_class.optimal_resources
            self.available_resources += social_class.resources
        if not hasattr(self, "old_avail_res"):
            self.old_avail_res: Resources = self.available_resources.copy()

    def _set_prices(self):
        """
        Calculates the prices of the resources.
        """
        # If one of the available res is 0, arithmetic dict will make the
        # resulting price be float positive infinity
        self._full_prices = self.needed_resources / self.available_resources
        self._full_prices *= DEFAULT_PRICES
        for resource in self._full_prices:
            if self._full_prices[resource] == 0.0:
                self._full_prices[resource] = DEFAULT_PRICES[resource]

        self.prices = self._full_prices.copy()
        # Obtain the differential price:
        # diff_price = -d(ava_res), (-inf, inf)
        diff_prices = self.old_avail_res - self.available_resources
        # diff_price = e^(-d(ava_res)), (0, inf)
        # when price hasn't changed in last month, diff_price = 1
        diff_prices = diff_prices.exp()
        diff_prices *= DEFAULT_PRICES

        # real_prices = avg of prices and diff_prices
        DERIVATION = 0.5  # 0.5 means arithmetic mean
        self.prices = self.prices * (1 - DERIVATION) + diff_prices * DERIVATION

        for resource in self.prices:
            if self.prices[resource] > self.parent.sm.max_prices[resource]:
                self.prices[resource] = self.parent.sm.max_prices[resource]

    def _buy_needed_resources(self):
        """
        Executes the classes purchasing resources they need.
        """
        for social_class in self.classes:
            try:
                # social_class doesn't have to have population attribute
                if social_class.population == 0:  # type: ignore
                    continue
            except AttributeError:
                pass

            corrected_optimal_resources = Resources()
            rel_prices = self._full_prices / DEFAULT_PRICES
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
                social_class.market_res = Resources()

    def _buy_other_resources(self):
        """
        Executes the classes purchasing all remaining resources.
        """
        total_price = sum((self.available_resources * self.prices).values())
        if total_price > 0:
            for social_class in self.classes:
                try:
                    # social_class doesn't have to have population attribute
                    if social_class.population == 0:  # type: ignore
                        continue
                except AttributeError:
                    pass

                part_bought = social_class.money / total_price
                social_class.market_res += \
                    self.available_resources * part_bought
                social_class.money = 0
        else:
            classes_count = 0
            for social_class in self.classes:
                try:
                    # social_class doesn't have to have population attribute
                    if social_class.population == 0:  # type: ignore
                        continue
                except AttributeError:
                    pass
                classes_count += 1
            for social_class in self.classes:
                try:
                    # social_class doesn't have to have population attribute
                    if social_class.population == 0:  # type: ignore
                        continue
                except AttributeError:
                    pass
                social_class.market_res += \
                    self.available_resources / classes_count
        self.available_resources = Resources()

    def _delete_trade_attributes(self):
        """
        Finalizes trade and deletes attributes used during trade calculations.
        """
        for social_class in self.classes:
            try:
                # social_class doesn't have to have population attribute
                if social_class.population == 0:  # type: ignore
                    continue
            except AttributeError:
                pass
            del social_class.money
            social_class.resources = social_class.market_res
            del social_class.market_res

        self.old_avail_res = self.available_resources.copy()
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
