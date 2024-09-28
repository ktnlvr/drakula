from .character import Character

import pygame
from pygame.event import Event

from .maths import (
    angles_to_world_pos,
)

from .renderer import Renderer, AirportStatus
from .scene import Scene
from .state import GameState, AirportStatus

MAP_SCROLL_SPEED_PX_PER_S = 60


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

        for i, js in self.state.graph.items():
            airport = self.state.airports[i]
            a = angles_to_world_pos(*airport.position)
            a = [(a[0] + normalized_scroll) % 1.0, a[1]]
            for j in js:
                connection = self.state.airports[j]
                b = angles_to_world_pos(*connection.position)
                b = [(b[0] + normalized_scroll) % 1.0, b[1]]

                renderer.draw_line_wrapping((0, 255, 0), a, b)

        for state in self.state.states:
            airport = state.airport
            p = angles_to_world_pos(airport.latitude_deg, airport.longitude_deg)
            p = [(p[0] + normalized_scroll) % 1.0, p[1]]
            point_color = (255, 0, 0)
            if state.status == AirportStatus.TRAPPED:
                point_color = (255, 200, 0)
            renderer.draw_circle(point_color, p, 0.01)

    def render_icao_input(self, renderer: Renderer):
        font = pygame.font.Font(None, 22)
        input_rect = pygame.Rect(10, 0, 300, 40)
        input_rect.bottomleft = (5, pygame.display.get_surface().get_height() - 5)

        current_airport = self.state.states[self.character.current_location].airport
        current_airport_pos = current_airport.position
        world_pos = angles_to_world_pos(*current_airport_pos)
        renderer.draw_circle((0, 255, 0), world_pos, 0.007)
        bg_color = pygame.Color(200, 200, 200)

        pygame.draw.rect(renderer.surface, bg_color, input_rect)
        input_text = font.render(
            f"Enter ICAO: {self.character.input_text}", True, (0, 0, 0)
        )
        renderer.surface.blit(input_text, (input_rect.x + 5, input_rect.y + 5))

        connected_airports = ",".join(
            self.state.airports[i].ident
            for i in self.state.graph[self.character.current_location]
        )
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
            world_pos = angles_to_world_pos(*airport.position)
            world_pos = (
                world_pos[0] * screen_width - 15,
                world_pos[1] * screen_height - 20,
            )

            # Check for overlaps and adjust position if necessary
            while any(
                    (abs(world_pos[0] - pos[0]) < 10 and abs(world_pos[1] - pos[1]) < 10)
                    for pos in positions
            ):
                world_pos = (world_pos[0] + 10, world_pos[1] + 10)

            # Check if the text is going off-screen and adjust position
            text_surface = font.render(airport.ident, True, (0, 0, 0))
            text_rect = text_surface.get_rect(topleft=world_pos)

            # Adjust position if text is off-screen
            if text_rect.right > screen_width:
                world_pos = (
                    screen_width - text_rect.width,
                    world_pos[1],
                )  # Align to the right edge
            if text_rect.bottom > screen_height:
                world_pos = (
                    world_pos[0],
                    screen_height - text_rect.height,
                )  # Align to the bottom edge
            if text_rect.left < 0:
                world_pos = (0, world_pos[1])  # Align to the left edge
            if text_rect.top < 0:
                world_pos = (world_pos[0], 0)  # Align to the top edge

            positions.append(world_pos)

            # Render the ICAO code text surface
            text_surface = font.render(airport.ident, True, (0, 0, 0))
            text_surfaces.append(
                (text_surface, world_pos, airport.ident)
            )  # Store surface, position, and ICAO code

            # Blit the text at the calculated position
            renderer.surface.blit(text_surface, world_pos)

    def handle_event(self, event: Event) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.horizontal_scroll_px += 100
            if event.key == pygame.K_RIGHT:
                self.horizontal_scroll_px -= 100
        return super().handle_event(event)

    def normalized_horizontal_scroll(self, renderer) -> float:
        return (
                0.5 * self.horizontal_scroll_px / renderer.size[1]
        )
