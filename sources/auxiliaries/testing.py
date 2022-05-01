from pytest import approx


def dict_eq(dict1: dict, dict2: dict):
    for key in dict1 | dict2:
        assert dict1.get(key, 0) == approx(dict2.get(key, 0))
