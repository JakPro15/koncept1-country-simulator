from contextlib import contextmanager
from io import StringIO
import sys
from typing import Any, Generator, Type

from pytest import approx  # type: ignore


def dict_eq(dict1: dict[Any, float], dict2: dict[Any, float]) -> bool:
    try:
        for key in dict1 | dict2:
            if dict1[key] != approx(dict2[key]):
                return False
    except KeyError:
        return False
    return True


class replace:
    def __init__(self, class_or_object: Any, attr_name: str, new_attr: Any
                 ) -> None:
        self.class_ = class_or_object
        self.attr_name = attr_name
        self.new_attr = new_attr

    def __enter__(self) -> None:
        self.old_attr = getattr(self.class_, self.attr_name)
        setattr(self.class_, self.attr_name, self.new_attr)

    def __exit__(self, class_: Type[Any], attr_name: str, new_attr: Any
                 ) -> None:
        setattr(self.class_, self.attr_name, self.old_attr)


class create:
    def __init__(self, class_: Type[Any], attr_name: str, new_attr: Any
                 ) -> None:
        self.class_ = class_
        self.attr_name = attr_name
        self.new_attr = new_attr

    def __enter__(self) -> None:
        setattr(self.class_, self.attr_name, self.new_attr)

    def __exit__(self, class_: Type[Any], attr_name: str, new_attr: Any
                 ) -> None:
        delattr(self.class_, self.attr_name)


@contextmanager
def capture_standard_output() -> Generator[StringIO, None, None]:
    fake_stdout = StringIO()
    old_stdout = sys.stdout
    try:
        sys.stdout = fake_stdout
        yield fake_stdout
    finally:
        sys.stdout = old_stdout


@contextmanager
def set_standard_input(text: str) -> Generator[StringIO, None, None]:
    fake_stdin = StringIO(text)
    old_stdin = sys.stdin
    try:
        sys.stdin = fake_stdin
        yield fake_stdin
    finally:
        sys.stdin = old_stdin
