import numpy as np
from math import atan, cos, sin, tan

from scipy.spatial import Delaunay

# https://stackoverflow.com/questions/1369512/converting-longitude-latitude-to-x-y-on-a-map-with-calibration-points
def angles_to_world_pos(lat: float, lon: float) -> np.ndarray:
    """
    :param lat: north-south position of a point (from -90 at south to +90 at north).
    :param lon: east-west position of a point relative to the prime meridian (from -180 to +180)
    :return: the position of a point projected equirectangularly onto a flat plane
    """
    x = (180 + lon) / 360
    y = (90 - lat) / 180

    return np.array([x, y])

# https://stackoverflow.com/questions/10473852/convert-latitude-and-longitude-to-point-in-3d-space
def geodesic_to_3d_pos(lat_deg: float, lon_deg: float, alt_ft: float, flattening: float = 1/298.25, radius_ft: float = 2.093e+7) -> np.ndarray:
    """
    Convert latitude and longitude to coordinates on a sphere.

    :param lat_deg: north-south position of a point (from -90 at south to +90 at north).
    :param lon_deg: east-west position of a point relative to the prime meridian
    :param alt_ft: height of the position relative to the mean sea level
    :param flattening: compression of a sphere along the diameter (basically eccentricity but 3D).
        use 0 for naive projection, while the actual value is closer to 1/298.25
        (see https://www.oc.nps.edu/oc2902w/c_mtutor/shape/shape3.htm)
    :return: the position a given point would be at on the sphere
    """
    # for a spherical planet flattening should be zero
    # since earth is actually elliptical, we need to account for that
    # it will depend on the projection used

    # latitude at mean sea level
    lat = lat_deg * np.pi / 180.
    lon = lon_deg * np.pi / 180.
    alt = alt_ft
    l = atan((1 - flattening)**2 * tan(lat))
    r = radius_ft

    x = r * cos(l) * cos(lon) + alt * cos(lat) * cos(lon)
    y = r * cos(l) * sin(lon) + alt * cos(lat) * sin(lon)
    z = r * sin(l) + alt * sin(lat)

    return np.array([x, y, z])

# https://math.stackexchange.com/questions/804301/what-is-the-approximation-equation-for-making-the-day-night-wave
def solar_terminator_rad(lat_rad: float, gamma: float) -> float:
    return atan(gamma * sin(lat_rad))

def delaunay_triangulate_points(points):
    return Delaunay(points).convex_hull
