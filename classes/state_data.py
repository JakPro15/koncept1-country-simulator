from .constants import WOOD_CONSUMPTION


class State_Data:
    def __init__(self, starting_month="January"):
        self.month = starting_month

    def _advance_month(self):
        months = list(WOOD_CONSUMPTION.keys())
        months_moved = months[1:] + [months[0]]
        next_months = {
            month1: month2
            for month1, month2
            in zip(months, months_moved)}
        self.month = next_months[self.month]
