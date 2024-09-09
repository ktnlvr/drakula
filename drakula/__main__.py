from logging import basicConfig as config_logging, INFO

import dotenv
import pygame

from .game import MapScene
from .debug import debug_layers
from .db import Database, GameDatabaseFacade
from .state import GameState
from .renderer import Renderer
from .logging import logger


def main(*args, **kwargs):
    logger.info("Setting up the database")

    db = Database()
    game = GameDatabaseFacade(db)

    logger.info("Fetching airports")
    airports = list()
    for continent in game.continents:
        airports.extend(game.fetch_random_airports(4, continent))
    logger.info(f"Got {len(airports)} airports")

    state = GameState(airports)

    renderer = Renderer((1280, 644))

    pygame.init()

    scene = MapScene()

    running = True
    while running:
        renderer.begin()
        scene.render(state, renderer)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if renderer.handle_event(event):
                continue
            if scene.handle_event(event):
                continue

        renderer.end()
        scene = scene.next_scene


if __name__ == "__main__":
    dotenv.load_dotenv()
    config_logging(level=INFO)
    if layers := debug_layers():
        logger.info(f"{len(layers)} debug layers enabled: {', '.join((layer.lower() for layer in layers))}")
    main()
