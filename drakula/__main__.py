from collections import defaultdict

import dotenv
import pygame
import numpy as np
from pygame import VIDEORESIZE

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

    # TODO: use the dimensions of the actual screen
    screen_size = np.array([2040, 1020])

    pygame.init()
    screen = pygame.display.set_mode(screen_size,pygame.RESIZABLE)
    map = pygame.image.load("map.png")
    pygame.display.set_caption("Dracula")
    icon = pygame.image.load("./vampire.png")
    pygame.display.set_icon(icon)
    mapx = 0
    running = True
    while running:
        screen.fill((255, 255, 255))
        screen.blit(map, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == VIDEORESIZE:
                screen_size = (event.w,event.h)
                screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
                map = pygame.image.load("map.png")
                map = pygame.transform.scale(map,screen_size)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    mapx += 100
                if event.key == pygame.K_RIGHT:
                    mapx -= 100
        mapx %= screen_size[0]
        screen.blit(map, (mapx, 0))
        if mapx > 0:
            screen.blit(map, (mapx - screen_size[0], 0))
        if mapx < 0:
            screen.blit(map, (mapx + screen_size[0], 0))

        for i, js in state.graph.items():
            airport = airports[i]
            a = screen_size * angles_to_world_pos(*airport.position)
            a[0] = (a[0] + mapx) % screen_size[0]
            for j in js:
                connection = airports[j]
                b = screen_size * angles_to_world_pos(*connection.position)
                b[0] = (b[0] + mapx) % screen_size[0]

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
            p = angles_to_world_pos(airport.latitude_deg , airport.longitude_deg)
            p *= screen_size
            p[0] = (p[0] + mapx) % screen_size[0]
            pygame.draw.circle(screen, (255, 0, 0), p, 5.)
        pygame.display.update()

if __name__ == '__main__':
    main()
