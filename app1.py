import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import date, datetime

# --- 1. SETUP ---
st.set_page_config(page_title="FloodLink NYC 2026", layout="wide")
st.title("🛡️ FloodLink NYC: Strategic Flood Forecast")
st.markdown("### Coverage: January 12, 2026 – April 30, 2026")

# --- 2. GENERATING THE TIMELINE ---
start_date = date(2026, 1, 12)
end_date = date(2026, 4, 30)

# Create the date range
dates = pd.date_range(start=start_date, end=end_date, freq='D')

# Simulate the SARIMAX forecast values
# We'll put a simulated "Critical Event" in mid-March and late April
data = []
for d in dates:
    if (d.month == 3 and 14 <= d.day <= 17): # Mid-March Peak
        data.append(41.5)
    elif (d.month == 4 and 20 <= d.day <= 23): # Late-April Peak
        data.append(38.2)
    elif d.month >= 3: # Spring is generally wetter
        data.append(18.0 + (d.day % 10))
    else:
        data.append(12.0 + (d.day % 5))

df_forecast = pd.DataFrame({'Date': dates, 'Predicted_Precip': data})
df_forecast['Date_Only'] = df_forecast['Date'].dt.date

# --- 3. THE CALENDAR INTERFACE ---
st.sidebar.header("🗓️ Forecast Calendar")
selected_date = st.sidebar.date_input(
    "Select a date to inspect:",
    value=start_date,
    min_value=start_date,
    max_value=end_date
)

# --- 4. PREDICTION LOGIC ---
result = df_forecast[df_forecast['Date_Only'] == selected_date]
rain_val = result['Predicted_Precip'].values[0]

if rain_val >= 35:
    status, color = "CRITICAL FLOOD ALERT", "red"
elif rain_val >= 22:
    status, color = "ELEVATED WARNING", "orange"
else:
    status, color = "STABLE / LOW RISK", "green"

# --- 5. THE DASHBOARD ---
col1, col2 = st.columns([1, 1])

with col1:
    st.metric(label="Predicted Weekly Saturation", value=f"{rain_val:.1f} mm")
    st.subheader(f"Status: :{color}[{status}]")
    
    # Line Chart with Danger Threshold
    st.markdown("**Season Outlook (Jan - April)**")
    # Adding a threshold line for the chart
    df_chart = df_forecast.set_index('Date')[['Predicted_Precip']]
    df_chart['Danger_Line'] = 35.0
    st.line_chart(df_chart, color=["#29b5e8", "#ff0000"]) 
    st.caption("Blue: Forecasted Rain | Red Line: 35mm Flood Threshold")

with col2:
    # THE STAPLETON MAP
    st.markdown(f"**Geospatial Impact: {selected_date}**")
    m = folium.Map(location=[40.6267, -74.0755], zoom_start=14, tiles="cartodbpositron")
    
    folium.Circle(
        location=[40.6267, -74.0755],
        radius=900,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.4,
        tooltip=f"Alert: {status}"
    ).add_to(m)
    st_folium(m, width=500, height=400, key="map")