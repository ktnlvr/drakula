from numpy.random import choice

import dotenv
import pygame

from .maths import angles_to_world_pos
from .dracula import DraculaBrain
from .game import MapScene
from .db import Database, GameDatabaseFacade
from .state import GameState
from .renderer import Renderer
from . import Character, airport_icao
from pygame.time import Clock

GRAPH_PRUNE_LEN = 10

def main(*args, **kwargs):
    db = Database()
    game = GameDatabaseFacade(db)
    moves = 0
    airports = list()
    for continent in game.continents:
        airports.extend(game.fetch_random_airports(4, continent))

    state = GameState(airports)

    renderer = Renderer((1280, 644))

    pygame.init()

    scene = MapScene(state)

    brain = DraculaBrain()
    current_dracula_pos = 0
    trail = [current_dracula_pos]

    character = Character(airports[0])#start at the first airport
    clock = Clock()

    running = True
    while running:
        renderer.begin()
        scene.render(state, renderer)
        moves = brain.list_moves(state, current_dracula_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if character.handle_input(event, airports):
                state.add_timer_for_traps()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    new_pos = choice([x for _, x in moves], 1, p=[p for p, _ in moves])[0]
                    current_dracula_pos = new_pos
                    trail.append(current_dracula_pos)
                if event.key == pygame.K_KP_ENTER:
                    state.trap_current_location(state.get_index(character.current_airport.ident))
            if renderer.handle_event(event):
                continue
            if scene.handle_event(event):
                continue

        for i in range(len(trail) - 1):
            a, b = [angles_to_world_pos(*p) for p in [airports[trail[i]].position, airports[trail[i + 1]].position]]
            renderer.draw_line_wrapping((100, 100, 255, 100), a, b, 0.01)

        renderer.draw_circle((0, 0, 255), angles_to_world_pos(*airports[current_dracula_pos].position), 0.015)
        for c, i in moves:
            p = c / max([c for c, _ in moves])
            renderer.draw_circle((150, 150, 255), angles_to_world_pos(*airports[i].position), 0.01 * p)
        scene = scene.next_scene

        scene.update(state, character) #Updates current pos
        scene.render(state, renderer)
        character.render(renderer, airports)
        renderer.end()

        pygame.display.flip()
        clock.tick(30)  # Limit frame

        renderer.end()

    pygame.quit()

if __name__ == '__main__':
    dotenv.load_dotenv()
    main()
