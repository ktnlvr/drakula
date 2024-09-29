from .character import Character

import pygame
from pygame.event import Event

import numpy as np

from .renderer import Renderer
from .scene import Scene
from .state import GameState, AirportStatus

MAP_SCROLL_SPEED_PX_PER_S = 60

AIRPORT_COLOR = pygame.Color(255, 0, 0)
AIRPORT_TRAPPED_COLOR = pygame.Color(255, 255, 0)
AIRPORT_DESTROYED_COLOR = pygame.Color(102, 88, 73)
AIRPORT_CONNECTION_COLOR = pygame.Color(0, 255, 0)
ICAO_INPUT_COLOR = pygame.Color(200, 200, 200)
ICAO_STATUS_BAR_COLOR = pygame.Color(0, 0, 0, int(255 * 0.3))

CURRENT_AIRPORT_HIGHLIGHT_COLOR = pygame.Color(40, 255, 40)

ICAO_INPUT_WIDTH = 300
ICAO_INPUT_HEIGHT = 40
ICAO_INPUT_PADDING = 5
ICAO_STATUS_PADDING = 10

ICAO_AIRPORT_SCREEN_RADIUS = 0.01
ICAO_AIRPORT_PLAYER_RADIUS = 0.007


class MapScene(Scene):
    def __init__(self, state: GameState, character: Character) -> None:
        super().__init__()

        self.state = state
        self.world_map = pygame.image.load("map.png")
        self.character = character

        self.horizontal_scroll_px = 0

    def render(self, renderer: Renderer):
        self.render_world_map(renderer)
        self.render_airport_network(renderer)
        self.render_icao_input(renderer)

        super().render(renderer)

    def render_world_map(self, renderer: Renderer):
        self.world_map = pygame.transform.scale(self.world_map, renderer.size)
        renderer.surface.blit(self.world_map, (0, 0))

        self.horizontal_scroll_px %= renderer.size[0]
        renderer.surface.blit(self.world_map, (self.horizontal_scroll_px, 0))
        if self.horizontal_scroll_px > 0:
            renderer.surface.blit(
                self.world_map, (self.horizontal_scroll_px - renderer.size[0], 0)
            )
        if self.horizontal_scroll_px < 0:
            renderer.surface.blit(
                self.world_map, (self.horizontal_scroll_px + renderer.size[0], 0)
            )

    def render_airport_network(self, renderer: Renderer):
        normalized_scroll = self.normalized_horizontal_scroll(renderer)

        # Draw airport connections
        for i, js in self.state.graph.items():
            airport = self.state.airports[i]
            a = airport.screen_position
            a = (a[0] + normalized_scroll) % 1.0, a[1]
            for j in js:
                connected_airports = self.state.airports[j]
                b = connected_airports.screen_position
                b = (b[0] + normalized_scroll) % 1.0, b[1]

                renderer.draw_line_wrapping(AIRPORT_CONNECTION_COLOR, a, b)

        # Draw airport markers
        for idx, state in enumerate(self.state.states):
            p = state.airport.screen_position
            p = (p[0] + normalized_scroll) % 1.0, p[1]
            point_color = AIRPORT_COLOR
            if state.status == AirportStatus.TRAPPED:
                point_color = AIRPORT_DESTROYED_COLOR
            elif state.status == AirportStatus.DESTROYED:
                point_color = AIRPORT_DESTROYED_COLOR
            renderer.draw_circle(point_color, p, ICAO_AIRPORT_SCREEN_RADIUS)

            if idx == self.character.current_location:
                renderer.draw_circle(
                    CURRENT_AIRPORT_HIGHLIGHT_COLOR, p, ICAO_AIRPORT_PLAYER_RADIUS
                )

        current_player_airport = self.state.airports[self.character.current_location]
        connected_airports = self.state.graph[self.character.current_location]
        airport_icao_name_font = pygame.font.Font(None, 18)

        for i, idx in enumerate(connected_airports):
            airport = self.state.airports[idx]
            icao_text_surface = airport_icao_name_font.render(
                airport.ident, True, (0, 0, 0)
            )
            airport_position_px = renderer.project(airport.screen_position)
            airport_position_px -= np.array(icao_text_surface.get_size()) / 2

            airport_position_screen = renderer.unproject(airport_position_px)
            player_airport_position_screen = current_player_airport.screen_position

            direction = airport_position_screen - player_airport_position_screen
            direction_normalized = direction / np.linalg.norm(direction)

            airport_position_screen += direction_normalized * ICAO_AIRPORT_SCREEN_RADIUS
            airport_position_px = renderer.project(airport_position_screen)

            renderer.surface.blit(icao_text_surface, airport_position_px)

    def render_icao_input(self, renderer: Renderer):
        font = pygame.font.Font(None, 22)
        input_rect = pygame.Rect()
        input_rect.bottomleft = (
            ICAO_INPUT_PADDING,
            pygame.display.get_surface().get_height()
            - ICAO_INPUT_PADDING
            - ICAO_INPUT_HEIGHT,
        )
        input_rect.width = ICAO_INPUT_WIDTH
        input_rect.height = ICAO_INPUT_HEIGHT

        current_airport = self.state.states[self.character.current_location].airport

        pygame.draw.rect(renderer.surface, ICAO_INPUT_COLOR, input_rect)
        input_text = font.render(
            f"Enter ICAO: {self.character.input_text}", True, (0, 0, 0)
        )
        renderer.surface.blit(
            input_text,
            (input_rect.x + ICAO_INPUT_PADDING, input_rect.y + ICAO_INPUT_PADDING),
        )

        connected_airports = ",".join(
            self.state.airports[i].ident
            for i in self.state.graph[self.character.current_location]
        )

        status_elements = [
            f"Airport: {current_airport.name}",
            f"ICAO: {current_airport.ident}",
            f"Position: {round(current_airport.geo_position[0], 2)}, {round(current_airport.geo_position[1], 2)}",
            f"Connected: {connected_airports}",
        ]

        status_text = font.render(" | ".join(status_elements), True, (255, 255, 255))

        status_rect = pygame.Rect(
            0,
            0,
            renderer.surface.get_width(),
            status_text.get_height() + ICAO_STATUS_PADDING * 2,
        )
        status_surface = pygame.Surface(
            (status_rect.width, status_rect.height), pygame.SRCALPHA
        )
        status_surface.fill(ICAO_STATUS_BAR_COLOR)
        renderer.surface.blit(status_surface, status_rect)
        renderer.surface.blit(status_text, (ICAO_STATUS_PADDING, ICAO_STATUS_PADDING))

    def handle_event(self, event: Event) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.horizontal_scroll_px += 100
            if event.key == pygame.K_RIGHT:
                self.horizontal_scroll_px -= 100
        return super().handle_event(event)

    def normalized_horizontal_scroll(self, renderer) -> float:
        return 0.5 * self.horizontal_scroll_px / renderer.size[1]
