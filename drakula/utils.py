import pygame
import moderngl
from collections.abc import Callable, Generator
from typing import TypeVar, Optional, Tuple

T = TypeVar("T")
U = TypeVar("U")


def list_map(ls: list[T], f: Callable[[T], U]) -> list[U]:
    return [f(**x) for x in ls]


def kwarg_id(argname: str):
    def func(*args, **kwargs):
        return kwargs[argname]

    return func


def pairs(ls):
    length = len(ls)
    for i in range(length - 1):
        yield ls[i], ls[i + 1]
    yield ls[-1], ls[0]


def load_shader(shader_file):
    with open(shader_file, "r") as file:
        return file.read()


def load_texture(texture_file, screen_size: Optional[Tuple[int, int]] = None):
    ctx = moderngl.create_context()
    image = pygame.image.load(texture_file).convert_alpha()
    if screen_size:
        image = pygame.transform.scale(image, screen_size)
    texture = ctx.texture(image.get_size(), 4, pygame.image.tostring(image, "RGBA"))
    return texture
