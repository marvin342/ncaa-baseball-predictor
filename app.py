import streamlit as st
import pandas as pd
import requests
import numpy as np
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Gemini NCAA Diamond AI", page_icon="⚾", layout="wide")

# Theme Styling
st.markdown("""
    <style>
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #444; }
    [data-testid="stSidebar"] { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CONFIG & API ---
API_KEY = os.getenv("ODDS_API_KEY")
SPORT = 'baseball_ncaa' 

# --- 2. THE PREDICTION LOGIC (THE BRAIN) ---
def get_ai_prediction(h_era, a_era, wind, temp, park_factor):
    """
    Refined Calculation: Base + Pitching Quality + Environment.
    NCAA average runs per game (RPG) is typically higher than MLB (~10.5).
    """
    base_rpg = 10.4 
    # Weighted impact: Pitching accounts for 60% of run prevention
    pitching_impact = ((h_era + a_era) - 9.0) * 0.55 
    # Weather impact: Temp > 80 adds runs; Wind blowing IN (- mph) reduces runs
    weather_impact = ((temp - 72) * 0.03) + (wind * 0.12)
    
    final_total = (base_rpg + pitching_impact + weather_impact) * park_factor
    return round(final_total, 1)

# --- 3. SIDEBAR: SCOUTING REPORT ---
st.sidebar.header("📋 Today's Scouting Report")
st.sidebar.markdown("Update these based on the current matchup:")
h_era = st.sidebar.number_input("Home Team Starter ERA", 0.0, 12.0, 4.50)
a_era = st.sidebar.number_input("Away Team Starter ERA", 0.0, 12.0, 4.80)
temp = st.sidebar.slider("Temperature (°F)", 40, 105, 75)
wind = st.sidebar.slider("Wind (Blowing Out)", -25, 25, 0, help="Negative = Blowing In")
park = st.sidebar.selectbox("Park Factor", [0.90, 1.0, 1.15], index=1, 
                            format_func=lambda x: "Pitcher Friendly (e.g. MSST)" if x < 1 else "Hitter Paradise (e.g. Wake)" if x > 1 else "Neutral")

# --- 4. MAIN APP ---
st.title("⚾ NCAA Baseball AI Predictor")
st.write("Live analysis of Over/Under lines using your personal API key.")

if st.button('🔍 Analyze Live NCAA Games'):
    if not API_KEY:
        st.error("Missing API Key in Secrets!")
    else:
        url = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions=us&markets=totals'
        response = requests.get(url)
        games = response.json()

        if not games:
            st.warning("No NCAA totals found. Sportsbooks usually post these 3-4 hours before game time.")
        else:
            for game in games:
                home = game['home_team']
                away = game['away_team']
                
                # Get Vegas Total
                try:
                    vegas_line = game['bookmakers'][0]['markets'][0]['outcomes'][0]['point']
                except:
                    vegas_line = None

                # Calculate AI Prediction
                ai_total = get_ai_prediction(h_era, a_era, wind, temp, park)

                # Display Card
                with st.container():
                    st.subheader(f"{away} @ {home}")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    col1.metric("Vegas Line", vegas_line if vegas_line else "N/A")
                    col2.metric("AI Projection", ai_total)
                    
                    if vegas_line:
                        edge = round(ai_total - vegas_line, 2)
                        col3.metric("Edge (Runs)", edge)
                        
                        if edge >= 1.5:
                            col4.success("🔥 STRONG OVER")
                        elif edge <= -1.5:
                            col4.error("❄️ STRONG UNDER")
                        else:
                            col4.info("NO VALUE")
                    else:
                        col3.write("Waiting for odds...")
                    st.divider()
