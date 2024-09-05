from math import pi, tau

import dotenv
import pygame
import numpy as np

from .db import Database, GameDatabaseFacade
from .state import GameState
from .maths import angles_to_world_pos, solar_terminator_rad
from .renderer import Renderer

GRAPH_PRUNE_LEN = 10

def should_wrap_coordinate(a: float, b: float, span: float) -> bool:
    signed_distance = b - a
    wrapped_signed_distance = span - signed_distance
    return abs(wrapped_signed_distance) < abs(signed_distance)

def main(*args, **kwargs):
    db = Database()
    game = GameDatabaseFacade(db)

    airports = list()
    for continent in game.continents:
        airports.extend(game.fetch_random_airports(4, continent))

    state = GameState(airports)

    renderer = Renderer((1280, 644))

    pygame.init()
    map = pygame.image.load("map.jpg")

    running = True
    while running:
        renderer.begin()
        renderer.blit(map, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for i, js in state.graph.items():
            airport = airports[i]
            a = angles_to_world_pos(*airport.position)
            for j in js:
                connection = airports[j]
                b = angles_to_world_pos(*connection.position)

                # because of the signed distance, the calculations are different for case b[0] > a[0]
                # TODO: figure out the case for b[0] > a[0]
                # until then this logic allows deduping the lines from A->B and B->A
                # AND avoiding handling wrapping around the right edge of the map
                if b[0] < a[0]:
                    continue

                if should_wrap_coordinate(a[0], b[0], 1):
                    renderer.draw_line((255, 200, 0), (a[0], a[1]), (b[0] - 1, b[1]))
                    renderer.draw_line((255, 200, 0), (b[0], b[1]), (a[0] + 1, a[1]))
                else:
                    renderer.draw_line((0, 255, 0), a, b)

        N = 100
        gamma = 0.1
        for i in range(N + 1):
            px = (solar_terminator_rad(tau * (state.day_percentage + i / N), gamma) / (pi / 4) + 1) / 2
            renderer.draw_circle((255, 0, 0), ((i / N), px), .01)

        for airport in airports:
            p = angles_to_world_pos(airport.latitude_deg, airport.longitude_deg)
            renderer.draw_circle((255, 0, 0), p, .01)

        renderer.end()

if __name__ == '__main__':
    dotenv.load_dotenv()
    main()
