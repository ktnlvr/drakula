import numpy as np
from numpy.typing import NDArray

from pydantic import BaseModel, PositiveInt, field_validator

from drakula.maths import geo_pos_to_screen_pos


class Airport(BaseModel):
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

    @field_validator("elevation_ft", mode="before")
    def check_elevation(cls, value: str) -> int:
        if not value:
            return 0
        return value

    @property
    def geo_position(self) -> NDArray[(2,)]:
        return np.array([self.latitude_deg, self.longitude_deg])

    @property
    def screen_position(self) -> NDArray[(2,)]:
        return geo_pos_to_screen_pos(*self.geo_position)
