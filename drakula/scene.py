from abc import ABC, abstractmethod
from typing import Optional

from .renderer import Renderer
from .state import GameState

class Scene(ABC):
    @property
    def previous_scene(self) -> Optional['Scene']:
        return None

    @abstractmethod
    def render(self, state: GameState, renderer: Renderer):
        ...
