from typing import Any, Callable, ParamSpec, Type

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
    def __init__(self, class_: Type[Any], attr_name: str, new_attr: Any
                 ) -> None:
        self.class_ = class_
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


P = ParamSpec("P")


class decorate:
    def __init__(self, class_: Type[Any], meth_name: str,
                 decor: Callable[P, Any]) -> None:
        self.class_ = class_
        self.meth_name = meth_name
        self.decor = decor

    def __enter__(self) -> None:
        self.old_meth = getattr(self.class_, self.meth_name)

        def new_meth(*args: P.args, **kwargs: P.kwargs):
            self.decor(*args, **kwargs)
            return self.old_meth(*args, **kwargs)

        setattr(self.class_, self.meth_name, new_meth)

    def __exit__(self, class_: Type[Any], attr_name: str, new_attr: Any
                 ) -> None:
        setattr(self.class_, self.meth_name, self.old_meth)
