import dotenv
import pygame
from numpy.random import choice
from logging import basicConfig as init_basic_logging

from .debug import is_debug_layer_enabled, DEBUG_LAYER_STRESSTEST
from .logging import logger
from .db import create_database_facade
from .character import Character, CharacterInputResult
from .dracula import DraculaBrain
from .game import MapScene
from .renderer import Renderer
from .scene import Scene
from .state import GameState, disperse_airports_inplace

AIRPORT_DISPERSION_STEPS = 32


def main(*args, **kwargs):
    game = create_database_facade()

    airports = list()
    for continent in game._continents:
        airports.extend(game.fetch_random_airports(4, continent))

    logger.info("Dispersing airports...")
    for _ in range(AIRPORT_DISPERSION_STEPS):
        disperse_airports_inplace(airports, 1 / AIRPORT_DISPERSION_STEPS)
    logger.info("Airport dispersion done!")

    renderer = Renderer((1280, 644))

    pygame.display.set_caption("The Hunt for Dracula")
    icon = pygame.image.load("vampire.png")
    pygame.display.set_icon(icon)

    character = Character(0)
    state = GameState(airports, character.current_location)
    scene: Scene = MapScene(state, character)

    brain = DraculaBrain()

    running = True
    while running:
        renderer.begin()

        scene = scene.next_scene
        scene.render(renderer)

        moves = brain.list_moves(state, state.dracula_location)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if result := character.handle_input(event, state, scene):
                if result == CharacterInputResult.Moved:
                    state.add_timer_for_traps(character)
                    # TODO: make this less confusing
                    if not state.dracula_on_trap():
                        state.dracula_location = choice(
                            [x for _, x in moves], 1, p=[p for p, _ in moves]
                        )[0]
                        state.dracula_trail += [state.dracula_location]
                continue
            character.handle_input(event, state, scene)
            if renderer.handle_event(event):
                continue
            if scene.handle_event(event):
                continue

        scene = scene.next_scene
        renderer.end()

    pygame.quit()


def stresstest_main(n):
    for i in range(n):
        pygame.init()
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        main()
        print(f"Stresstest {i}: {round(i / N, 2)}")
    print("Done! 100%")


if __name__ == "__main__":
    # set up environment
    dotenv.load_dotenv()
    pygame.init()
    init_basic_logging()

    if is_debug_layer_enabled(DEBUG_LAYER_STRESSTEST):
        N = 2**8
        stresstest_main(N)
        exit()

    main()
