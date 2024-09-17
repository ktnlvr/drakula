import dotenv
import pygame

from datetime import datetime

from .character import Character
from .db import Database, GameDatabaseFacade, create_database_facade
from .game import MapScene
from .renderer import Renderer
from .state import GameState

GRAPH_PRUNE_LEN = 10

def should_wrap_coordinate(a: float, b: float, span: float) -> bool:
    signed_distance = b - a
    wrapped_signed_distance = span - signed_distance
    return abs(wrapped_signed_distance) < abs(signed_distance)

def main(*args, **kwargs):
    game = create_database_facade()

    airports = list()
    for continent in game._continents:
        airports.extend(game.fetch_random_airports(4, continent))

    state = GameState(airports)

    pygame.init()
    pygame.display.set_caption("Dracula")
    icon = pygame.image.load("./vampire.png")
    pygame.display.set_icon(icon)

    screen_info = pygame.display.Info()
    display_size = (int(screen_info.current_w * 0.9), int(screen_info.current_h * 0.9))
    renderer = Renderer(display_size)

    scene = MapScene(state)
    character = Character(airports[0])

    running = True
    while running:
        renderer.begin()

        scene = scene.next_scene
        scene.render(renderer)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            character.handle_input(event, airports)
            if renderer.handle_event(event):
                continue
            if scene.handle_event(renderer, event):
                continue

        scene.update(state, character)
        character.render(renderer, airports)

        renderer.end()

    pygame.quit()

    pygame.quit()

if __name__ == '__main__':
    dotenv.load_dotenv()
    main()