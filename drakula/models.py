from pydantic import BaseModel, PositiveInt

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
