from abc import ABC, abstractmethod
from typing import Optional

import pygame

from .renderer import Renderer
from .state import GameState

class Scene(ABC):
    @property
    def previous_scene(self) -> Optional['Scene']:
        return None

    @abstractmethod
    def render(self, state: GameState, renderer: Renderer):
        ...

    @property
    def next_scene(self) -> 'Scene':
        return self
    
    def handle_event(self, renderer: Renderer, _: pygame.event.Event) -> bool:
        return False
