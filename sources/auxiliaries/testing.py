from pytest import approx


def dict_eq(dict1: dict, dict2: dict):
    for key in dict1 | dict2:
        assert dict1.get(key, 0) == approx(dict2.get(key, 0))


class replace:
    def __init__(self, class_, func_name, new_func):
        self.class_ = class_
        self.func_name = func_name
        self.new_func = new_func

    def __enter__(self):
        self.old_func = getattr(self.class_, self.func_name)
        setattr(self.class_, self.func_name, self.new_func)

    def __exit__(self, class_, func_name, new_func):
        setattr(self.class_, self.func_name, self.old_func)
