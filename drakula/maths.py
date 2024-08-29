from math import pi, tan, atan

def deg2norm(n):
    return n / 180

def angles_to_world_pos(lat: float, lon: float):
    x = lon / 180
    y = lat / 180

    return x, y
