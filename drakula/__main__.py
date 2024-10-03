import dotenv
import pygame
from numpy.random import choice

from .db import create_database_facade
from .character import Character, CharacterInputResult
from .dracula import DraculaBrain
from .game import MapScene
from .renderer import Renderer
from .scene import Scene
from .state import GameState


def main(*args, **kwargs):
    pygame.init()
    game = create_database_facade()

    airports = list()
    for continent in game._continents:
        airports.extend(game.fetch_random_airports(4, continent))

    state = GameState(airports)

    renderer = Renderer((1280, 644))

    pygame.display.set_caption("The Hunt for Dracula")
    icon = pygame.image.load("vampire.png")
    pygame.display.set_icon(icon)

    character = Character(8)
    dracula = DraculaBrain()
    scene: Scene = MapScene(state, character)

    running = True
    game_over = False
    result = None
    while running:
        renderer.begin()

        scene = scene.next_scene
        scene.render(renderer)

        #just for testing
        dracula_location = state.dracula_location
        dracula_icao = state.airports[dracula_location].ident
        renderer.display_dracula_location(dracula_icao)

        renderer.display_destroyed_airports(state.destroyed_airports)
        idx = state.get_index(character.input_text)

        if game_over:
            renderer.display_result(result)
            renderer.begin()

            scene.render(renderer)
            renderer.display_result(result)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        game_over = False
                        break
                    elif event.key == pygame.K_n or event.key == pygame.K_q:
                        running = False

        if not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                character_input = character.handle_input(event, state)
                if character_input == CharacterInputResult.Moved:

                    if idx == dracula_location:
                        result = "Win"
                        game_over = True
                        break

                    state.add_timer_for_traps()

                    dracula_next_move = choice(
                        [x for _, x in dracula.list_moves(state, state.dracula_location)],
                        1,
                        p=[p for p, _ in dracula.list_moves(state, state.dracula_location)]
                    )[0]

                    if dracula_next_move != state.dracula_location:
                        state.dracula_location = dracula_next_move
                        state.dracula_trail.append(state.dracula_location)
                        state.destroyed_airports.add(dracula_icao)

                if state.destroyed_airports_count / len(state.airports) >= 0.5:
                    result = "Lose"
                    game_over = True
                    break

        renderer.end()

    pygame.quit()


if __name__ == "__main__":
    dotenv.load_dotenv()
    main()
