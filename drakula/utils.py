import pygame
import moderngl
from collections.abc import Callable, Generator
from typing import TypeVar, Optional, Tuple

T = TypeVar("T")
U = TypeVar("U")


def list_map(ls: list[T], f: Callable[[T], U]) -> list[U]:
    """
    :param ls: List of type T
    :param f: A function which takes element of type T and returns a value of type U
    :return: Returns list of type U
    """
    return [f(**x) for x in ls]


def kwarg_id(argname: str):
    def func(*args, **kwargs):
        return kwargs[argname]

    return func


def pairs(ls):
    """
    :param ls: The list of elements to be paired
    :return: Tuples containing adjacent elements from the list. The first element is
    paired with the last element.
    """
    length = len(ls)
    for i in range(length - 1):
        yield ls[i], ls[i + 1]
    yield ls[-1], ls[0]


def load_shader(shader_file):
    """
    :param shader_file: Path to the shader file
    :return: contents of the shaders_file
    """
    with open(shader_file, "r") as file:
        return file.read()


def load_texture(
        ctx: moderngl.Context,
        texture_file: str,
        desired_size: Optional[Tuple[int, int]] = None,
):
    """
    :param ctx: The moderngl (opengl) context to load the image in
    :param texture_file: The filepath to load the texture from
    :param desired_size: The size to scale the texture to. No up-scaling applied if `None`.
    :return: The scaled texture
    """
    image = pygame.image.load(texture_file).convert_alpha()
    if desired_size:
        image = pygame.transform.scale(image, desired_size)
    texture = ctx.texture(image.get_size(), 4, pygame.image.tostring(image, "RGBA"))
    return texture
