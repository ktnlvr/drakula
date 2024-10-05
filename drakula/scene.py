from abc import ABC, abstractmethod

import pygame

from .renderer import Renderer


class Scene(ABC):
    @abstractmethod
    def render(self, renderer: Renderer): ...

    def handle_event(self, _: pygame.event.Event) -> bool:
        return False
