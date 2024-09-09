from collections import defaultdict

import dotenv
import pygame
from pygame import VIDEORESIZE
import numpy as np
from array import array
import moderngl
from pygame._sdl2 import Window

from drakula.db import Database, GameDatabaseFacade
from drakula.state import GameState
from drakula.utils import pairs
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

    screen_size = np.array([1920, 1080])
    # TODO: use the dimensions of the actual screen
    screen = pygame.display.set_mode((2040, 1020), pygame.OPENGL | pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF)
    Window.from_display_module().maximize()
    ctx= moderngl.create_context()
    clock = pygame.time.Clock()
    mapx = 0



    quad_buffer = ctx.buffer(data=array('f', [
        # position (x, y), uv coords (x, y)
        -1.0, 1.0, 0.0, 0.0,  # topleft
        1.0, 1.0, 1.0, 0.0,  # topright
        -1.0, -1.0, 0.0, 1.0,  # bottomleft
        1.0, -1.0, 1.0, 1.0,  # bottomright
    ]))

    vert_shader = '''
    #version 330 core

    in vec2 vert;
    in vec2 texcoord;
    out vec2 uvs;

    void main() {
        uvs = texcoord;
        gl_Position = vec4(vert, 0.0, 1.0);
    }
    '''

    frag_shader = '''
    #version 330 core

    uniform sampler2D tex;
    uniform float time;

    in vec2 uvs;
    out vec4 f_color;

    void main() {
        vec2 sample_pos = vec2(uvs.x + sin(uvs.y * 10 + time * 0.01) * 0.1, uvs.y);
        f_color = vec4(texture(tex, sample_pos).rg, texture(tex, sample_pos).b * 1.5, 1.0);
    }
    '''

    program = ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)
    render_object = ctx.vertex_array(program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])


    def surf_to_texture(surf):
        tex = ctx.texture(surf.get_size(), 4)
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        tex.swizzle = 'BGRA'
        tex.write(surf.get_view('1'))
        return tex


    t = 0

    running = True
    while running:
        map = pygame.image.load("map.png")
        screen.fill((255, 255, 255))
        screen.blit(pygame.transform.scale(map, (1920, 1080)), (0,0))

        t += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
            if event.type == VIDEORESIZE:
                screen = pygame.display.set_mode(
                    event.dict['size'], pygame.OPENGL | pygame.RESIZABLE | pygame.HWSURFACE)
                screen.blit(pygame.transform.scale(map, event.dict['size']), (0, 0))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    mapx += 100
                if event.key == pygame.K_RIGHT:
                    mapx -= 100
                if event.key == pygame.K_1:
                    Window.from_display_module().borderless = not Window.from_display_module().borderless
                if event.key == pygame.K_2:
                    Window.from_display_module().maximize()
        mapx %= screen_size[0]
        screen.blit(map, (mapx, 0))
        if mapx > 0:
            screen.blit(map, (mapx - screen_size[0], 0))
        if mapx < 0:
            screen.blit(map, (mapx + screen_size[0], 0))

        for i, js in state.graph.items():
            airport = airports[i]
            a = screen_size * angles_to_world_pos(*airport.position)
            a[0] = (a[0] + mapx) % screen_size[0]
            for j in js:
                connection = airports[j]
                b = screen_size * angles_to_world_pos(*connection.position)
                b[0] = (b[0] + mapx) % screen_size[0]


                # because of the signed distance, the calculations are different for case b[0] > a[0]
                # TODO: figure out the case for b[0] > a[0]
                # until then this logic allows deduping the lines from A->B and B->A
                # AND avoiding handling wrapping around the right edge of the map
                if b[0] < a[0]:
                    continue

                if should_wrap_coordinate(a[0], b[0], screen_size[0]):
                    pygame.draw.line(screen, (255, 200, 0), (a[0], a[1]), (-screen_size[0] + b[0], b[1]), 1)
                    pygame.draw.line(screen, (255, 200, 0), (b[0], b[1]), (screen_size[0] + a[0], a[1]), 1)
                else:
                    pygame.draw.line(screen, (0, 255, 0), a, b, 1)

        for airport in airports:
            p = angles_to_world_pos(airport.latitude_deg, airport.longitude_deg)
            p *= screen_size
            p[0] = (p[0] + mapx) % screen_size[0]
            pygame.draw.circle(screen, (255, 0, 0), p, 5.)

        frame_tex = surf_to_texture(screen)
        frame_tex.use(0)
        program['tex'] = 0
        program['time'] = t
        render_object.render(mode=moderngl.TRIANGLE_STRIP)


        pygame.display.flip()
        frame_tex.release()

        clock.tick(60)

if __name__ == '__main__':
    main()