import math

import numpy as np
from numpy.typing import NDArray

from pydantic import BaseModel, PositiveInt, field_validator

from drakula.maths import geo_pos_to_screen_pos


class Airport(BaseModel):
    """
    Contains all the information related to the airport provided from the database
    """
    id: PositiveInt
    ident: str
    type: str
    name: str
    latitude_deg: float
    longitude_deg: float
    elevation_ft: int
    continent: str
    iso_country: str
    iso_region: str
    municipality: str
    scheduled_service: str
    gps_code: str
    iata_code: str
    local_code: str
    home_link: str

    @property
    def geo_position(self) -> NDArray[(2,)]:
        """
        :returns: A 2D numpy array containing latitude and longitude of the point
        """
        return np.array([self.latitude_deg, self.longitude_deg])

    @property
    def screen_position(self) -> NDArray[(2,)]:
        """
        Converts geographical position of the image to position on the screen
        :returns: A 2D numpy array containing coordinates of the geographical point on the
        screen
        """
        return geo_pos_to_screen_pos(*self.geo_position)

    def correct_geo_position(self):
        """Correct latitude and longitude to be within their respective ranges"""
        self.latitude_deg = (self.latitude_deg + 90) % 180 - 90

        longitude_reduced = self.longitude_deg % 360.
        if longitude_reduced > 180.:
            longitude_reduced -= 360
        elif longitude_reduced < -180:
            longitude_reduced += 360
        self.longitude_deg = longitude_reduced

    @field_validator("elevation_ft", mode="before")
    def check_elevation(cls, value: str) -> int:
        if not value:
            return 0
        return value
