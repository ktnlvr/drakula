from math import tau

import pygame

from . import Character
from .debug import DEBUG_LAYER_SHOW_SOLAR_TERMINATOR, is_debug_layer_enabled
from .maths import angles_to_world_pos, solar_terminator_rad
from .renderer import Renderer
from .scene import Scene
from .state import GameState, AirportStatus


class MapScene(Scene):
    def __init__(self, state: GameState, character: Character) -> None:
        super().__init__()

        self.state = state
        self.world_map = pygame.image.load("map.jpg")
        self.character = character

    def render(self, renderer: Renderer):
        renderer.surface.blit(self.world_map, (0, 0))

        for i, js in self.state.graph.items():
            airport = self.state.airports[i]
            a = angles_to_world_pos(*airport.position)
            for j in js:
                connection = self.state.airports[j]
                b = angles_to_world_pos(*connection.position)

                renderer.draw_line_wrapping(
                    (0, 255, 0), a, b, color_if_wrap=(255, 200, 0)
                )

        if is_debug_layer_enabled(DEBUG_LAYER_SHOW_SOLAR_TERMINATOR):
            N = 100
            gamma = 0.5
            points = []
            for i in range(N + 1):
                px = (
                    solar_terminator_rad(
                        tau * (i / N - self.state.day_percentage), gamma
                    )
                    / (tau / 8)
                    + 1
                ) / 2
                points.append((i / N, px))

            for i in range(len(points) - 1):
                renderer.draw_line(0, points[i], points[i + 1], 0.001)

        for state in self.state.states:
            airport = state.airport
            p = angles_to_world_pos(airport.latitude_deg, airport.longitude_deg)
            if state.status == AirportStatus.TRAPPED:
                renderer.draw_circle((255, 255, 0), p, 0.01)
            else:
                renderer.draw_circle((255, 0, 0), p, 0.01)

        font = pygame.font.Font(None, 22)
        input_rect = pygame.Rect(10, 0, 300, 40)
        input_rect.bottomleft = (5, pygame.display.get_surface().get_height() - 5)

        current_airport = self.state.states[self.character.current_location].airport
        current_airport_pos = current_airport.position
        world_pos = angles_to_world_pos(*current_airport_pos)
        renderer.draw_circle((0, 255, 0), world_pos, 0.007)
        bg_color = pygame.Color(200, 200, 200)

        pygame.draw.rect(renderer.surface, bg_color, input_rect)
        input_text = font.render(f"Enter ICAO: {self.character.input_text}", True, (0, 0, 0))
        renderer.surface.blit(
            input_text, (input_rect.x + 5, input_rect.y + 5)
        )

        connected_airports = ",".join(self.state.airports[i].ident for i in self.state.graph[self.character.current_location])
        info_str = f" Airport: {current_airport.name}  |  ICAO: {current_airport.ident}  |  Position:{current_airport.position}  | Connected Airports:{connected_airports}"
        info_text = font.render(info_str, True, (255, 255, 255))

        padding = 5
        bg_rect = pygame.Rect(
            0, 0, renderer.surface.get_width(), info_text.get_height() + padding * 2
        )
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 76))  # 30% opacity
        renderer.surface.blit(bg_surface, bg_rect)
        renderer.surface.blit(info_text, (padding, padding))

        super().render(renderer)
