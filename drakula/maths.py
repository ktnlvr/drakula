import numpy as np

def angles_to_world_pos(lat: float, lon: float):
    x = (180 + lon) / 360
    y = (90 - lat) / 180

    return np.array([x, y])
