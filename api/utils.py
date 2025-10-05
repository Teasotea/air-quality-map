#!/usr/bin/env python3
"""
Utility functions for working with the air quality database.
"""

from api.database import db


def print_database_summary():
    """Print a summary of what's stored in the database."""
    stats = db.get_location_sensor_stats()
    print("=== Air Quality Database Summary ===")
    print(f"Total locations: {stats['total_locations']}")
    print(f"Total sensors: {stats['total_sensors']}")
    print(f"Total location-sensor relationships: {stats['total_relationships']}")
    print(f"Average sensors per location: {stats['avg_sensors_per_location']}")


def get_location_details(location_id: int):
    """Get detailed information about a specific location."""
    sensors = db.get_sensors_by_location(location_id)
    print(f"\nLocation ID {location_id} has {len(sensors)} sensors:")
    for sensor in sensors:
        print(f"  - {sensor.name} (ID: {sensor.id})")


def find_locations_with_sensor(sensor_name: str):
    """Find all locations that have a sensor with the given name."""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT DISTINCT l.id, l.name, l.latitude, l.longitude
            FROM locations l
            JOIN location_sensors ls ON l.id = ls.location_id
            JOIN sensors s ON ls.sensor_id = s.id
            WHERE s.name LIKE ?
        """,
            (f"%{sensor_name}%",),
        )

        results = cursor.fetchall()
        print(f"\nLocations with sensors containing '{sensor_name}':")
        for row in results:
            print(f"  - {row[1]} (ID: {row[0]}) at ({row[2]:.4f}, {row[3]:.4f})")


if __name__ == "__main__":
    print_database_summary()

    # Example queries
    find_locations_with_sensor("pm25")
    find_locations_with_sensor("no2")
