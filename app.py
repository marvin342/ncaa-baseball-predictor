import streamlit as st
import pandas as pd
import requests
import os
import numpy as np

# --- 1. THE AUTOMATED DATABASE (Top 2026 Teams) ---
# This replaces manual ERA entry. 
TEAM_DB = {
    "LSU Tigers": {"era": 3.45, "park": 1.05},
    "Wake Forest Demon Deacons": {"era": 3.20, "park": 1.25}, # Hitter paradise
    "Florida Gators": {"era": 3.90, "park": 1.00},
    "Vanderbilt Commodores": {"era": 3.10, "park": 0.90}, # Pitcher friendly
    "Arkansas Razorbacks": {"era": 3.25, "park": 0.95},
    "Tennessee Volunteers": {"era": 3.60, "park": 1.10},
    "Oregon State Beavers": {"era": 3.80, "park": 1.00},
    "TCU Horned Frogs": {"era": 4.10, "park": 1.00},
    "Texas Longhorns": {"era": 3.95, "park": 1.05}
}
DEFAULT_STATS = {"era": 4.80, "park": 1.00}

# --- 2. AUTOMATED WEATHER FETCH ---
def get_weather(city="Omaha"):
    # Using a free weather API (Open-Meteo) which requires no key
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude=35.22&longitude=-80.84&current=temperature_2m,wind_speed_10m"
        res = requests.get(url).json()
        temp = res['current']['temperature_2m'] * 1.8 + 32 # Convert to F
        wind = res['current']['wind_speed_10m']
        return temp, wind
    except:
        return 72, 5 # Default if weather fails

# --- 3. THE AI BRAIN ---
def auto_predict(home_team, away_team):
    h_data = TEAM_DB.get(home_team, DEFAULT_STATS)
    a_data = TEAM_DB.get(away_team, DEFAULT_STATS)
    temp, wind = get_weather()
    
    # Logic: Base runs + Pitching + Weather + Park
    base = 10.2
    pitching = (h_data['era'] + a_data['era']) * 0.4
    weather = (temp - 70) * 0.05 + (wind * 0.1)
    park = h_data['park']
    
    return round((base + pitching + weather) * park, 1)

# --- 4. THE INTERFACE ---
st.title("⚾ NCAA Diamond AI (Fully Automated)")
API_KEY = os.getenv("ODDS_API_KEY")

if st.button('🚀 RUN FULL AUTO ANALYSIS'):
    url = f"https://api.the-odds-api.com/v4/sports/baseball_ncaa/odds/?apiKey={API_KEY}&regions=us&markets=totals"
    data = requests.get(url).json()
    
    if not data:
        st.warning("No games found. Try again closer to first pitch!")
    else:
        for game in data:
            home = game['home_team']
            away = game['away_team']
            
            try:
                vegas = game['bookmakers'][0]['markets'][0]['outcomes'][0]['point']
            except:
                vegas = 11.5
                
            prediction = auto_predict(home, away)
            edge = round(prediction - vegas, 1)
            
            with st.expander(f"📊 {away} vs {home}", expanded=True):
                c1, c2, c3 = st.columns(3)
                c1.metric("AI Projection", prediction)
                c2.metric("Vegas Line", vegas)
                c3.metric("Edge", edge)
                
                if edge >= 1.5: st.success("🔥 ACTION: OVER")
                elif edge <= -1.5: st.error("❄️ ACTION: UNDER")
                else: st.info("PASS")
