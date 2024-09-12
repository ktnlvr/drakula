import dotenv
import pygame
from numpy.random import choice
from pygame.time import Clock

from drakula.scene import Scene
from . import Character, CharacterInputResult
from .db import Database, GameDatabaseFacade
from .dracula import DraculaBrain
from .game import MapScene
from .renderer import Renderer
from .state import GameState

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

    scene: Scene = MapScene(state)

    brain = DraculaBrain()

    character = Character(airports[0])
    clock = Clock()

    running = True
    while running:
        renderer.begin()
        scene.render(renderer)

        moves = brain.list_moves(state, state.dracula_location)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if result := character.handle_input(event, state):
                if result == CharacterInputResult.Moved:
                    state.add_timer_for_traps()
                    # TODO: make this less confusing
                    state.dracula_location = choice(
                        [x for _, x in moves], 1, p=[p for p, _ in moves]
                    )[0]
                    state.dracula_trail += [state.dracula_location]
                continue
            if renderer.handle_event(event):
                continue
            if scene.handle_event(event):
                continue

        scene = scene.next_scene()

        scene.update(state, character)  # Updates current pos
        scene.render(renderer)
        character.render(renderer, airports)
        renderer.end()

        pygame.display.flip()
        clock.tick(30)  # Limit frame

        renderer.end()

    pygame.quit()


if __name__ == "__main__":
    dotenv.load_dotenv()
    main()
