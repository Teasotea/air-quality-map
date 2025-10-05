import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Title ---
st.set_page_config(page_title="Air Quality Dashboard", layout="wide")
st.title("🌍 Air Quality Dashboard (NASA + OpenAQ MVP)")

# --- Load sample data ---
with open("data/sample_data.json") as f:
    data = json.load(f)

# --- Display city info ---
city = data["location"]["city"]
country = data["location"]["country"]
st.subheader(f"{city}, {country}")
st.write(f"Data timestamp: {data['timestamp']}")

# --- Display combined AQ info ---
aq_category = data["combined_analysis"]["category"]
aq_index = data["combined_analysis"]["air_quality_index"]
recommendation = data["combined_analysis"]["recommendation"]

st.markdown(f"**Air Quality Index (AQI):** {aq_index}")
st.markdown(f"**Category:** {aq_category}")
st.info(recommendation)

# --- Display ground data ---
ground = data["ground_data"]["parameters"]
ground_df = pd.DataFrame({
    "Pollutant": ["PM2.5", "NO₂", "O₃"],
    "Value": [ground["pm25"]["value"], ground["no2"]["value"], ground["o3"]["value"]],
    "Unit": [ground["pm25"]["unit"], ground["no2"]["unit"], ground["o3"]["unit"]]
})

st.subheader("📊 Ground Measurements (OpenAQ)")
st.dataframe(ground_df)

# Bar chart
fig = px.bar(
    ground_df,
    x="Pollutant",
    y="Value",
    color="Pollutant",
    text="Value",
    labels={"Value": "Concentration"},
    title="Ground-level Air Pollutants"
)
st.plotly_chart(fig, use_container_width=True)

# --- Display satellite data ---
sat = data["satellite_data"]["parameters"]
sat_df = pd.DataFrame({
    "Pollutant": ["NO₂ Column Density", "Aerosol Index"],
    "Value": [sat["no2_column_density"]["value"], sat["aerosol_index"]["value"]],
    "Unit": [sat["no2_column_density"]["unit"], sat["aerosol_index"]["unit"]]
})

st.subheader("🛰 Satellite Measurements (TEMPO)")
st.dataframe(sat_df)

# Satellite bar chart
fig2 = px.bar(
    sat_df,
    x="Pollutant",
    y="Value",
    color="Pollutant",
    text="Value",
    labels={"Value": "Measurement"},
    title="Satellite Observations"
)
st.plotly_chart(fig2, use_container_width=True)

# --- Map ---
st.subheader("🗺 Location Map")
lat = data["location"]["coordinates"]["latitude"]
lon = data["location"]["coordinates"]["longitude"]

map_df = pd.DataFrame({
    "lat": [lat],
    "lon": [lon],
    "AQI": [aq_index]
})

st.map(map_df)

# --- Alerts ---
st.subheader("⚠ Alerts")
alerts = data["combined_analysis"].get("alerts", [])
if alerts:
    for alert in alerts:
        st.warning(f"{alert['type']}: {alert['message']}")
else:
    st.success("No alerts at this time.")

# --- Air Quality Forecast ---
def plot_air_quality_forecast():
    with open("data/sample_data2.json", "r") as f:
        data = json.load(f)
    hours = [entry["hour"] for entry in data]
    pm25 = [entry["pm25"] for entry in data]
    pm10 = [entry["pm10"] for entry in data]
    aqi = [entry["aqi"] for entry in data]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hours, y=pm25, mode='lines+markers', name='PM2.5'))
    fig.add_trace(go.Scatter(x=hours, y=pm10, mode='lines+markers', name='PM10'))
    fig.add_trace(go.Scatter(x=hours, y=aqi, mode='lines+markers', name='AQI'))
    fig.update_layout(
        title="24-Hour Air Quality Forecast",
        xaxis_title="Hour",
        yaxis_title="Value",
        legend_title="Metric",
        template="plotly_white"
    )
    st.plotly_chart(fig)

plot_air_quality_forecast()
