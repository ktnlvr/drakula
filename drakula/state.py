import datetime
from collections import defaultdict
from enum import Enum
import numpy as np
from geopy.distance import distance

from .maths import geodesic_to_3d_pos, delaunay_triangulate_points, x_y_to_geo_pos_deg
from .models import Airport
from .utils import pairs
from .logging import logger


class AirportStatus(Enum):
    AVAILABLE = 1
    DESTROYED = 2
    TRAPPED = 3


class AirportState:
    def __init__(self, airport, status):
        self.airport = airport
        self.status = status
        self.timer = 0


def disperse_airports_inplace(airports: list[Airport], dt=0.2, iters=16):
    graph = graph_from_airports(airports)
    forces = np.array([[0.0, 0.0] for _ in airports])

    def q(idx):
        return np.log2(len(graph[idx]))

    for _ in range(iters):
        k = 0.04
        for i, a in enumerate(airports):
            q1 = q(i)
            for j, b in enumerate(airports):
                if i == j:
                    continue

                q2 = q(j)

                r = distance(a.geo_position, b.geo_position).miles
                assert r != 0

                f = k * q1 * q2 / r**2
                magnitude = (f / q1) * (dt**2 / 2)
                if np.isclose(magnitude, 0):
                    magnitude = 0.1

                displacement = (
                        magnitude
                        * (v := a.screen_position - b.screen_position)
                        / np.linalg.norm(v)
                )
                lat, lon = x_y_to_geo_pos_deg(*displacement)

                # naive force, wouldn't work like that
                forces[i][0] += lat
                forces[i][1] += lon

    for (lat, lon), airport in zip(forces, airports):
        airport.latitude_deg += lat
        airport.longitude_deg += lon
        airport.correct_geo_position()


def graph_from_airports(airports):
    points = []
    for airport in airports:
        point = geodesic_to_3d_pos(*airport.geo_position, airport.elevation_ft)
        points.append(point)
    points = np.array(points)

    hull = delaunay_triangulate_points(points)

    graph = defaultdict(set)
    for simplex in hull:
        for i, j in pairs(simplex):
            graph[i].add(j)
            graph[j].add(i)

    ret_graph: dict[int, list[int]] = {}
    for vert in graph:
        ret_graph[vert] = list(graph[vert])

    return ret_graph


class GameState:
    def __init__(
        self,
        airports: list[Airport],
        player_start_location: int,
    ):
        # copy the values to prevent accidental mutations
        self.states = [
            AirportState(airport, AirportStatus.AVAILABLE) for airport in airports
        ]
        self.airports = airports.copy()

        self.graph = graph_from_airports(self.airports)

        # TODO: refactor me
        min_degree_of_separation = 3
        banned_vertices = [player_start_location]
        for i in range(min_degree_of_separation - 1):
            new_banned = []
            for v in banned_vertices:
                for neighbour in self.graph[v]:
                    new_banned.append(neighbour)
            banned_vertices.extend(new_banned)

        vertices = set(range(len(self.airports)))
        for v in banned_vertices:
            if v in vertices:
                vertices.remove(v)
        assert len(vertices) != 0
        self.dracula_location = np.random.choice(list(vertices), 1)[0]
        self.dracula_trail = [self.dracula_location]
        self.destroyed_airports = set(self.dracula_trail)

    def get_index(self, icao):
        for i in range(len(self.airports)):
            if icao == self.airports[i].ident:
                return i
        return -1

    def trap_location(self, index):
        if (
            self.states[index].status != AirportStatus.TRAPPED
            and self.states[index].status != AirportStatus.DESTROYED
        ):
            self.states[index].status = AirportStatus.TRAPPED

    def tick_trap_timer(self, character):
        for state in self.states:
            if state.status == AirportStatus.TRAPPED:
                logger.info(
                    f"Ticking trap for airport {state.airport.ident}, {state.timer} turns left"
                )
                state.timer = state.timer + 1
                if state.timer > 3:
                    state.status = AirportStatus.AVAILABLE
                    character.trap_count += 1
                    state.timer = 0

    def dracula_on_trap(self):
        return self.states[self.dracula_location].status == AirportStatus.TRAPPED

    def is_dracula_near_trap(self) -> bool:
        for vert in self.graph[self.dracula_location]:
            if self.states[vert].status == AirportStatus.TRAPPED:
                return True
        return False
