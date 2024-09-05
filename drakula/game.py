from math import tau

from .scene import Scene
from .renderer import Renderer
from .state import GameState
from .maths import angles_to_world_pos, solar_terminator_rad

import pygame

def should_wrap_coordinate(a: float, b: float, span: float) -> bool:
    signed_distance = b - a
    wrapped_signed_distance = span - signed_distance
    return abs(wrapped_signed_distance) < abs(signed_distance)

class MapScene(Scene):
    def __init__(self) -> None:
        super().__init__()

        self.world_map = pygame.image.load("map.jpg")

    def render(self, state: GameState, renderer: Renderer):
        renderer.blit(self.world_map, (0, 0))

        for i, js in state.graph.items():
            airport = state.airports[i]
            a = angles_to_world_pos(*airport.position)
            for j in js:
                connection = state.airports[j]
                b = angles_to_world_pos(*connection.position)

                # because of the signed distance, the calculations are different for case b[0] > a[0]
                # TODO: figure out the case for b[0] > a[0]
                # until then this logic allows deduping the lines from A->B and B->A
                # AND avoiding handling wrapping around the right edge of the map
                if b[0] < a[0]:
                    continue

                if should_wrap_coordinate(a[0], b[0], 1):
                    renderer.draw_line((255, 200, 0), (a[0], a[1]), (b[0] - 1, b[1]))
                    renderer.draw_line((255, 200, 0), (b[0], b[1]), (a[0] + 1, a[1]))
                else:
                    renderer.draw_line((0, 255, 0), a, b)

        N = 100
        gamma = 0.1
        for i in range(N + 1):
            px = (solar_terminator_rad(tau * (state.day_percentage + i / N), gamma) / (tau / 8) + 1) / 2
            renderer.draw_circle((255, 0, 0), ((i / N), px), .01)

        for airport in state.airports:
            p = angles_to_world_pos(airport.latitude_deg, airport.longitude_deg)
            renderer.draw_circle((255, 0, 0), p, 0.01)

        super().render(state, renderer)