from datetime import datetime
from typing import Tuple, Optional

import moderngl
import numpy as np
import pygame
from .utils import load_shader

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
        if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
            self.fullscreen = not self.fullscreen

            flags = PYGAME_MODE_FLAGS
            if self.fullscreen:
                flags |= pygame.FULLSCREEN
            self.fullscreen = pygame.display.set_mode(get_screen_size(), flags)
            return True
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
