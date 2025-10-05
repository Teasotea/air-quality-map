import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from api.database import AirQualityDB
from api.locations import get_ground_data_by_location_id, get_locations_by_coord
from api.predictions import AirQualityPredictor

# from api.models import Location

load_dotenv()
# --- Title ---
st.set_page_config(page_title="Air Quality Dashboard", layout="wide")
st.title("🌍 Air Quality Dashboard (OpenAQ)")

# Initialize the predictor
predictor = AirQualityPredictor(client=None)  # Pass the OpenAQ client if needed

# Initialize the database
AirQualityDB(db_path="air_quality.db")

# --- Location Search ---
st.subheader("🔍 Search Location")
col1, col2, col3 = st.columns(3)

with col1:
    latitude = st.number_input("Latitude", value=13.74433, format="%.5f")
with col2:
    longitude = st.number_input("Longitude", value=100.54365, format="%.5f")
with col3:
    radius = st.number_input(
        "Search Radius (meters)",
        value=10000,
        min_value=1000,
        max_value=100000,
        step=1000,
    )

if st.button("Search Locations"):
    locations = get_locations_by_coord(x=latitude, y=longitude, radius=radius)
    if locations:
        st.session_state.locations = locations
        st.session_state.selected_location = None
    else:
        st.error("No locations found in the specified radius")

# --- Location Selection ---
if "locations" in st.session_state:
    st.subheader("📍 Available Locations")
    location_options = {
        f"{loc.name} ({loc.id})": loc for loc in st.session_state.locations
    }
    selected_location_name = st.selectbox(
        "Select a location",
        options=list(location_options.keys()),
        key="location_selector",
    )

    if selected_location_name:
        selected_location = location_options[selected_location_name]
        st.session_state.selected_location = selected_location

        # Get ground data for selected location
        ground_data = get_ground_data_by_location_id(
            selected_location.id, include_predictions=False
        )

        # --- Display location info ---
        st.subheader(f"📍 {selected_location.name}")
        st.write(f"Last Updated: {selected_location.last_updated}")

        if ground_data.parameters:
            # Prepare ground data for display
            ground_measurements = []
            for param_name, measurement in ground_data.parameters.items():
                ground_measurements.append(
                    {
                        "Pollutant": param_name,
                        "Value": measurement.value,
                        "Unit": measurement.unit,
                        "Sensor": measurement.sensor_name,
                    }
                )

            ground_df = pd.DataFrame(ground_measurements)

            st.subheader("📊 Ground Measurements (OpenAQ)")
            st.dataframe(ground_df)

            # Bar chart
            if not ground_df.empty:
                fig = px.bar(
                    ground_df,
                    x="Pollutant",
                    y="Value",
                    color="Pollutant",
                    text="Value",
                    labels={"Value": "Concentration"},
                    title="Ground-level Air Pollutants",
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No recent measurements available for this location")

        # --- Map ---
        st.subheader("🗺 Location Map")
        map_df = pd.DataFrame(
            {
                "lat": [selected_location.latitude],
                "lon": [selected_location.longitude],
                "Location": [selected_location.name],
            }
        )

        st.map(map_df)

        # --- Sensor Info ---
        # Ensure selected_location is defined before accessing it
        if (
            "selected_location" in st.session_state
            and st.session_state.selected_location
        ):
            selected_location = st.session_state.selected_location

            st.subheader("📡 Available Sensors")
            for sensor in selected_location.available_sensors:
                st.write(f"- {sensor.name} (ID: {sensor.id})")
        else:
            st.warning(
                "No location selected. Please select a location to view sensors."
            )

        # --- Prediction Section ---
        if (
            "selected_location" in st.session_state
            and st.session_state.selected_location
        ):
            selected_location = st.session_state.selected_location

            st.subheader("📈 Air Quality Predictions")

            # Example: Predict for PM2.5
            historical_data = pd.DataFrame(
                {  # Replace with actual historical data fetching
                    "timestamp": pd.date_range(
                        start="2025-10-01", periods=24, freq="H"
                    ),
                    "value": [i + (i % 5) for i in range(24)],
                }
            )

            prediction = predictor.predict_parameter_from_data(
                historical_data=historical_data,
                parameter_name="pm25",
                parameter_unit="µg/m³",
                forecast_hours=24,
            )

            if prediction:
                # Prepare prediction data for display
                prediction_df = pd.DataFrame(
                    {
                        "Timestamp": [p.timestamp for p in prediction.predictions],
                        "Predicted Value": [
                            p.predicted_value for p in prediction.predictions
                        ],
                        "Lower Bound": [p.lower_bound for p in prediction.predictions],
                        "Upper Bound": [p.upper_bound for p in prediction.predictions],
                    }
                )

                st.dataframe(prediction_df)

                # Plot predictions
                fig = px.line(
                    prediction_df,
                    x="Timestamp",
                    y="Predicted Value",
                    error_y="Upper Bound",
                    error_y_minus="Lower Bound",
                    title="Predicted PM2.5 Levels",
                    labels={"Predicted Value": "Concentration (µg/m³)"},
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Unable to generate predictions due to insufficient data.")
