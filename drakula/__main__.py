import dotenv
import pygame
from numpy.random import choice
from pygame.time import Clock

from .character import Character, CharacterInputResult
from .db import Database, GameDatabaseFacade
from .dracula import DraculaBrain
from .game import MapScene
from .renderer import Renderer
from .scene import Scene
from .state import GameState


def main(*args, **kwargs):
    db = Database()
    game = GameDatabaseFacade(db)

    airports = list()
    for continent in game.continents:
        airports.extend(game.fetch_random_airports(4, continent))

    state = GameState(airports)

    renderer = Renderer((1280, 644))

    pygame.init()
    pygame.display.set_caption("The Hunt for Dracula")
    icon = pygame.image.load("vampire.png")
    pygame.display.set_icon(icon)

    character = Character(0)
    scene: Scene = MapScene(state, character)

    brain = DraculaBrain()

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

        scene.render(renderer)
        renderer.end()

        pygame.display.flip()
        clock.tick(30)  # Limit frame

        renderer.end()

    pygame.quit()


if __name__ == "__main__":
    dotenv.load_dotenv()
    main()
