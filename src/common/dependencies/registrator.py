from typing import Callable, Type, Union

_mapper = {}


def add_factory_to_mapper(class_: Union[Type, Callable]):
    """Декоратор переопределения классов фабрик."""

    def _add_factory_to_mapper(func: Callable):
        _mapper[class_] = func
        return func

    return _add_factory_to_mapper


def get_mapper() -> dict[Union[Type, Callable], Callable]:
    return _mapper
