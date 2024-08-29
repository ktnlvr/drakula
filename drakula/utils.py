from collections.abc import Callable
from typing import TypeVar

T = TypeVar('T')
U = TypeVar('U')

def list_map(ls: list[T], f: Callable[[T], U]) -> list[U]:
    return [f(**x) for x in ls]

def kwarg_id(argname: str):
    def func(*args, **kwargs):
        return kwargs[argname]
    return func
