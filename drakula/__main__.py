import datetime
from math import pi, tau

import dotenv
import pygame

from .debug import DEBUG_LAYER_TIMESKIP, is_debug_layer_enabled
from .game import MapScene
from .db import Database, GameDatabaseFacade
from .state import GameState
from .renderer import Renderer

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

    scene = MapScene(state)

    running = True
    while running:
        renderer.begin()
        scene.render(renderer)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if is_debug_layer_enabled(DEBUG_LAYER_TIMESKIP):
                if pygame.key.get_pressed()[pygame.K_SPACE]:
                    state.timestamp += datetime.timedelta(hours=1, minutes=1, days=21)
                    print(state.timestamp)

            if renderer.handle_event(event):
                continue
            if scene.handle_event(event):
                continue

        renderer.end()
        scene = scene.next_scene


if __name__ == '__main__':
    dotenv.load_dotenv()
    main()
