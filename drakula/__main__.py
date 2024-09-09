import dotenv
import pygame

from .game import MapScene
from .db import Database, GameDatabaseFacade
from .state import GameState
from .renderer import Renderer
from .character import Character


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

    character = Character(airports[0])  # start at the first airport
    clock = pygame.time.Clock()

    pygame.init()

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
            if scene.handle_event(renderer, event):
                continue

        scene = scene.next_scene

        scene.update(state, character)
        scene.render(state, renderer)
        character.render(renderer, airports)

        clock.tick(30)

        renderer.end()

    pygame.quit()


if __name__ == "__main__":
    dotenv.load_dotenv()
    main()
