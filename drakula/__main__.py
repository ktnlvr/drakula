import datetime
from logging import basicConfig as config_logging, INFO

import dotenv
import pygame

from .character import Character
from .db import create_database_facade
from .debug import DEBUG_LAYER_TIMESKIP, is_debug_layer_enabled
from .debug import debug_layers
from .game import MapScene
from .logging import logger
from .renderer import Renderer
from .state import GameState


def main(*args, **kwargs):
    logger.info("Setting up the database")

    game = create_database_facade()

    logger.info("Fetching airports")
    airports = list()
    for continent in game._continents:
        airports.extend(game.fetch_random_airports(4, continent))
    logger.info(f"Got {len(airports)} airports")

    state = GameState(airports)

    renderer = Renderer((1280, 644))

    pygame.init()

    scene = MapScene(state)

    character = Character(airports[0])
    clock = pygame.time.Clock()

    running = True
    while running:
        renderer.begin()

        scene = scene.next_scene
        scene.render(renderer)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if is_debug_layer_enabled(DEBUG_LAYER_TIMESKIP):
                if pygame.key.get_pressed()[pygame.K_SPACE]:
                    state.timestamp += datetime.timedelta(hours=1, minutes=1, days=21)
                    print(state.timestamp)

            character.handle_input(event, airports)
            if renderer.handle_event(event):
                continue
            if scene.handle_event(renderer, event):
                continue

        scene.update(state, character)
        character.render(renderer, airports)

        clock.tick(30)

        renderer.end()

    pygame.quit()


if __name__ == "__main__":
    dotenv.load_dotenv()
    config_logging(level=INFO)
    if layers := debug_layers():
        logger.info(
            f"{len(layers)} debug layers enabled: {', '.join((layer.lower() for layer in layers))}"
        )
    main()
