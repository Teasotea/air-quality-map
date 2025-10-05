# AirVision 🌍  

*A solution for [From EarthData to Action: Cloud Computing with Earth Observation Data for Predicting Cleaner, Safer Skies](https://www.spaceappschallenge.org/2025/challenges/from-earthdata-to-action-cloud-computing-with-earth-observation-data-for-predicting-cleaner-safer-skies)*  
Developed by **Team RandomStorm** (@Teasotea, @andrii0yerko) during the **NASA Space Apps Challenge 2025**, 4–5 October 2025.

---

## 🌍 PROJECT DETAILS  

**AirVision** is a web application that visualizes **real-time air quality** by combining **NASA TEMPO satellite data** with **ground-based OpenAQ sensor data**.  
The platform helps users understand their local air quality, receive forecasts such as *Good*, *Moderate*, or *Unhealthy*, and get alerts when pollution levels increase.

Our goal is to bridge **satellite Earth observation data** and **everyday public awareness**, transforming complex data into actionable insights for citizens, policymakers, and educators.

![airvision_demo](https://drive.google.com/file/d/1pfhAILsnZ9_88nBgpyKjOmUrvRXHf4vZ/view)

---

### ✨ Features  

1. **Integrated Air Quality Dashboard** – Displays real-time PM2.5, NO₂, and O₃ readings from OpenAQ alongside satellite-based pollution data from NASA TEMPO.  
2. **City-Level Search & Forecast** – Allows users to search any city or coordinates and receive a forecast labeled “Good / Moderate / Unhealthy.”  
3. **Satellite–Ground Comparison View** – Side-by-side visualization of satellite vs. ground-level measurements for data validation and context.  
4. **Health Alerts & Recommendations** – Simple, color-coded alerts to help users make informed outdoor activity decisions.  
5. **Offline Sample Mode** – Includes a sample dataset (`data/sample_data.json`) for instant visualization testing without API calls.

---

### 🧠 Technical Details  

We primarily use:  

- **OpenAQ API** – Live ground sensor data (PM2.5, NO₂, O₃).  
- **NASA TEMPO (Tropospheric Emissions: Monitoring of Pollution)** – Column-level satellite NO₂ and aerosol data for the North American region.  

**Core stack:**  

- `Python` + `Streamlit` – Web app engine and UI.  
- `Prophet` – Simple forecasting for short-term AQI prediction.  
- `Pydantic` – Data validation layer for OpenAQ & satellite inputs.

---

### 🧩 Challenges Tackled  

1. **Data Harmonization:** Aligning units and timestamps between OpenAQ and NASA datasets.  
2. **Lightweight Architecture:** Building a demo that works both locally and in the cloud (Streamlit + REST APIs).  
3. **Usability:** Simplifying air quality indices into accessible messages and visual cues for everyday users.  
4. **Forecast Modeling:** Implementing a minimal prediction model using Prophet for AQI trends.  

---

### 🚀 Future Enhancements  

1. Add **weather data** (wind, humidity) to refine forecasts.  
2. Build **mobile alerts and notifications**.  
3. Expand **region coverage** beyond North America.  
4. Deploy scalable **cloud version (Azure/AWS)** for global use.  
5. Include **historical air quality trend visualizations**.

---

## 🤖 USE OF ARTIFICIAL INTELLIGENCE  

We used **ChatGPT (GPT-5)** and **GitHub Copilot** to accelerate development and documentation.  
Forecasting was powered by **Prophet**, an open-source ML model for time series prediction.

---

## 🛰️ SPACE AGENCY DATA  

- [OpenAQ API](https://docs.openaq.org) – Ground air quality sensors (PM2.5, NO₂, O₃).  
- [NASA TEMPO Data](https://asdc.larc.nasa.gov/project/TEMPO) – Satellite pollution monitoring.  

---

## 📚 REFERENCES  

**Python libraries used:**  

- [Streamlit](https://streamlit.io/) – Web app engine  
- [Prophet](https://facebook.github.io/prophet/) – Forecasting model  
- [Folium](https://python-visualization.github.io/folium/) – Interactive maps  
- [OpenAQ Python SDK](https://github.com/openaq/openaq-api-client) – Air quality API  
- [Pydantic](https://docs.pydantic.dev/) – Data models  

**Other resources:**  

- [NASA EarthData TEMPO Portal](https://asdc.larc.nasa.gov/project/TEMPO)  
- [WHO Air Quality Guidelines 2021](https://www.who.int/news-room/fact-sheets/detail/ambient-(outdoor)-air-quality-and-health)

---

## 📜 LICENSE  

This project was created for the **NASA Space Apps Challenge 2025** and is open-sourced for educational and research use.  
