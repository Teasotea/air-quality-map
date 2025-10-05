from datetime import UTC, datetime, timedelta

from pydantic import BaseModel


class Sensor(BaseModel):
    id: int
    name: str


class Location(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    available_sensors: list[Sensor]
    last_updated: datetime | None = None
