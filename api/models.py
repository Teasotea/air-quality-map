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


class ParameterMeasurement(BaseModel):
    value: float
    unit: str
    sensor_id: int
    sensor_name: str
    timestamp: str


class PredictionPoint(BaseModel):
    timestamp: str
    predicted_value: float
    lower_bound: float | None = None
    upper_bound: float | None = None


class ParameterPrediction(BaseModel):
    parameter_name: str
    unit: str
    model_type: str = "Prophet"
    forecast_hours: int = 24
    predictions: list[PredictionPoint]
    confidence_interval: float = 0.8
    training_data_points: int = 0


class ParameterMeasurementWithPrediction(ParameterMeasurement):
    prediction: ParameterPrediction | None = None


class GroundData(BaseModel):
    source: str
    parameters: dict[str, ParameterMeasurementWithPrediction]
    datetime_from: str
    datetime_to: str
    sensors_count: int
    measurements_found: int
    message: str | None = None
