from typing import Tuple
import numpy as np
import pygame

Coordinate = Tuple[float, float]

class Renderer:
    def __init__(self, screen_size: Tuple[int, int]):
        self.surface = pygame.display.set_mode(screen_size)

    def blit(self, source: pygame.Surface, at: Coordinate):
        self.surface.blit(source, self.project(at))

    def begin(self):
        self.surface.fill((255, 0, 255))
    
    def draw_line(self, color: pygame.Color, begin: Coordinate, end: Coordinate, width: float = 0):
        pygame.draw.line(self.surface, color, self.project(begin), self.project(end), int(max(width * self.minimal_scalar, 1)))
    
    def draw_line_wrapping(self, color: pygame.Color, begin: Coordinate, end: Coordinate, width: float = 0, wrap_around: float = 1.):
        a, b = begin, end
        
        if b[0] < a[0]:
            a, b = b, a

        def should_wrap_coordinate(a: float, b: float, span: float) -> bool:
            signed_distance = b - a
            wrapped_signed_distance = span - signed_distance
            return abs(wrapped_signed_distance) < abs(signed_distance)

        if should_wrap_coordinate(a[0], b[0], wrap_around):
            self.draw_line(color, (a[0], a[1]), (b[0] - wrap_around, b[1]), width)
            self.draw_line(color, (b[0], b[1]), (a[0] + wrap_around, a[1]), width)
        else:
            self.draw_line(color, begin, end, width)

    def draw_circle(self, color: pygame.Color, at: Coordinate, radius: float):
        pygame.draw.circle(self.surface, color, self.project(at), radius * self.minimal_scalar)

    def end(self):
        pygame.display.update()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle all the events relevant to the renderer.

        :return: False if the event was not handled, True otherwise
        """
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
