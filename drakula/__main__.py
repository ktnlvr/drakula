import dotenv
from pprint import pprint

from drakula.db import Database, Airport, GameDatabaseFacade
import pygame

from drakula.maths import angles_to_world_pos

if __name__ == '__main__':
    dotenv.load_dotenv()
    db = Database()
    game = GameDatabaseFacade(db)
    airports = game.fetch_random_airports(5, "OC")

    pygame.init()
    screen = pygame.display.set_mode((1280, 644))
    map = pygame.image.load("map.jpg")

    running = True
    while running:
        screen.fill((255, 255, 255))
        screen.blit(map,(0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for airport in airports:
            p = angles_to_world_pos(airport.latitude_deg, airport.longitude_deg)
            print(p)
            px = p[0] * 1280
            py = p[1] * 644
            pygame.draw.circle(screen, (255, 0, 0), [px, py], 2.)
        pygame.display.update()