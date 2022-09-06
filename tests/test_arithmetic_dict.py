from math import exp, inf, isinf, isnan, nan
from random import randint
from typing import Callable

from pytest import raises

from ..sources.auxiliaries.arithmetic_dict import Arithmetic_Dict


def get_numbers() -> tuple[list[float],
                           Arithmetic_Dict[str],
                           Arithmetic_Dict[str]]:
    def rand_no_zero() -> int:
        result = 0
        while result == 0:
            result = randint(-10000, 10000)
        return result

    numbers = [randint(-10000, 10000) / rand_no_zero()
               for _ in range(2700)]

    first = Arithmetic_Dict({
        str(i): numbers[i] for i in range(1500)
    })
    second = Arithmetic_Dict({
        str(i): numbers[i + 1000] for i in range(500, 1700)
    })
    return numbers, first, second


def get_result(
    numbers: list[float], operation: Callable[[float, float], float]
) -> dict[str, float]:
    result: dict[str, float] = {}
    for i in range(500):
        result[str(i)] = operation(numbers[i], 0)
    for i in range(500, 1500):
        result[str(i)] = operation(numbers[i], numbers[i + 1000])
    for i in range(1500, 1700):
        result[str(i)] = operation(0, numbers[i + 1000])
    return result


def test_addition():
    numbers, first, second = get_numbers()
    assert first + second == get_result(numbers, lambda x, y: x + y)


def test_addition_assignment():
    numbers, first, second = get_numbers()
    first += second
    assert first == get_result(numbers, lambda x, y: x + y)


def test_subtraction():
    numbers, first, second = get_numbers()
    assert first - second == get_result(numbers, lambda x, y: x - y)


def test_subtraction_assignment():
    numbers, first, second = get_numbers()
    first -= second
    assert first == get_result(numbers, lambda x, y: x - y)


def test_multiplication_dict():
    numbers, first, second = get_numbers()
    assert first * second == get_result(numbers, lambda x, y: x * y)

    third = Arithmetic_Dict({"a": inf, "b": 0})
    fourth = Arithmetic_Dict({"a": 0, "b": -inf})
    assert third * fourth == {"a": 0, "b": 0}


def test_multiplication_dict_assignment():
    numbers, first, second = get_numbers()
    first *= second
    assert first == get_result(numbers, lambda x, y: x * y)

    third = Arithmetic_Dict({"a": inf, "b": 0})
    fourth = Arithmetic_Dict({"a": 0, "b": -inf})
    third *= fourth
    assert third == {"a": 0, "b": 0}


def test_multiplication_float():
    numbers, first, _ = get_numbers()
    assert first * 3.5 == get_result(numbers, lambda x, y: x * 3.5)

    third = Arithmetic_Dict({"a": inf, "b": -inf})
    assert third * 0 == {"a": 0, "b": 0}


def test_multiplication_float_assignment():
    numbers, first, _ = get_numbers()
    first *= -3.5
    assert first == get_result(numbers, lambda x, y: x * -3.5)

    third = Arithmetic_Dict({"a": inf, "b": -inf})
    third *= 0
    assert third == {"a": 0, "b": 0}


def test_division_dict():
    numbers, first, second = get_numbers()
    assert first / second == get_result(
        numbers, lambda x, y: x / y if y != 0 else (inf if x != 0 else 0) * x)

    third = Arithmetic_Dict({"a": inf, "b": inf})
    fourth = Arithmetic_Dict({"a": inf, "b": -inf})
    fifth = third / fourth
    assert isnan(fifth["a"]) and isnan(fifth["b"])


def test_division_dict_assignment():
    numbers, first, second = get_numbers()
    first /= second
    assert first == get_result(
        numbers, lambda x, y: x / y if y != 0 else (inf if x != 0 else 0) * x)

    third = Arithmetic_Dict({"a": inf, "b": inf})
    fourth = Arithmetic_Dict({"a": inf, "b": -inf})
    third /= fourth
    assert isnan(third["a"]) and isnan(third["b"])


def test_division_float():
    numbers, first, _ = get_numbers()
    assert first / -3.5 == get_result(numbers, lambda x, y: x / -3.5)

    third = Arithmetic_Dict({"a": -2, "b": inf, "c": -inf})
    assert third / 0 == {"a": -inf, "b": inf, "c": -inf}


def test_division_float_assignment():
    numbers, first, _ = get_numbers()
    first /= 3.5
    assert first == get_result(numbers, lambda x, y: x / 3.5)

    third = Arithmetic_Dict({"a": -2, "b": inf, "c": -inf})
    third /= 0
    assert third == {"a": -inf, "b": inf, "c": -inf}


def test_floor_division_dict():
    numbers, first, second = get_numbers()
    assert first / second == get_result(
        numbers, lambda x, y: x / y if y != 0
        else (inf if x != 0 else 0) * x)

    third = Arithmetic_Dict({"a": inf, "b": inf})
    fourth = Arithmetic_Dict({"a": inf, "b": -inf})
    fifth = third // fourth
    assert isnan(fifth["a"]) and isnan(fifth["b"])


def test_floor_division_dict_assignment():
    numbers, first, second = get_numbers()
    first //= second
    assert first == get_result(
        numbers, lambda x, y: x // y if y != 0
        else (inf if x != 0 else 0) * x)

    third = Arithmetic_Dict({"a": inf, "b": inf})
    fourth = Arithmetic_Dict({"a": inf, "b": -inf})
    third //= fourth
    assert isnan(third["a"]) and isnan(third["b"])


def test_floor_division_float():
    numbers, first, _ = get_numbers()
    result = first // -3.5
    assert result == get_result(numbers, lambda x, y: x // -3.5)
    assert result is not first

    third = Arithmetic_Dict({"a": -2, "b": inf, "c": -inf})
    result = third // 0
    assert result == {"a": -inf, "b": inf, "c": -inf}
    assert result is not third


def test_floor_division_float_assignment():
    numbers, first, _ = get_numbers()
    first //= 3.5
    assert first == get_result(numbers, lambda x, y: x // 3.5)

    third = Arithmetic_Dict({"a": -2, "b": inf, "c": -inf})
    third //= 0
    assert third == {"a": -inf, "b": inf, "c": -inf}


def test_lesser_than_dict():
    _, first, _ = get_numbers()
    minimum = min(first.values())
    second = Arithmetic_Dict({
        key: minimum - abs(val)
        for key, val in first.items()
    })
    assert not first < second

    third = {
        key: minimum + abs(val)
        for key, val in first.items()
    }
    assert first < third
    assert second < third


def test_lesser_than_float():
    _, first, _ = get_numbers()
    minimum = min(first.values())
    maximum = max(first.values())

    assert not first < minimum
    assert first < minimum + 0.1
    assert first < maximum


def test_equality():
    a = Arithmetic_Dict({
        "a": 234,
        "b": 345,
        "c": 567
    })
    b = a.copy()
    assert a == b
    assert b == a

    c = {
        "a": 234,
        "b": 345,
        "c": 567,
        "d": 0
    }
    assert a == c

    d = {
        "b": 345,
        "c": 567,
        "d": 0
    }
    assert a != d

    assert a != {}


def test_copy():
    _, first, second = get_numbers()
    first_copy = first.copy()
    assert first == first_copy
    assert first is not first_copy

    second_copy = second.copy()
    assert second == second_copy
    assert second is not second_copy


def test_exp():
    _, first, second = get_numbers()
    assert (first / 100).exp() == {
        key: exp(val / 100) for key, val in first.items()
    }
    assert (second / 100).exp() == {
        key: exp(val / 100) for key, val in second.items()
    }


def test_int():
    _, first, second = get_numbers()
    first_int, second_int = first.int(), second.int()
    assert first_int == {
        key: int(val) for key, val in first.items()
    }
    for value in first_int.values():
        assert isinstance(value, int)

    assert second_int == {
        key: int(val) for key, val in second.items()
    }
    for value in second_int.values():
        assert isinstance(value, int)


def test_float():
    _, first, second = get_numbers()
    first_float = first.float()
    assert first_float == first
    for value in first_float.values():
        assert isinstance(value, float)

    second = second.int()
    second_float = second.float()
    assert second_float == second
    for value in second_float.values():
        assert isinstance(value, float)


def test_round_one():
    # ignoring private use warnings
    assert isinf(Arithmetic_Dict._round(inf))  # type: ignore
    assert isinf(Arithmetic_Dict._round(-inf))  # type: ignore
    assert isnan(Arithmetic_Dict._round(nan))  # type: ignore

    numbers, _, _ = get_numbers()
    for num in numbers:
        rounded = Arithmetic_Dict._round(num)  # type: ignore
        assert rounded == round(num)
        assert isinstance(rounded, int)

        rounded = Arithmetic_Dict._round(num, 1)  # type: ignore
        assert rounded == round(num, 1)
        assert isinstance(rounded, float)

        rounded = Arithmetic_Dict._round(num, -1)  # type: ignore
        assert rounded == round(num, -1)
        assert isinstance(rounded, int)


def test_round():
    numbers, first, second = get_numbers()
    assert round(first, 1) == get_result(
        numbers, lambda x, y: round(x, 1))

    rounded = round(second, -1)
    assert rounded == get_result(
        numbers, lambda x, y: round(y, -1))
    for val in rounded.values():
        assert isinstance(val, int)

    for val in round(first, 0).values():
        assert isinstance(val, int)

    with raises(TypeError):
        round(first)


def test_calculate_ratios():
    _, first, second = get_numbers()
    first_total = sum(first.values())
    assert first.calculate_ratios() == first / first_total

    second_total = sum(second.values())
    assert second.calculate_ratios() == second / second_total

    # make the sum of first's values zero
    first["0"] -= first_total
    # check if the ratios values are all zeros
    assert first.calculate_ratios() == {}
