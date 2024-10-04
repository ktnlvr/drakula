import numpy as np
from math import atan, cos, sin, tan

from scipy.spatial import Delaunay

Rad = float
Deg = float

EARTH_RADIUS = 2.093e7


# https://stackoverflow.com/questions/1369512/converting-longitude-latitude-to-x-y-on-a-map-with-calibration-points
def geo_pos_to_screen_pos(lat: Deg, lon: Deg) -> np.ndarray:
    """
    :param lat: north-south position of a point (from -90 at south to +90 at north).
    :param lon: east-west position of a point relative to the prime meridian (from -180 to +180)
    :return: the position of a point projected equirectangularly onto a flat plane from 0 to 1
    """
    x = (180 + lon) / 360
    y = (90 - lat) / 180
    return np.array([x, y])

# https://stackoverflow.com/questions/10473852/convert-latitude-and-longitude-to-point-in-3d-space
def geodesic_to_3d_pos(
    lat_deg: Deg,
    lon_deg: Deg,
    alt_ft: float,
    flattening: float = 1 / 298.25,
) -> np.ndarray:
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
    lat = lat_deg * np.pi / 180.0
    lon = lon_deg * np.pi / 180.0
    alt = alt_ft
    l = atan((1 - flattening) ** 2 * tan(lat))
    r = EARTH_RADIUS

    x = r * cos(l) * cos(lon) + alt * cos(lat) * cos(lon)
    y = r * cos(l) * sin(lon) + alt * cos(lat) * sin(lon)
    z = r * sin(l) + alt * sin(lat)

    return np.array([x, y, z])

# https://en.wikipedia.org/wiki/Spherical_coordinate_system#Cartesian_coordinates
def x_y_to_geo_pos_deg(x, y):
    """
    :param x:screen position from 0 to 1
    :param y:screen position from 0 to 1
    :return:returns latitude and longitude as an array
    """
    theta = np.arccos(1 / np.sqrt(x**2 + y**2 + 1))
    phi = np.sign(y) * np.arccos(x / np.sqrt(x**2 + y**2))
    return np.array([theta, phi])


def delaunay_triangulate_points(points):
    """
    :param: coordinates of the points in 3D space
    :return: the convex hull of the points
    """
    return Delaunay(points).convex_hull
