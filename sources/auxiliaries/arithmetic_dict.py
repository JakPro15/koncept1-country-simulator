from math import inf, isnan, exp, isinf


class Arithmetic_Dict(dict):
    def __add__(self, other: "Arithmetic_Dict"):
        result = Arithmetic_Dict(self.copy())
        for key in self | other:
            result[key] = self.get(key, 0) + other.get(key, 0)
        return result

    def __IADD__(self, other: "Arithmetic_Dict"):
        for key in self | other:
            self[key] = self.get(key, 0) + other.get(key, 0)

    def __sub__(self, other: "Arithmetic_Dict"):
        result = Arithmetic_Dict(self.copy())
        for key in self | other:
            result[key] = self.get(key, 0) - other.get(key, 0)
        return result

    def __ISUB__(self, other: "Arithmetic_Dict"):
        for key in self | other:
            self[key] = self.get(key, 0) - other.get(key, 0)

    def __mul__(self, factor):
        result = Arithmetic_Dict(self.copy())
        if isinstance(factor, Arithmetic_Dict) or isinstance(factor, dict):
            for key in self | factor:
                result[key] = self.get(key, 0) * factor.get(key, 0)
                if isnan(result[key]):
                    result[key] = 0
        else:
            for key in result:
                result[key] = self.get(key, 0) * factor
                if isnan(result[key]):
                    result[key] = 0
        return result

    def __IMUL__(self, factor):
        if isinstance(factor, Arithmetic_Dict) or isinstance(factor, dict):
            for key in self | factor:
                self[key] = self.get(key, 0) * factor.get(key, 0)
                if isnan(self.get(key, 0)):
                    self[key] = 0
        else:
            for key in self:
                self[key] = self.get(key, 0) * factor
                if isnan(self.get(key, 0)):
                    self[key] = 0
        return self

    def __truediv__(self, factor):
        result = Arithmetic_Dict(self.copy())
        if isinstance(factor, Arithmetic_Dict) or isinstance(factor, dict):
            for key in self | factor:
                try:
                    result[key] = self.get(key, 0) / factor.get(key, 0)
                except ZeroDivisionError:
                    if self.get(key, 0) == 0:
                        result[key] = 0
                    else:
                        result[key] = inf
        else:
            for key in result:
                try:
                    result[key] = self.get(key, 0) / factor
                except ZeroDivisionError:
                    if self.get(key, 0) == 0:
                        result[key] = 0
                    else:
                        result[key] = inf
        return result

    def __IDIV__(self, factor):
        if isinstance(factor, Arithmetic_Dict) or isinstance(factor, dict):
            for key in self | factor:
                try:
                    self[key] = self.get(key, 0) / factor.get(key, 0)
                except ZeroDivisionError:
                    if self.get(key, 0) != 0:
                        self[key] = inf
        else:
            for key in self:
                try:
                    self[key] = self.get(key, 0) / factor
                except ZeroDivisionError:
                    if self.get(key, 0) != 0:
                        self[key] = inf
        return self

    def __floordiv__(self, factor):
        result = Arithmetic_Dict(self.copy())
        if isinstance(factor, Arithmetic_Dict) or isinstance(factor, dict):
            for key in self | factor:
                try:
                    result[key] = self.get(key, 0) // factor.get(key, 0)
                except ZeroDivisionError:
                    if self.get(key, 0) == 0:
                        result[key] = 0
                    else:
                        result[key] = inf
        else:
            for key in result:
                try:
                    result[key] = self.get(key, 0) // factor
                except ZeroDivisionError:
                    if self.get(key, 0) == 0:
                        result[key] = 0
                    else:
                        result[key] = inf
        return result

    def __IFLOORDIV__(self, factor):
        if isinstance(factor, Arithmetic_Dict) or isinstance(factor, dict):
            for key in self | factor:
                try:
                    self[key] = self.get(key, 0) // factor.get(key, 0)
                except ZeroDivisionError:
                    if self.get(key, 0) != 0:
                        self[key] = inf
        else:
            for key in self:
                try:
                    self[key] = self.get(key, 0) // factor
                except ZeroDivisionError:
                    if self.get(key, 0) != 0:
                        self[key] = inf
        return self

    def __lt__(self, other):
        if isinstance(other, Arithmetic_Dict) or isinstance(other, dict):
            for key in self | other:
                if self.get(key, 0) < other.get(key, 0):
                    return True
        else:
            for key in self:
                if self.get(key, 0) < other:
                    return True
        return False

    def copy(self):
        return Arithmetic_Dict(super().copy())

    def exp(self):
        return Arithmetic_Dict(
            {element: exp(value) for element, value in self.items()}
        )

    def __round__(self, ndigits=0):
        result = self.copy()
        for key in result:
            result[key] = round(result[key], ndigits)
            if ndigits <= 0 and not (isnan(result[key]) or isinf(result[key])):
                result[key] = int(result[key])
        return result
