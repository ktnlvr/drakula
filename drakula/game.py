from math import tau

from pygame.event import Event

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
    def __init__(self) -> None:
        super().__init__()

        self.world_map = pygame.image.load("map.png")
        self.horizontal_scroll = 0

    def render(self, state: GameState, renderer: Renderer):
        self.horizontal_scroll %= renderer.size[0]
        renderer.surface.blit(self.world_map, (self.horizontal_scroll, 0))
        if self.horizontal_scroll > 0:
            renderer.surface.blit(self.world_map, (self.horizontal_scroll - renderer.size[0], 0))
        if self.horizontal_scroll < 0:
            renderer.surface.blit(self.world_map, (self.horizontal_scroll + renderer.size[0], 0))

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

        if is_debug_layer_enabled(DEBUG_LAYER_SHOW_SOLAR_TERMINATOR):
            N = 100
            gamma = 0.5
            points = []
            for i in range(N + 1):
                px = (solar_terminator_rad(tau * (state.day_percentage + i / N), gamma) / (tau / 8) + 1) / 2
                points.append((i / N, px))
                
            for i in range(len(points) - 1):
                renderer.draw_line(0, points[i], points[i + 1], 0.001)

        for airport in state.airports:
            p = angles_to_world_pos(airport.latitude_deg, airport.longitude_deg)
            renderer.draw_circle((255, 0, 0), p, 0.01)

        super().render(state, renderer)


    def update(self, state, character):
        cntd_airports = self.get_cntd_airports(state, character.current_airport)
        character.get_cntd_airports(cntd_airports)

    def handle_event(self, renderer: Renderer, event: Event) -> bool:
        if event.type == pygame.VIDEORESIZE:
            surface = pygame.display.get_surface()
            self.world_map = pygame.transform.scale(self.world_map, renderer.size)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.horizontal_scroll += 100
            if event.key == pygame.K_RIGHT:
                self.horizontal_scroll -= 100
        return super().handle_event(renderer, event)

    def get_cntd_airports(self, state, current_airport):
        connected = []
        current_airport_index = state.airports.index(current_airport)
        if current_airport_index in state.graph:
            for connected_index in state.graph[current_airport_index]:
                connected.append(state.airports[connected_index])
        return connected