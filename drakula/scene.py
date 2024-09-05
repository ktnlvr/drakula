from abc import ABC, abstractmethod
from typing import Optional

from .renderer import Renderer
from .state import GameState

class Scene:
    def previous_scene() -> Optional['Scene']:
        return None

    @abstractmethod
    def render(self, state: GameState, renderer: Renderer):
        ...
