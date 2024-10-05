import dotenv
import pygame
from numpy.random import choice, randint
from logging import basicConfig as init_basic_logging

from .debug import (
    is_debug_layer_enabled,
    DEBUG_LAYER_STRESSTEST,
    DEBUG_LAYER_LOG_VERBOSE,
)
from .logging import logger
from .db import create_database_facade
from .character import Character, CharacterInputResult
from .dracula import DraculaBrain
from .game import MapScene, GameOverScene, GameOverKind
from .renderer import Renderer
from .scene import Scene
from .state import GameState, disperse_airports_inplace, AirportStatus

AIRPORT_DISPERSION_STEPS = 1
WINDOW_TITLE = "The Hunt for Dracula"
WINDOW_TITLE_TEMPLATE = WINDOW_TITLE + " - {percent}% destroyed"


def main(*args, **kwargs):
    game = create_database_facade()

    airports = list()
    for continent in game._continents:
        airports.extend(game.fetch_random_airports(4, continent))

    logger.info("Dispersing airports...")
    for _ in range(AIRPORT_DISPERSION_STEPS):
        disperse_airports_inplace(airports)
    logger.info("Airport dispersion done!")

    renderer = Renderer((1280, 644))

    pygame.display.set_caption(WINDOW_TITLE)
    icon = pygame.image.load("vampire.png")
    pygame.display.set_icon(icon)

    character = Character(randint(len(airports)))
    state = GameState(airports, character.current_location)
    logger.info(f"Dracula starts at {state.airports[state.dracula_location].ident}!")
    scene: Scene = MapScene(state, character)

    brain = DraculaBrain()

    running = True
    while running:
        renderer.begin()

        scene.render(renderer)

        moves = brain.list_moves(state, state.dracula_location)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if scene.handle_event(event):
                continue
            if result := character.handle_input(event, state, scene):
                if result == CharacterInputResult.Moved:
                    if state.dracula_location == character.current_location:
                        scene = GameOverScene(scene, GameOverKind.WIN)
                        continue

                    state.tick_trap_timer(character)
                    # TODO: make this less confusing
                    state.states[state.dracula_location].status = AirportStatus.DESTROYED

                    prev_drakula_location = state.dracula_location
                    state.states[state.dracula_location].status = AirportStatus.DESTROYED
                    state.destroyed_airports.add(state.dracula_location)

                    state.dracula_location = choice(
                        [x for _, x in moves], 1, p=[p for p, _ in moves]
                    )[0]

                    logger.info(
                        f"Dracula moves from {state.airports[prev_drakula_location].ident} to {state.airports[state.dracula_location].ident}"
                    )

                    if state.dracula_location == character.current_location:
                        scene = GameOverScene(scene, GameOverKind.LOSS_CAUGHT)
                        continue

                    percent_of_world_destroyed = round(100 * len(state.destroyed_airports) / len(state.airports))
                    pygame.display.set_caption(WINDOW_TITLE_TEMPLATE.format(percent=percent_of_world_destroyed))

                    if percent_of_world_destroyed > 50:
                        scene = GameOverScene(scene, GameOverKind.LOSS_DESTROYED)
                        continue

            if renderer.handle_event(event):
                continue

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

    if is_debug_layer_enabled(DEBUG_LAYER_LOG_VERBOSE):
        from logging import DEBUG

        logger.setLevel(DEBUG)

    if is_debug_layer_enabled(DEBUG_LAYER_STRESSTEST):
        N = 2**8
        stresstest_main(N)
        exit()

    main()
