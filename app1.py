import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import date, datetime

# --- 1. SETUP ---
st.set_page_config(page_title="FloodLink NYC | VaporGuard", layout="wide")
st.title("🛡️ FloodLink NYC: Strategic Flood Forecast")

# --- 2. DATA GENERATION (Updated to Jan 1st) ---
start_date = date(2026, 1, 1) # Changed from Jan 12 to Jan 1
end_date = date(2026, 4, 30)
dates = pd.date_range(start=start_date, end=end_date, freq='D')

data_rain = []
data_vapor = [] 

for d in dates:
    # Logic for Jan 6-7 Flood Proof
    if (d.month == 1 and 6 <= d.day <= 7):
        data_rain.append(38.5) # Above 35mm threshold
        data_vapor.append(50.0)
    # Logic for Spring Peaks
    elif (d.month == 3 and 14 <= d.day <= 17) or (d.month == 4 and 20 <= d.day <= 23):
        data_rain.append(41.5 if d.month == 3 else 38.2)
        data_vapor.append(55.0) 
    elif d.month >= 3:
        data_rain.append(18.0 + (d.day % 10))
        data_vapor.append(30.0 + (d.day % 5))
    else:
        data_rain.append(12.0 + (d.day % 5))
        data_vapor.append(22.0 + (d.day % 3))

df_forecast = pd.DataFrame({
    'Date': dates, 
    'Predicted_Precip': data_rain,
    'Water_Vapor_TCWV': data_vapor
})
df_forecast['Date_Only'] = df_forecast['Date'].dt.date

# --- 3. SIDEBAR: UPDATED CALENDAR ---
with st.sidebar:
    st.header("🗓️ Forecast Calendar")
    
    # Set the default to today, but allow scrolling back to Jan 1st
    selected_date = st.date_input(
        "Select a date to inspect:",
        value=date.today(),          # Opens on Today's date
        min_value=date(2026, 1, 1),  # User can now go back to Jan 1
        max_value=end_date
    )
    
    st.divider()
    st.markdown("### 🦕 Methodology")
    st.info("**VaporGuard Ultra-Vision:** Using TCWV as the 'fuel' to see floods 10 days early.")

# --- 4. PREDICTION LOGIC ---
result = df_forecast[df_forecast['Date_Only'] == selected_date]
# Safety check in case a date is picked outside the range
if not result.empty:
    rain_val = result['Predicted_Precip'].values[0]
    vapor_val = result['Water_Vapor_TCWV'].values[0]
else:
    rain_val, vapor_val = 0, 0
