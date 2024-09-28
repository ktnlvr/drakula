import datetime
from collections import defaultdict
from enum import Enum
import numpy as np
from geopy.distance import distance

from .maths import geodesic_to_3d_pos, delaunay_triangulate_points
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

        points = np.array(
            [
                geodesic_to_3d_pos(
                    airport.latitude_deg, airport.longitude_deg, airport.elevation_ft
                )
                for airport in airports
            ]
        )
        hull = delaunay_triangulate_points(points)

        graph = defaultdict(set)
        for simplex in hull:
            for i, j in pairs(simplex):
                graph[i].add(j)
                graph[j].add(i)

        self.graph: dict[int, list[int]] = defaultdict(list)
        for vert in graph:
            assert vert not in self.graph[vert]

            def relative_distance_key(rel_to_idx: int):
                def func(idx: int):
                    a = points[rel_to_idx]
                    b = points[idx]
                    return np.dot(a - b, (a - b).T)

                return func

            self.graph[vert] = sorted(graph[vert], key=relative_distance_key(vert))
        self._distance_cache = dict()
        for v0 in self.graph:
            for v1 in self.graph[v0]:
                # to simplify the cache use symmetry of distances
                if v1 > v0:
                    v0, v1 = v1, v0
                p0 = airports[v0].position
                p1 = airports[v1].position
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

    def distance_between(self, idx0: int, idx1: int) -> float:
        if idx1 > idx0:
            idx0, idx1 = idx1, idx0
        pair = (idx0, idx1)
        if pair in self._distance_cache:
            p0 = self.airports[idx0].position
            p1 = self.airports[idx1].position
            self._distance_cache[pair] = distance(p0, p1).kilometers
        return self._distance_cache[pair]

    def add_hours(self, hours: int):
        self.timestamp += datetime.timedelta(hours=hours)

    @property
    def day_percentage(self) -> float:
        secs = self.timestamp.second + 60 * (
                self.timestamp.minute + 60 * self.timestamp.hour
        )
        secs_in_day = 86400
        return secs / secs_in_day
