from math import tau

from .utils import pairs
from .scene import Scene
from .renderer import Renderer
from .state import GameState
from .maths import (
    angles_to_world_pos,
    solar_terminator_rad_from_gp,
    to_julian_datetime,
    solar_position_from_jd,
)
from .debug import DEBUG_LAYER_SHOW_SOLAR_TERMINATOR, is_debug_layer_enabled

import pygame
import numpy as np

class MapScene(Scene):
    def __init__(self, state: GameState) -> None:
        super().__init__()

        self.state = state
        self.world_map = pygame.image.load("map.jpg")

    def render(self, renderer: Renderer):
        renderer.blit(self.world_map, (0, 0))

        for i, js in self.state.graph.items():
            airport = self.state.airports[i]
            a = angles_to_world_pos(*airport.position)
            for j in js:
                connection = self.state.airports[j]
                b = angles_to_world_pos(*connection.position)

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
            renderer.draw_circle((255, 0, 0), p, 0.01)

        super().render(renderer)
