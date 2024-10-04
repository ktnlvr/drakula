from datetime import datetime
from typing import Tuple, Optional

import moderngl
import numpy as np
import pygame
from .utils import load_shader
from .character import CharacterInputResult

Coordinate = Tuple[float, float]


def should_wrap_coordinate(a: float, b: float, span: float) -> bool:
    signed_distance = b - a
    wrapped_signed_distance = span - signed_distance
    return abs(wrapped_signed_distance) < abs(signed_distance)


PYGAME_MODE_FLAGS = (
    pygame.OPENGL | pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF
)


def get_screen_size():
    screen_info = pygame.display.Info()
    return np.array(
        list(map(int, [screen_info.current_w * 0.9, screen_info.current_h * 0.9]))
    )


class Renderer:
    def __init__(self, screen_size: Optional[Tuple[int, int]] = None):
        pygame.init()
        pygame.font.init()
        self.scaling_factor = screen_size[0] / 1280
        self.result_font = self.scaled_font('Arial', 60, bold=True)
        self.option_font = self.scaled_font('Arial', 40)
        self.info_font = self.scaled_font('Arial', 15)

        if screen_size is None:
            screen_size = get_screen_size()
        self.screen = pygame.display.set_mode(screen_size, PYGAME_MODE_FLAGS)
        self.surface = pygame.Surface(screen_size, flags=pygame.SRCALPHA)
        self.fullscreen = False
        self.ctx = moderngl.create_context()
        self.screen_texture = self.ctx.texture(screen_size, 4)

        self.vertex_shader = load_shader("drakula/shaders/vertex_shader.glsl")
        self.fragment_shader = load_shader("drakula/shaders/fragment_shader.glsl")
        self.program = self.ctx.program(
            vertex_shader=self.vertex_shader, fragment_shader=self.fragment_shader
        )
        self._screen_quad_vertices = np.array(
            [[-1.0, -1], [1.0, -1], [-1, 1], [1, 1]], dtype="f4"
        )
        self.vbo = self.ctx.buffer(self._screen_quad_vertices)
        self.vao = self.ctx.simple_vertex_array(self.program, self.vbo, "position")

        self.clock = pygame.time.Clock()
        self.start_time = pygame.time.get_ticks()
        self.last_time = self.start_time
        self.current_time = None
        self.time = 0
        self.delta_time = 0
        self.frame_count = 0

    def scaled_font(self, font_name: str, size: int, bold: bool = False) -> pygame.font.Font:
            return pygame.font.SysFont(font_name, int(size * self.scaling_factor), bold)

    def blit(self, source: pygame.Surface, at: Coordinate):
        self.surface.blit(source, self.project(at))

    def begin(self):
        self.surface.fill((255, 0, 255, 255))

        self.current_time = pygame.time.get_ticks()
        self.time = (self.current_time - self.start_time) / 1000.0
        self.delta_time = (self.current_time - self.last_time) / 1000.0

        now = datetime.now()
        year, month, day = now.year, now.month, now.day
        seconds_since_midnight = (
            now - now.replace(hour=0, minute=0, second=0, microsecond=0)
        ).total_seconds()

        screen_size = self.size

        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        self.set_uniform("iResolution", [*screen_size, 1.0])
        self.set_uniform("iTime", self.time)
        self.set_uniform("iTimeDelta", self.delta_time)
        self.set_uniform("iFrame", self.frame_count)
        self.set_uniform(
            "iMouse",
            (
                mouse_pos[0],
                screen_size[1] - mouse_pos[1],
                mouse_buttons[0],
                mouse_buttons[2],
            ),
        )
        self.set_uniform("iDate", (year, month, day, seconds_since_midnight))

    def set_uniform(self, name, value):
        if name in self.program._members:
            self.program[name].value = value

    def draw_line(
        self, color: pygame.Color, begin: Coordinate, end: Coordinate, width: float = 0
    ):
        pygame.draw.line(
            self.surface,
            color,
            self.project(begin),
            self.project(end),
            int(max(width * self.minimal_scalar, 1)),
        )

    def draw_line_wrapping(
        self,
        color: pygame.Color,
        begin: Coordinate,
        end: Coordinate,
        width: float = 0,
        color_if_wrap: Optional[pygame.Color] = None,
    ):
        a, b = begin, end
        if b[0] < a[0]:
            a, b = b, a
        if should_wrap_coordinate(a[0], b[0], 1):
            self.draw_line(color_if_wrap or color, a, (b[0] - 1, b[1]), width)
            self.draw_line(color_if_wrap or color, b, (a[0] + 1, a[1]), width)
        else:
            self.draw_line(color, a, b, width)

    def draw_circle(self, color: pygame.Color, at: Coordinate, radius: float):
        pygame.draw.circle(
            self.surface, color, self.project(at), radius * self.minimal_scalar
        )
    # just for testing
    def display_dracula_location(self, dra_icao: str):
        dra_text = self.info_font.render(f"Dracula is at: {dra_icao}", True, (0, 0, 255))
        text_rect = dra_text.get_rect()
        screen_width, screen_height = self.surface.get_size()
        x_position = screen_width - text_rect.width - 10
        y_position = screen_height - text_rect.height - 10
        self.surface.blit(dra_text, (x_position, y_position))

    def display_destroyed_airports(self, destroyed_airports: set):
        filtered_airports = [str(airport) for airport in destroyed_airports if airport != 0]
        destroyed_airports_str = ', '.join(str(airport) for airport in filtered_airports)
        destroyed_text = self.info_font.render(f"Destroyed Airports: {destroyed_airports_str}", True, (0, 0, 255))
        text_rect = destroyed_text.get_rect()
        screen_width, screen_height = self.surface.get_size()
        x_position = (screen_width - text_rect.width) // 2
        y_position = screen_height - text_rect.height - 10
        self.surface.blit(destroyed_text, (x_position, y_position))

    def display_result(self, result: str):
        box_width, box_height = 700, 350
        screen_width, screen_height = self.surface.get_size()
        box_x = (screen_width - box_width) // 2
        box_y = (screen_height - box_height) // 2
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (0, 0, 0, 200), box_surface.get_rect(), border_radius=20)

        if "Win" in result:
            result_text = self.result_font.render("You Catched Dracula!", True, (0, 255, 0))
        elif "Lose" in result:
            result_text = self.result_font.render("Game Over", True, (255, 0, 0))
        else:
            result_text = self.result_font.render("Game Over", True, (255, 255, 255))

        result_rect = result_text.get_rect(center=(box_width // 2, box_height // 3))
        options_text = self.option_font.render("Play again? Y / N", True, (255, 255, 255))
        options_rect = options_text.get_rect(center=(box_width // 2, 2 * box_height // 3))
        box_surface.blit(result_text, result_rect)
        box_surface.blit(options_text, options_rect)
        border_rect = box_surface.get_rect()
        pygame.draw.rect(box_surface, (255, 215, 0), border_rect, width=1, border_radius=20)
        self.surface.blit(box_surface, (box_x, box_y))

    def font(self, size) -> pygame.font.Font:
        size = size / get_screen_size()[0]
        return pygame.font.Font(None, round(2 * size * self.minimal_scalar))

    def end(self):
        self.screen_texture.write(self.surface.get_view("1"))
        self.screen_texture.use(0)
        self.set_uniform("texture0", 0)
        self.vao.render(moderngl.TRIANGLE_STRIP)
        pygame.display.flip()
        self.last_time = self.current_time
        self.clock.tick(60)
        self.frame_count += 1

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle all the events relevant to the renderer.

        :return: True if the event was consumed, False otherwise
        """
        if event.type == pygame.VIDEORESIZE:
            screen_size = event.size
            self.screen = pygame.display.set_mode(screen_size, PYGAME_MODE_FLAGS)
            self.surface = pygame.Surface(screen_size, flags=pygame.SRCALPHA)
            self.screen_texture = self.ctx.texture(screen_size, 4)
        return False

    @property
    def size(self) -> np.ndarray[(2,)]:
        return np.array([self.surface.get_width(), self.surface.get_height()])

    @property
    def minimal_scalar(self) -> np.float32:
        return min(self.surface.get_width(), self.surface.get_height())

    def project(self, coordinates: Tuple[int, int]) -> np.ndarray[(2,)]:
        return np.array(list(coordinates)) * self.size

    def unproject(self, coordinates: np.ndarray[(2,)]) -> np.ndarray[(2,)]:
        return np.array(list(coordinates)) / self.size
