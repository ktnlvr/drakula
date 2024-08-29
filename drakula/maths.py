import numpy as np
from math import atan, cos, sin, tan

from scipy.spatial import Delaunay


def angles_to_world_pos(lat: float, lon: float) -> np.ndarray:
    x = (180 + lon) / 360
    y = (90 - lat) / 180

    return np.array([x, y])

def geodesic_to_3d_pos(lat: float, lon: float, alt: float) -> np.ndarray:
    f = 0
    l = atan((1 - f)**2 * tan(lat))
    r = 1000

    x = r * cos(l) * cos(lon) + alt * cos(lat) * cos(lon)
    y = r * cos(l) * sin(lon) + alt * cos(lat) * sin(lon)
    z = r * sin(l) + alt * sin(lat)

    return np.array([x, y, z])

def points_to_hull(points):
    return Delaunay(points).simplices