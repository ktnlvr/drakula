import dotenv
from pprint import pprint

from drakula.db import Database, Airport, GameDatabaseFacade
import pygame

if __name__ == '__main__':
    dotenv.load_dotenv()
    db = Database()
    game = GameDatabaseFacade(db)
    airports = game.fetch_random_airports(5, "OC")
    pprint(airports)

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
        pygame.display.update()