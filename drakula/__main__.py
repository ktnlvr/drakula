import dotenv
import pygame

from drakula.db import Database, GameDatabaseFacade
from drakula.maths import angles_to_world_pos

if __name__ == '__main__':
    dotenv.load_dotenv()
    db = Database()
    game = GameDatabaseFacade(db)

    airports = []
    for continent in game.continents:
        airports.extend(game.fetch_random_airports(10, continent))

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
            p *= [1280, 644]
            pygame.draw.circle(screen, (255, 0, 0), p, 5.)
        pygame.display.update()
