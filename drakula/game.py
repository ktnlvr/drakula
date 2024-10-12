import pygame
from pygame.event import Event
from enum import Enum
from typing import Optional, List, NoReturn, Union

import numpy as np

from .renderer import Renderer
from .scene import Scene
from .state import GameState, AirportStatus
from .character import Character

MAP_SCROLL_ACCELERATION_COEFFICIENT = 21
MAP_SCROLL_SPEED_PERCENT_PER_S = 25

AIRPORT_COLOR = pygame.Color(255, 70, 70)
AIRPORT_TRAPPED_COLOR = pygame.Color(255, 255, 0)
AIRPORT_DESTROYED_COLOR = pygame.Color(102, 88, 73)
AIRPORT_CONNECTION_COLOR = pygame.Color(200, 200, 200)
AVAILABLE_AIRPORT_CONNECTION_COLOR = pygame.Color(0, 255, 0)
ICAO_INPUT_COLOR = pygame.Color(200, 200, 200)
ICAO_STATUS_BAR_COLOR = pygame.Color(0, 0, 0, int(255 * 0.3))

CURRENT_AIRPORT_HIGHLIGHT_COLOR = pygame.Color(40, 255, 40)

ICAO_INPUT_WIDTH = 300
ICAO_INPUT_HEIGHT = 40
ICAO_INPUT_PADDING = 5
ICAO_STATUS_PADDING = 10

ICAO_AIRPORT_SCREEN_RADIUS = 0.01
ICAO_AIRPORT_PLAYER_RADIUS = 0.01


class MapScene(Scene):
    def __init__(self, state: GameState, character: Character) -> None:
        super().__init__()

        self.state = state

        self.character = character

        self.horizontal_scroll_px = 0
        self.current_scroll_speed = 0
        self.target_scroll_speed = 0

    def render(self, renderer: Renderer):
        renderer.surface.fill((0, 0, 0, 0))
        self.update_scroll(renderer)
        self.scroll_world_map(renderer)
        self.render_airport_network(renderer)
        self.render_icao_input(renderer)
        self.render_dracula_warning(renderer)

        super().render(renderer)

    def update_scroll(self, renderer: Renderer):
        dt = renderer.delta_time

        # https://youtu.be/LSNQuFEDOyQ?si=UjWW6xscLc3TvTP2&t=2991
        def exp_decay(a, b, decay):
            return b + (a - b) * np.exp(-decay * dt)

        lerp_speed = MAP_SCROLL_ACCELERATION_COEFFICIENT
        self.current_scroll_speed = exp_decay(
            self.current_scroll_speed, self.target_scroll_speed, lerp_speed
        )

        horizontal_scroll_px_per_s = (
            renderer.size[0] * MAP_SCROLL_SPEED_PERCENT_PER_S / 100
        )
        self.horizontal_scroll_px += (
            self.current_scroll_speed * horizontal_scroll_px_per_s * dt
        )

    def scroll_world_map(self, renderer: Renderer):
        renderer.horizontal_scroll = self.normalized_horizontal_scroll(renderer)

    def render_airport_network(self, renderer: Renderer):
        def apply_scroll(arr):
            normalized_scroll = self.normalized_horizontal_scroll(renderer)
            return np.array([(arr[0] + normalized_scroll) % 1.0, arr[1]])

        # Draw airport connections
        for i, js in self.state.graph.items():
            airport = self.state.airports[i]
            a = apply_scroll(airport.screen_position)
            for j in js:
                connected_airports = self.state.airports[j]
                b = apply_scroll(connected_airports.screen_position)

                if (
                    i == self.character.current_location
                    or j == self.character.current_location
                ):
                    connection_color = AVAILABLE_AIRPORT_CONNECTION_COLOR
                else:
                    connection_color = AIRPORT_CONNECTION_COLOR

                renderer.draw_line_wrapping(connection_color, a, b)

        # Draw airport markers
        for idx, state in enumerate(self.state.states):
            p = apply_scroll(state.airport.screen_position)
            point_color = AIRPORT_COLOR
            if state.status == AirportStatus.TRAPPED:
                point_color = AIRPORT_TRAPPED_COLOR
            elif state.status == AirportStatus.DESTROYED:
                point_color = AIRPORT_DESTROYED_COLOR
            elif idx == self.character.current_location:
                point_color = CURRENT_AIRPORT_HIGHLIGHT_COLOR

            renderer.draw_circle(point_color, p, ICAO_AIRPORT_SCREEN_RADIUS)
            if idx == self.character.current_location:
                renderer.draw_circle(
                    CURRENT_AIRPORT_HIGHLIGHT_COLOR, p, 0.005
                )

        current_player_airport = self.state.airports[self.character.current_location]
        connected_airports = self.state.graph[self.character.current_location]
        airport_icao_name_font = renderer.font(18)

        for i, idx in enumerate(connected_airports):
            airport = self.state.airports[idx]
            icao_text_surface = airport_icao_name_font.render(
                airport.ident, True, (255, 255, 255)
            )
            airport_position_px = renderer.project(airport.screen_position)
            airport_position_px -= np.array(icao_text_surface.get_size()) / 2

            airport_position_screen = renderer.unproject(airport_position_px)
            player_airport_position_screen = current_player_airport.screen_position

            direction = airport_position_screen - player_airport_position_screen
            direction_normalized = direction / np.linalg.norm(direction)

            airport_position_screen += direction_normalized * ICAO_AIRPORT_SCREEN_RADIUS
            airport_position_px = renderer.project(
                apply_scroll(airport_position_screen)
            )

            renderer.text_surface.blit(icao_text_surface, airport_position_px)

    def render_icao_input(self, renderer: Renderer):
        font = renderer.font(18)
        input_rect = pygame.Rect(0, 0, 0, 0)
        input_rect.bottomleft = (
            ICAO_INPUT_PADDING,
            renderer.size[1] - ICAO_INPUT_PADDING - ICAO_INPUT_HEIGHT,
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

    def render_dracula_warning(self, renderer: Renderer):
        if not self.state.is_dracula_near_trap():
            return
        if self.state.dracula_on_trap():
            warning_message = "Dracula is trapped on one of the traps"
        else:
            warning_message = "Your traps sense a spooky presence"
        font = renderer.font(36)
        text_surface = font.render(warning_message, True, (255, 0, 0))
        text_width, text_height = np.array([*text_surface.get_size()]) / renderer.size
        text_x = 1 - text_width
        text_y = 1 - text_height
        renderer.blit(text_surface, (text_x, text_y))

    def handle_event(self, event: Event) -> bool:
        self.target_scroll_speed = 0
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.target_scroll_speed += 1
            if event.key == pygame.K_RIGHT:
                self.target_scroll_speed -= 1

        # lazy evaluation ftw
        # https://docs.python.org/2/reference/expressions.html#boolean-operations
        return bool(self.target_scroll_speed) or super().handle_event(event)

    def normalized_horizontal_scroll(self, renderer) -> float:
        return self.horizontal_scroll_px / renderer.size[0]


# TODO: bad name, rename me?
class GameOverKind(Enum):
    WIN = 0
    LOSS_CAUGHT = 1
    LOSS_DESTROYED = 2


class GameOverScene(Scene):
    def __init__(self, previous_scene: Scene, kind: GameOverKind,state: Optional[GameState] = None):
        super().__init__()
        self.previous_scene = previous_scene
        self.result_kind = kind
        self.state = state or getattr(previous_scene, 'state', None)

    def wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if font.size(test_line)[0] > max_width:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def render(self, renderer: Renderer):
        self.previous_scene.render(renderer)
        self.display_result(renderer)

    def display_result(self, renderer: Renderer):
        result_font = renderer.font(40)
        option_font =  renderer.font(20)

        box_width, box_height = 700, 350
        screen_width, screen_height = renderer.surface.get_size()
        box_x = (screen_width - box_width) // 2
        box_y = (screen_height - box_height) // 2
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (0, 0, 0, 200), box_surface.get_rect(), border_radius=20)

        if self.result_kind == GameOverKind.WIN:
            result_text = result_font.render("You Caught Dracula!", True, (0, 255, 0))
        elif self.result_kind == GameOverKind.LOSS_CAUGHT:
            result_text = result_font.render("You got caught!", True, (255, 0, 0))
        elif self.result_kind == GameOverKind.LOSS_DESTROYED:
            result_text = result_font.render("The world was destroyed!", True, (255, 0, 0))

        result_rect = result_text.get_rect(center= (box_width // 2, box_height // 3))
        box_surface.blit(result_text, result_rect)

        title_text = option_font.render("Dracula Destroyed Airports:", True, (255, 215, 0))
        title_rect = title_text.get_rect(midtop=(box_width // 2, result_rect.bottom - 5))
        box_surface.blit(title_text, title_rect)

        if self.state and self.state.destroyed_airports:
            filtered_airports = [
                self.state.airports[airport_index].ident
                for airport_index in self.state.destroyed_airports
                if airport_index != 0
            ]
            destroyed_airports_str = ', '.join(filtered_airports)
            wrapped_lines = self.wrap_text(destroyed_airports_str, option_font, box_width - 20)  # Adjust for padding

            y_position = box_height // 2
            line_spacing = 5
            for line in wrapped_lines:
                options_text = option_font.render(line, True, (0, 0, 255))
                options_rect = options_text.get_rect(midtop=(box_width // 2, y_position))
                box_surface.blit(options_text, options_rect)
                y_position += options_text.get_height() + line_spacing

        border_rect = box_surface.get_rect()
        pygame.draw.rect(box_surface, (255, 215, 0), border_rect, width=1, border_radius=20)
        renderer.text_surface.blit(box_surface, (box_x, box_y))

    def handle_event(self, event: pygame.event.Event) -> Union[NoReturn, bool]:
        if event.type == pygame.KEYDOWN:
            exit(0)
        return False
