import os
from datetime import UTC, datetime, timedelta

from dateutil import parser
from openaq import OpenAQ

from api.database import db
from api.models import Location, Sensor


def exctact_datetime(location) -> datetime | None:
    if location.datetime_last is None:
        return None
    if location.datetime_last.utc is None:
        return None
    return parser.parse(location.datetime_last.utc)


client = OpenAQ(api_key=os.environ.get("OPENAQ_API_KEY", None))


def get_locations_by_coord(x=13.74433, y=100.54365, radius=10_000, limit=1000):
    locations = client.locations.list(coordinates=(x, y), radius=radius, limit=limit)

    new_locations = []
    for location in locations.results:
        loc = Location(
            id=location.id,
            name=location.name,
            latitude=location.coordinates.latitude,
            longitude=location.coordinates.longitude,
            available_sensors=[Sensor(id=s.id, name=s.name) for s in location.sensors],
            last_updated=exctact_datetime(location),
        )
        new_locations.append(loc)

    new_locations = [
        loc
        for loc in new_locations
        if loc.last_updated is not None
        and datetime.now(tz=UTC) - loc.last_updated < timedelta(days=1)
    ]

    # Store all locations and their sensor relationships in the database
    if new_locations:
        db.store_locations_batch(new_locations)

    return new_locations


def get_ground_data_by_location_id(
    location_id: int,
    datetime_from: str | None = None,
    datetime_to: str | None = None,
    limit: int = 100,
) -> dict[str, str | int | dict]:
    """
    Get ground sensor measurements for a location from OpenAQ API.

    Args:
        location_id: The ID of the location to get measurements for
        datetime_from: Start datetime in ISO format (defaults to 24 hours ago)
        datetime_to: End datetime in ISO format (defaults to now)
        limit: Maximum number of measurements per sensor

    Returns:
        Dictionary formatted similar to sample_data.json ground_data structure
    """
    # Set default time range if not provided
    if datetime_from is None:
        datetime_from = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    if datetime_to is None:
        datetime_to = datetime.now(UTC).isoformat()

    # Get sensors for this location from database
    sensors = db.get_sensors_by_location(location_id)

    if not sensors:
        return {
            "source": "OpenAQ",
            "parameters": {},
            "message": f"No sensors found for location ID {location_id}",
        }

    # Dictionary to store parameters with their latest measurements
    parameters = {}

    # Get measurements for each sensor
    for sensor in sensors:
        try:
            # Query measurements from OpenAQ
            measurements_response = client.measurements.list(
                sensors_id=sensor.id,
                datetime_from=datetime_from,
                datetime_to=datetime_to,
                limit=limit,
            )

            if measurements_response.results:
                # Get the latest measurement
                latest_measurement = measurements_response.results[0]

                # Extract parameter information
                parameter_name = latest_measurement.parameter.name
                parameter_units = latest_measurement.parameter.units
                parameter_value = latest_measurement.value

                parameters[parameter_name] = {
                    "value": parameter_value,
                    "unit": parameter_units,
                    "sensor_id": sensor.id,
                    "sensor_name": sensor.name,
                    "timestamp": latest_measurement.period.datetime_to.utc,
                }

        except Exception as e:
            # Log error but continue with other sensors
            print(
                f"Error getting measurements for sensor {sensor.id} ({sensor.name}): {e}"
            )
            continue

    return {
        "source": "OpenAQ",
        "parameters": parameters,
        "datetime_from": datetime_from,
        "datetime_to": datetime_to,
        "sensors_count": len(sensors),
        "measurements_found": len(parameters),
    }
