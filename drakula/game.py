from .character import Character

import pygame
from pygame.event import Event

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
            renderer.draw_circle(point_color, p, 0.01)

            if idx == self.character.current_location:
                renderer.draw_circle(CURRENT_AIRPORT_HIGHLIGHT_COLOR, p, 0.007)

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

    def display_connected_airports(self, renderer):
        cntd_airports = self.state.graph[self.character.current_location]
        font = pygame.font.Font(None, 18)
        screen_width = renderer.surface.get_width()
        screen_height = renderer.surface.get_height()
        positions = []  # To track where we've drawn text
        text_surfaces = []  # To store text surfaces for hover detection

        for airport_index in cntd_airports:
            airport = self.state.states[airport_index].airport
            if self.state.states[airport_index].status != AirportStatus.AVAILABLE:
                continue
            screen_pos = airport.screen_position
            screen_pos = (
                screen_pos[0] * screen_width - 15,
                screen_pos[1] * screen_height - 20,
            )

            # Check for overlaps and adjust position if necessary
            while any(
                    (abs(screen_pos[0] - pos[0]) < 10 and abs(screen_pos[1] - pos[1]) < 10)
                    for pos in positions
            ):
                screen_pos = (screen_pos[0] + 10, screen_pos[1] + 10)

            # Check if the text is going off-screen and adjust position
            text_surface = font.render(airport.ident, True, (0, 0, 0))
            text_rect = text_surface.get_rect(topleft=screen_pos)

            # Adjust position if text is off-screen
            if text_rect.right > screen_width:
                screen_pos = (
                    screen_width - text_rect.width,
                    screen_pos[1],
                )  # Align to the right edge
            if text_rect.bottom > screen_height:
                screen_pos = (
                    screen_pos[0],
                    screen_height - text_rect.height,
                )  # Align to the bottom edge
            if text_rect.left < 0:
                screen_pos = (0, screen_pos[1])  # Align to the left edge
            if text_rect.top < 0:
                screen_pos = (screen_pos[0], 0)  # Align to the top edge

            positions.append(screen_pos)

            # Render the ICAO code text surface
            text_surface = font.render(airport.ident, True, (0, 0, 0))
            text_surfaces.append(
                (text_surface, screen_pos, airport.ident)
            )  # Store surface, position, and ICAO code

            # Blit the text at the calculated position
            renderer.surface.blit(text_surface, screen_pos)

    def handle_event(self, event: Event) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.horizontal_scroll_px += 100
            if event.key == pygame.K_RIGHT:
                self.horizontal_scroll_px -= 100
        return super().handle_event(event)

    def normalized_horizontal_scroll(self, renderer) -> float:
        return 0.5 * self.horizontal_scroll_px / renderer.size[1]
