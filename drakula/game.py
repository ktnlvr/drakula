from math import tau

from .utils import pairs
from .scene import Scene
from .renderer import Renderer
from .state import GameState
from .maths import angles_to_world_pos, solar_terminator_rad
from .debug import DEBUG_LAYER_SHOW_SOLAR_TERMINATOR, is_debug_layer_enabled

import pygame

def should_wrap_coordinate(a: float, b: float, span: float) -> bool:
    signed_distance = b - a
    wrapped_signed_distance = span - signed_distance
    return abs(wrapped_signed_distance) < abs(signed_distance)

class MapScene(Scene):
    def __init__(self, state: GameState) -> None:
        super().__init__()

        self.state = state
        self.world_map = pygame.image.load("map.jpg")

    def render(self, state: GameState, renderer: Renderer):
        renderer.surface.blit(self.world_map, (0, 0))

        for i, js in self.state.graph.items():
            airport = self.state.airports[i]
            a = angles_to_world_pos(*airport.position)
            for j in js:
                connection = self.state.airports[j]
                b = angles_to_world_pos(*connection.position)

                renderer.draw_line_wrapping((0, 255, 0), a, b, color_if_wrap=(255, 200, 0))

        if is_debug_layer_enabled(DEBUG_LAYER_SHOW_SOLAR_TERMINATOR):
            N = 100
            gamma = 0.5
            points = []
            for i in range(N + 1):
                px = (solar_terminator_rad(tau * (i / N - self.state.day_percentage), gamma) / (tau / 8) + 1) / 2
                points.append((i / N, px))

            for i in range(len(points) - 1):
                renderer.draw_line(0, points[i], points[i + 1], 0.001)

        for airport in self.state.airports:
            p = angles_to_world_pos(airport.latitude_deg, airport.longitude_deg)
            renderer.draw_circle((255, 0, 0), p, 0.01)

        super().render(state)


    def update(self, state, character):
        cntd_airports = self.get_cntd_airports(state, character.current_airport)
        character.get_cntd_airports(cntd_airports)

    def get_cntd_airports(self, state, current_airport):
        connected = []
        current_airport_index = state.airports.index(current_airport)
        if current_airport_index in state.graph:
            for connected_index in state.graph[current_airport_index]:
                connected.append(state.airports[connected_index])
        return connected