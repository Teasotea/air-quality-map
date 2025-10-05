import sqlite3
from typing import List

from api.models import Location, Sensor


class AirQualityDB:
    def __init__(self, db_path: str = "air_quality.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def init_database(self) -> None:
        """Initialize the database with required tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Create locations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    last_updated TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create sensors table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensors (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create location_sensors relationship table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS location_sensors (
                    location_id INTEGER,
                    sensor_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (location_id, sensor_id),
                    FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE CASCADE,
                    FOREIGN KEY (sensor_id) REFERENCES sensors (id) ON DELETE CASCADE
                )
            """)

            # Create indexes for better query performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_location_coords ON locations (latitude, longitude)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_location_sensors_location ON location_sensors (location_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_location_sensors_sensor ON location_sensors (sensor_id)"
            )

            conn.commit()

    def store_location(self, location: Location) -> None:
        """Store a location and its sensors in the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Insert or update location
            cursor.execute(
                """
                INSERT OR REPLACE INTO locations (id, name, latitude, longitude, last_updated, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
                (
                    location.id,
                    location.name,
                    location.latitude,
                    location.longitude,
                    location.last_updated.isoformat()
                    if location.last_updated
                    else None,
                ),
            )

            # Insert sensors (ignore duplicates)
            for sensor in location.available_sensors:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO sensors (id, name)
                    VALUES (?, ?)
                """,
                    (sensor.id, sensor.name),
                )

            # Remove existing location-sensor relationships for this location
            cursor.execute(
                "DELETE FROM location_sensors WHERE location_id = ?", (location.id,)
            )

            # Insert new location-sensor relationships
            for sensor in location.available_sensors:
                cursor.execute(
                    """
                    INSERT INTO location_sensors (location_id, sensor_id)
                    VALUES (?, ?)
                """,
                    (location.id, sensor.id),
                )

            conn.commit()

    def store_locations_batch(self, locations: List[Location]) -> None:
        """Store multiple locations efficiently in a batch operation."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Prepare location data
            location_data = [
                (
                    loc.id,
                    loc.name,
                    loc.latitude,
                    loc.longitude,
                    loc.last_updated.isoformat() if loc.last_updated else None,
                )
                for loc in locations
            ]

            # Prepare sensor data (deduplicated)
            sensor_data = {}
            for location in locations:
                for sensor in location.available_sensors:
                    sensor_data[sensor.id] = (sensor.id, sensor.name)

            # Prepare relationship data
            relationship_data = [
                (location.id, sensor.id)
                for location in locations
                for sensor in location.available_sensors
            ]

            # Insert locations
            cursor.executemany(
                """
                INSERT OR REPLACE INTO locations (id, name, latitude, longitude, last_updated, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
                location_data,
            )

            # Insert sensors
            cursor.executemany(
                """
                INSERT OR IGNORE INTO sensors (id, name)
                VALUES (?, ?)
            """,
                list(sensor_data.values()),
            )

            # Remove existing relationships for these locations
            location_ids = [loc.id for loc in locations]
            cursor.executemany(
                "DELETE FROM location_sensors WHERE location_id = ?",
                [(loc_id,) for loc_id in location_ids],
            )

            # Insert new relationships
            cursor.executemany(
                """
                INSERT INTO location_sensors (location_id, sensor_id)
                VALUES (?, ?)
            """,
                relationship_data,
            )

            conn.commit()

    def get_sensors_by_location(self, location_id: int) -> List[Sensor]:
        """Get all sensors for a specific location."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT s.id, s.name
                FROM sensors s
                JOIN location_sensors ls ON s.id = ls.sensor_id
                WHERE ls.location_id = ?
            """,
                (location_id,),
            )

            return [Sensor(id=row[0], name=row[1]) for row in cursor.fetchall()]

    def get_locations_by_sensor(self, sensor_id: int) -> List[int]:
        """Get all location IDs that have a specific sensor."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT location_id
                FROM location_sensors
                WHERE sensor_id = ?
            """,
                (sensor_id,),
            )

            return [row[0] for row in cursor.fetchall()]

    def get_location_sensor_stats(self) -> dict:
        """Get statistics about locations and sensors in the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Count total locations
            cursor.execute("SELECT COUNT(*) FROM locations")
            total_locations = cursor.fetchone()[0]

            # Count total sensors
            cursor.execute("SELECT COUNT(*) FROM sensors")
            total_sensors = cursor.fetchone()[0]

            # Count total relationships
            cursor.execute("SELECT COUNT(*) FROM location_sensors")
            total_relationships = cursor.fetchone()[0]

            # Get average sensors per location
            cursor.execute("""
                SELECT AVG(sensor_count) FROM (
                    SELECT COUNT(*) as sensor_count
                    FROM location_sensors
                    GROUP BY location_id
                )
            """)
            avg_sensors_per_location = cursor.fetchone()[0] or 0

            return {
                "total_locations": total_locations,
                "total_sensors": total_sensors,
                "total_relationships": total_relationships,
                "avg_sensors_per_location": round(avg_sensors_per_location, 2),
            }


# Global database instance
db = AirQualityDB()
