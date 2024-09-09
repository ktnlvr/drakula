from math import pi, tau

import dotenv
import pygame

from .game import MapScene
from .db import Database, GameDatabaseFacade
from .state import GameState
from .renderer import Renderer
from . import Character, airport_icao
from pygame.time import Clock

GRAPH_PRUNE_LEN = 10

def main(*args, **kwargs):
    db = Database()
    game = GameDatabaseFacade(db)

    airports = list()
    for continent in game.continents:
        airports.extend(game.fetch_random_airports(4, continent))

    state = GameState(airports)

    renderer = Renderer((1280, 644))

    pygame.init()

    scene = MapScene()

    character = Character(airports[0])#start at the first airport
    clock = Clock()

    running = True
    while running:
        renderer.begin()
        scene.render(state, renderer)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            character.handle_input(event, airports)
            if renderer.handle_event(event):
                continue
            if scene.handle_event(event):
                continue

        scene = scene.next_scene

        scene.update(state, character)  # Update
        renderer.begin()
        scene.render(state, renderer)
        character.render(renderer, airports)
        renderer.end()

        pygame.display.flip()
        clock.tick(30)  # Limit frame

        renderer.end()

    pygame.quit()

if __name__ == '__main__':
    dotenv.load_dotenv()
    main()
