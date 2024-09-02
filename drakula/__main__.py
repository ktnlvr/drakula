import dotenv
import pygame
import numpy as np
from array import array
import moderngl

from drakula.db import Database, GameDatabaseFacade
from drakula.utils import pairs
from drakula.maths import angles_to_world_pos, geodesic_to_3d_pos, points_to_hull

if __name__ == '__main__':
    dotenv.load_dotenv()
    db = Database()
    game = GameDatabaseFacade(db)

    airports = list()
    for continent in game.continents:
        airports.extend(game.fetch_random_airports(1, continent))

    points = np.array([geodesic_to_3d_pos(airport.latitude_deg, airport.longitude_deg, airport.elevation_ft) for airport in airports])
    hull = points_to_hull(points)
    screen_size = np.array([1280, 644])

    pygame.init()
    screen = pygame.display.set_mode(screen_size, pygame.OPENGL | pygame.DOUBLEBUF)
    ctx= moderngl.create_context()
    clock = pygame.time.Clock()

    map = pygame.image.load("mapv2.png")

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
        screen.fill((255, 255, 255))
        screen.blit(map, (0, 0))

        t += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        for simplex in hull:
            p = np.array([screen_size * angles_to_world_pos(airports[i].latitude_deg, airports[i].longitude_deg) for i in simplex])
            for a, b in pairs(p):
                pygame.draw.line(screen, (0, 255, 0), a, b, 1)

        for airport in airports:
            p = angles_to_world_pos(airport.latitude_deg, airport.longitude_deg)
            p *= screen_size
            pygame.draw.circle(screen, (255, 0, 0), p, 5.)

        frame_tex = surf_to_texture(screen)
        frame_tex.use(0)
        program['tex'] = 0
        program['time'] = t
        render_object.render(mode=moderngl.TRIANGLE_STRIP)

        pygame.display.flip()

        frame_tex.release()

        clock.tick(60)
