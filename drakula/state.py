import datetime
from collections import defaultdict
from enum import Enum
import numpy as np
from geopy.distance import distance

from .maths import geodesic_to_3d_pos, delaunay_triangulate_points, x_y_to_geo_pos_deg
from .models import Airport
from .utils import pairs


class AirportStatus(Enum):
    AVAILABLE = 1
    DESTROYED = 2
    TRAPPED = 3


class AirportState:
    def __init__(self, airport, status):
        self.airport = airport
        self.status = status
        self.timer = 0


def disperse_airports_inplace(airports: list[Airport], dt=0):
    graph = graph_from_airports(airports)

    def q(idx):
        return np.log2(len(graph[idx]))

    k = 0.04
    for i, a in enumerate(airports):
        q1 = q(i)
        for j, b in enumerate(airports):
            if i == j:
                continue

            q2 = q(j)

            r = distance(a.geo_position, b.geo_position).miles
            assert r != 0

            f = k * q1 * q2 / r ** 2
            magnitude = (f / q1) * (dt ** 2 / 2)
            if np.isclose(magnitude, 0):
                continue

            displacement = (
                    magnitude
                    * (v := a.screen_position - b.screen_position)
                    / np.linalg.norm(v)
            )
            lat, lon = x_y_to_geo_pos_deg(*displacement)

            # naive force, wouldn't work like that
            a.latitude_deg += lat
            a.longitude_deg += lon


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
    def __init__(self, airports: list[Airport], timestamp: datetime.datetime = None):
        if timestamp is None:
            timestamp = datetime.datetime.now()

        # copy the values to prevent accidental mutations
        self.states = [
            AirportState(airport, AirportStatus.AVAILABLE) for airport in airports
        ]
        self._airports = airports.copy()
        self.timestamp = timestamp

        self.graph = graph_from_airports(self._airports)

        self._distance_cache = dict()
        for v0 in self.graph:
            for v1 in self.graph[v0]:
                # to simplify the cache use symmetry of distances
                if v1 > v0:
                    v0, v1 = v1, v0
                p0 = airports[v0].geo_position
                p1 = airports[v1].geo_position
                self._distance_cache[(v0, v1)] = distance(p0, p1).kilometers

        # TODO: choose a better dracula location
        self.dracula_location = 0
        self.dracula_trail = [self.dracula_location]

    @property
    def airports(self) -> list[Airport]:
        return [state.airport for state in self.states]

    def get_index(self, icao):
        for i in range(len(self._airports)):
            if icao == self._airports[i].ident:
                return i
        return -1

    def trap_location(self, index):
        if (
                self.states[index].status != AirportStatus.TRAPPED
                and self.states[index].status != AirportStatus.DESTROYED
        ):
            self.states[index].status = AirportStatus.TRAPPED

    def add_timer_for_traps(self, character):
        for state in self.states:
            if state.status == AirportStatus.TRAPPED:
                state.timer = state.timer + 1
                if state.timer > 3:
                    state.status = AirportStatus.AVAILABLE
                    character.trap_count += 1
                    state.timer = 0
