from math import tau

import pygame
from pygame.event import Event

from .debug import DEBUG_LAYER_SHOW_SOLAR_TERMINATOR, is_debug_layer_enabled
from .maths import (
    angles_to_world_pos,
    solar_terminator_rad_from_gp,
    to_julian_datetime,
    solar_position_from_jd,
)
from .renderer import Renderer
from .scene import Scene
from .state import GameState


class MapScene(Scene):
    def __init__(self, state: GameState) -> None:
        super().__init__()

        self.state = state
        self.world_map = pygame.image.load("map.png")

        self.horizontal_scroll = 0

    def render(self, renderer: Renderer):
        self.world_map = pygame.transform.scale(self.world_map, renderer.size)

        self.horizontal_scroll %= renderer.size[0]
        renderer.surface.blit(self.world_map, (self.horizontal_scroll, 0))
        if self.horizontal_scroll > 0:
            renderer.surface.blit(
                self.world_map, (self.horizontal_scroll - renderer.size[0], 0)
            )
        if self.horizontal_scroll < 0:
            renderer.surface.blit(
                self.world_map, (self.horizontal_scroll + renderer.size[0], 0)
            )

        normalized_horizontal_scroll = 0.5 * self.horizontal_scroll / renderer.size[1]
        for i, js in self.state.graph.items():
            airport = self.state.airports[i]
            a = angles_to_world_pos(*airport.position)
            a = [(a[0] + normalized_horizontal_scroll) % 1., a[1]]
            for j in js:
                connection = self.state.airports[j]
                b = angles_to_world_pos(*connection.position)
                b = [(b[0] + normalized_horizontal_scroll) % 1., b[1]]

                renderer.draw_line_wrapping((0, 220, 0), a, b)

        if is_debug_layer_enabled(DEBUG_LAYER_SHOW_SOLAR_TERMINATOR):
            julian_dt = to_julian_datetime(self.state.timestamp)
            sun_lat, sun_lon = solar_position_from_jd(julian_dt)
            sun_pos = angles_to_world_pos(360 * sun_lat / tau, 360 * sun_lon / tau)
            renderer.draw_circle(
                (255, 255, 0, 75),
                sun_pos,
                0.015,
            )

            points = []
            for i in range(-180, 180):
                px = solar_terminator_rad_from_gp(
                    tau * i / 360,
                    sun_lat,
                    sun_lon,
                ) / (tau / 8)
                points.append(((i + 180) / 360, px))

            for i in range(len(points) - 1):
                renderer.draw_line(0, points[i], points[i + 1], 0.001)

        for airport in self.state.airports:
            p = angles_to_world_pos(airport.latitude_deg, airport.longitude_deg)
            p = [(p[0] + normalized_horizontal_scroll) % 1., p[1]]
            renderer.draw_circle((255, 0, 0), p, 0.01)

        super().render(renderer)

    def update(self, state, character):
        cntd_airports = self.get_cntd_airports(state, character.current_airport)
        character.get_cntd_airports(cntd_airports)

    def handle_event(self, renderer: Renderer, event: Event) -> bool:
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
