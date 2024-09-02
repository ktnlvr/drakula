import dotenv
import pygame
import numpy as np

from drakula.db import Database, GameDatabaseFacade
from drakula.utils import pairs
from drakula.maths import angles_to_world_pos, geodesic_to_3d_pos, points_to_hull

if __name__ == '__main__':
    dotenv.load_dotenv()
    db = Database()
    game = GameDatabaseFacade(db)

    airports = list()
    for continent in game.continents:
        airports.extend(game.fetch_random_airports(1, continent))

    points = np.array([geodesic_to_3d_pos(airport.latitude_deg, airport.longitude_deg, airport.elevation_ft) for airport in airports])
    hull = points_to_hull(points)
    screen_size = np.array([1280, 644])

    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    map = pygame.image.load("map.jpg")
    pygame.display.set_caption("Dracula")
    icon = pygame.image.load("./vampire.png")
    pygame.display.set_icon(icon)
    mapx = 0
    mapy = 0
    offset_x = 0
    running = True
    while running:
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    mapx += 100
                if event.key == pygame.K_RIGHT:
                    mapx -= 100
        offset_x = mapx % 1280
        screen.blit(map, (offset_x, mapy))
        if offset_x > 0:
            screen.blit(map, (offset_x - 1280,mapy))
        if offset_x < 0:
            screen.blit(map, (offset_x + 1280, mapy))
        for simplex in hull:
            p = np.array([screen_size * angles_to_world_pos(airports[i].latitude_deg, airports[i].longitude_deg) for i in simplex])
            p[:,0] += mapx
            p[:,1] += mapy
            for a, b in pairs(p):
                pygame.draw.line(screen, (0, 255, 0), a, b, 1)

        for airport in airports:
            p = angles_to_world_pos(airport.latitude_deg , airport.longitude_deg)
            p *= screen_size
            p[0] += mapx
            p[1] += mapy
            pygame.draw.circle(screen, (255, 0, 0), p, 5.)
        pygame.display.update()