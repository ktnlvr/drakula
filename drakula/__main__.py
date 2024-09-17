import dotenv
import pygame

from .character import Character
from .db import create_database_facade
from .game import MapScene
from .renderer import Renderer
from .state import GameState


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

    renderer = Renderer()

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


if __name__ == '__main__':
    dotenv.load_dotenv()
    main()
