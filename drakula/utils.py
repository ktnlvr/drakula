from collections.abc import Callable, Generator
from typing import TypeVar
from logging import getLogger

T = TypeVar("T")
U = TypeVar("U")


def list_map(ls: list[T], f: Callable[[T], U]) -> list[U]:
    return [f(**x) for x in ls]


def kwarg_id(argname: str):
    def func(*args, **kwargs):
        return kwargs[argname]

    return func


def flatten(ls: list[list[T]]) -> Generator[T, None, None]:
    for sublist in ls:
        yield from sublist


def pairs(ls):
    length = len(ls)
    for i in range(length - 1):
        yield ls[i], ls[i + 1]
    yield ls[-1], ls[0]


# Used to load shader files
def load_shader(shader_file):
    with open(shader_file, "r") as file:
        return file.read()
