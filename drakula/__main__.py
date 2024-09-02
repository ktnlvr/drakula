from collections import defaultdict

import dotenv
import pygame
import numpy as np

from drakula.db import Database, GameDatabaseFacade
from drakula.state import GameState
from drakula.utils import pairs
from drakula.maths import angles_to_world_pos, geodesic_to_3d_pos, delaunay_triangulate_points

GRAPH_PRUNE_LEN = 10

def should_wrap_coordinate(a: float, b: float, span: float) -> bool:
    signed_distance = b - a
    wrapped_signed_distance = span - signed_distance
    return abs(wrapped_signed_distance) < abs(signed_distance)

def main(*args, **kwargs):
    dotenv.load_dotenv()
    db = Database()
    game = GameDatabaseFacade(db)

    airports = list()
    for continent in game.continents:
        airports.extend(game.fetch_random_airports(4, continent))

    state = GameState(airports)

    screen_size = np.array([1280, 644])

    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    map = pygame.image.load("map.jpg")

    running = True
    while running:
        screen.fill((255, 255, 255))
        screen.blit(map,(0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for i, js in state.graph.items():
            airport = airports[i]
            a = screen_size * angles_to_world_pos(*airport.position)
            for j in js:
                connection = airports[j]
                b = screen_size * angles_to_world_pos(*connection.position)

                # because of the signed distance, the calculations are different for case b[0] > a[0]
                # TODO: figure out the case for b[0] > a[0]
                # until then this logic allows deduping the lines from A->B and B->A
                # AND avoiding handling wrapping around the right edge of the map
                if b[0] < a[0]:
                    continue

                if should_wrap_coordinate(a[0], b[0], screen_size[0]):
                    pygame.draw.line(screen, (255, 200, 0), (a[0], a[1]), (-screen_size[0] + b[0], b[1]), 1)
                    pygame.draw.line(screen, (255, 200, 0), (b[0], b[1]), (screen_size[0] + a[0], a[1]), 1)
                else:
                    pygame.draw.line(screen, (0, 255, 0), a, b, 1)

        for airport in airports:
            p = angles_to_world_pos(airport.latitude_deg, airport.longitude_deg)
            p *= screen_size
            pygame.draw.circle(screen, (255, 0, 0), p, 5.)
        pygame.display.update()

if __name__ == '__main__':
    main()
