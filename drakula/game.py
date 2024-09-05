from .scene import Scene
from .renderer import Renderer
from .state import GameState

import pygame

class MapScene(Scene):
    def __init__(self) -> None:
        super().__init__()

        self.world_map = pygame.image.load("map.jpg")

    def render(self, state: GameState, renderer: Renderer):
        renderer.blit(self.world_map, (0, 0))

        super().render(state, renderer)