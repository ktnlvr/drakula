import dotenv
import pygame
import numpy as np

import moderngl
from datetime import datetime
from pygame._sdl2 import Window
from pygame import VIDEORESIZE

from drakula.db import Database, GameDatabaseFacade
from drakula.state import GameState
from drakula.utils import pairs, load_shader
from drakula.maths import angles_to_world_pos, geodesic_to_3d_pos, delaunay_triangulate_points

GRAPH_PRUNE_LEN = 10

def should_wrap_coordinate(a: float, b: float, span: float) -> bool:
    signed_distance = b - a
    wrapped_signed_distance = span - signed_distance
    return abs(wrapped_signed_distance) < abs(signed_distance)

def main(*args, **kwargs):
    dotenv.load_dotenv()
    db = Database()
    game = GameDatabaseFacade(db)

    airports = list()
    for continent in game.continents:
        airports.extend(game.fetch_random_airports(4, continent))

    state = GameState(airports)

    pygame.init()
    pygame.display.set_caption("Dracula")
    icon = pygame.image.load("./vampire.png")
    pygame.display.set_icon(icon)

    screen_info = pygame.display.Info()
    display = (int(screen_info.current_w * 0.9), int(screen_info.current_h * 0.9))
    screen = pygame.display.set_mode(display, pygame.OPENGL | pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF)
    fullscreen = False

    map = pygame.transform.scale(pygame.image.load("map.png"), display)
    mapx = 0


    ctx = moderngl.create_context()

    pygame_surface = pygame.Surface(display, flags=pygame.SRCALPHA)
    pygame_surface.blit(map, (0, 0))

    texture = ctx.texture(display, 4)

    vertex_shader = load_shader('drakula/shaders/vertex_shader.glsl')
    fragment_shader = load_shader('drakula/shaders/fragment_shader.glsl')

    program = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

    vertices = np.array([
        # x,    y,
        -1.0, -1.0,
        1.0, -1.0,
        -1.0, 1.0,
        1.0, 1.0,
    ], dtype='f4')
    vbo = ctx.buffer(vertices)
    vao = ctx.simple_vertex_array(program, vbo, 'position')


    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    last_time = start_time
    frame_count = 0


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            #if event.type == VIDEORESIZE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    mapx += 100
                if event.key == pygame.K_RIGHT:
                    mapx -= 100
                if event.key == pygame.K_1:
                    if fullscreen:
                        fullscreen = False
                        screen = pygame.display.set_mode(display, pygame.OPENGL | pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF)
                    else:
                        fullscreen = True
                        screen = pygame.display.set_mode(display, pygame.OPENGL | pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN)


        current_time = pygame.time.get_ticks()
        time = (current_time - start_time) / 1000.0
        delta_time = (current_time - last_time) / 1000.0
        last_time = current_time

        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        now = datetime.now()
        year, month, day = now.year, now.month, now.day
        seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

        active_uniforms = program._members
        if 'iResolution' in active_uniforms:
            program['iResolution'].value = (*display, 1.0)
        if 'iTime' in active_uniforms:
            program['iTime'].value = time
        if 'iTimeDelta' in active_uniforms:
            program['iTimeDelta'].value = delta_time
        if 'iFrame' in active_uniforms:
            program['iFrame'].value = frame_count
        if 'iMouse' in active_uniforms:
            program['iMouse'].value = (mouse_pos[0], display[1] - mouse_pos[1], mouse_buttons[0], mouse_buttons[2])
        if 'iDate' in active_uniforms:
            program['iDate'].value = (year, month, day, seconds_since_midnight)

        mapx %= display[0]

        pygame_surface.fill((0, 0, 0, 255))
        pygame_surface.blit(map, (mapx, 0))
        if mapx > 0:
            pygame_surface.blit(map, (mapx - display[0], 0))
        if mapx < 0:
            pygame_surface.blit(map, (mapx + display[0], 0))

        for i, js in state.graph.items():
            airport = airports[i]
            a = display * angles_to_world_pos(*airport.position)
            a[0] = (a[0] + mapx) % display[0]
            for j in js:
                connection = airports[j]
                b = display * angles_to_world_pos(*connection.position)
                b[0] = (b[0] + mapx) % display[0]


                # because of the signed distance, the calculations are different for case b[0] > a[0]
                # TODO: figure out the case for b[0] > a[0]
                # until then this logic allows deduping the lines from A->B and B->A
                # AND avoiding handling wrapping around the right edge of the map
                if b[0] < a[0]:
                    continue

                if should_wrap_coordinate(a[0], b[0], display[0]):
                    pygame.draw.line(pygame_surface, (255, 200, 0), (a[0], a[1]), (-display[0] + b[0], b[1]), 1)
                    pygame.draw.line(pygame_surface, (255, 200, 0), (b[0], b[1]), (display[0] + a[0], a[1]), 1)
                else:
                    pygame.draw.line(pygame_surface, (0, 255, 0), a, b, 1)

        for airport in airports:
            p = angles_to_world_pos(airport.latitude_deg, airport.longitude_deg)
            p *= display
            p[0] = (p[0] + mapx) % display[0]
            pygame.draw.circle(pygame_surface, (255, 0, 0), p, 5.)

        texture.write(pygame_surface.get_view('1'))
        ctx.clear(color=(0.0, 0.0, 0.0, 1.0))

        program['texture0'] = 0
        texture.use(0)
        program['iResolution'].value = (*display, 1.0)

        vao.render(moderngl.TRIANGLE_STRIP)
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1

    pygame.quit()
if __name__ == '__main__':
    main()