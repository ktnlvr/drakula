import numpy as np
from math import atan, cos, sin, tan, tau, asin, atan2
import datetime

from scipy.spatial import Delaunay

Rad = float
Deg = float


# https://stackoverflow.com/questions/1369512/converting-longitude-latitude-to-x-y-on-a-map-with-calibration-points
def angles_to_world_pos(lat: Deg, lon: Deg) -> np.ndarray:
    """
    :param lat: north-south position of a point (from -90 at south to +90 at north).
    :param lon: east-west position of a point relative to the prime meridian (from -180 to +180)
    :return: the position of a point projected equirectangularly onto a flat plane
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
    radius_ft: float = 2.093e7,
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
    r = radius_ft

    x = r * cos(l) * cos(lon) + alt * cos(lat) * cos(lon)
    y = r * cos(l) * sin(lon) + alt * cos(lat) * sin(lon)
    z = r * sin(l) + alt * sin(lat)

    return np.array([x, y, z])


# https://celestialprogramming.com/snippets/terminator.html
def solar_terminator_rad_from_gp(longitude: Rad, sun_lat: Rad, sun_lon: Rad) -> float:
    return atan(-cos(longitude - sun_lon) / tan(sun_lat))


def to_julian_datetime(date: datetime.datetime) -> float:
    return (
        date.toordinal()
        + (date.hour * 60 * 60 + date.minute * 60 + date.second) / (24 * 60 * 60)
        + 1721424.375
    )


def geographise(ra, dec, gst):
    lat = dec
    lon = ra - gst
    if lon > tau:
        lon -= tau
    if lon > tau / 2:
        lon = lon - tau
    if lon < -tau / 2:
        lon = lon + tau
    return lat, lon


# https://celestialprogramming.com/sunPosition-LowPrecisionFromAstronomicalAlmanac.html
def solar_position_from_jd(jd: float) -> np.ndarray:
    deg2rad = tau / 360

    def earth_rotation_angle(jd):
        t = jd - 2451545
        frac = t % 1.0
        era = (tau * (0.7790572732640 + 0.00273781191135448 * t + frac)) % tau
        era += (era < 0) * tau
        return era

    def greenwich_mean_sidereal_time(jd):
        t = (jd - 2451545.0) / 36525.0
        era = earth_rotation_angle(jd)
        gmst = (
            era
            + (
                0.014506
                + 4612.15739966 * t
                + 1.39667721 * t * t
                + -0.00009344 * t * t * t
                + 0.00001882 * t * t * t * t
            )
            / 60
            / 60
            * deg2rad
        )
        gmst %= tau
        return gmst

    n = jd - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360
    g = ((357.528 + 0.9856003 * n) % 360) * deg2rad
    L += (L < 0) * 360
    g += (g < 0) * tau

    l = (L + 1.915 * sin(g) + 0.02 * sin(2 * g)) * deg2rad
    eps = (23.439 - 0.0000004 * n) * deg2rad
    ra = atan2(cos(eps) * sin(l), cos(l))
    dec = asin(sin(eps) * sin(l))
    ra += (ra < 0) * tau

    gmst = greenwich_mean_sidereal_time(jd)
    gp = geographise(ra, dec, gmst)
    return np.array(list(gp))


def delaunay_triangulate_points(points):
    return Delaunay(points).convex_hull
