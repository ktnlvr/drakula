from math import nan
from collections import defaultdict
import datetime

from geopy.distance import distance
import numpy as np

from .maths import geodesic_to_3d_pos, delaunay_triangulate_points
from .utils import pairs
from .models import Airport

class GameState:
    def __init__(self, airports: list[Airport], timestamp: datetime.datetime = None):
        if timestamp is None:
            timestamp = datetime.datetime.now()

        # copy the values to prevent accidental mutations
        self.airports = airports.copy()
        self.timestamp = timestamp

        points = np.array([geodesic_to_3d_pos(airport.latitude_deg, airport.longitude_deg, airport.elevation_ft) for airport in airports])
        hull = delaunay_triangulate_points(points)

        graph = defaultdict(set)
        for simplex in hull:
            for i, j in pairs(simplex):
                graph[i].add(j)
                graph[j].add(i)

        self.graph = defaultdict(list)
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

    def distance_between(self, idx0: int, idx1: int) -> float:
        if idx1 > idx0:
            idx0, idx1 = idx1, idx0
        return self._distance_cache.get((idx0, idx1)) or nan

    def add_hours(self, hours: int):
        self.timestamp += datetime.timedelta(hours=hours)

    @property
    def day_percentage(self) -> float:
        return self.timestamp.second + 60 * (self.timestamp.minute + 60 * self.timestamp.hour)
