import streamlit as st
import pandas as pd
import requests
import os

# --- 1. PRO TEAM DATABASE (2026 Season Intel) ---
# Automatically applies unique stats based on team identity
TEAM_INTEL = {
    "LSU Tigers": {"era": 3.4, "power": 1.2},      # Elite pitching + High offense
    "Oregon St Beavers": {"era": 3.6, "power": 1.3},# High scoring powerhouse
    "Arkansas Razorbacks": {"era": 3.1, "power": 1.0}, # Best pitching in SEC
    "Air Force Falcons": {"era": 6.1, "power": 1.5},  # Altitude = Runs
    "Tennessee Volunteers": {"era": 3.7, "power": 1.4}, # Massive HR potential
    "Wake Forest Demon Deacons": {"era": 3.3, "power": 1.6}, # Small park factor
    "Mississippi State Bulldogs": {"era": 3.5, "power": 0.9} # Pitcher friendly park
}

# --- 2. AUTOMATED SCOUTING ENGINE ---
def get_pro_prediction(home, away):
    # Fetch data or apply "Smart Average" for unknown teams
    h = TEAM_INTEL.get(home, {"era": 5.2, "power": 1.05})
    a = TEAM_INTEL.get(away, {"era": 5.4, "power": 1.05})
    
    # Fundamental Scoring Logic
    # (Pitching Weakness) x (Offensive Power) x (Baseline RPG)
    base_rpg = 10.5
    pitching_impact = (h['era'] + a['era']) / 9.0
    power_impact = (h['power'] + a['power']) / 2.0
    
    projection = base_rpg * pitching_impact * power_impact
    return round(max(7.5, min(projection, 18.5)), 1)

# --- 3. THE LIVE DASHBOARD ---
st.set_page_config(layout="wide")
st.title("⚾ Pro-Grade NCAA Diamond AI")
API_KEY = os.getenv("ODDS_API_KEY")

if st.button('🚀 ANALYZE LIVE VALUE'):
    url = f"https://api.the-odds-api.com/v4/sports/baseball_ncaa/odds/?apiKey={API_KEY}&regions=us&markets=totals"
    data = requests.get(url).json()
    
    if not data:
        st.warning("No live lines found yet. Books usually post 2-4 hours before first pitch.")
    else:
        results = []
        for game in data:
            home, away = game['home_team'], game['away_team']
            try:
                vegas = game['bookmakers'][0]['markets'][0]['outcomes'][0]['point']
            except: continue # Skip if no line posted
                
            ai_val = get_pro_prediction(home, away)
            edge = round(ai_val - vegas, 1)
            
            # Action Logic: Flag only high-value opportunities
            if edge >= 1.3: action = "🔥 OVER"
            elif edge <= -1.3: action = "❄️ UNDER"
            else: action = "PASS"
            
            results.append({"Matchup": f"{away} @ {home}", "Vegas": vegas, "AI": ai_val, "Edge": edge, "Action": action})
        
        # Display as a clean table
        df = pd.DataFrame(results)
        st.dataframe(df.style.background_gradient(subset=['Edge'], cmap='RdYlGn'))
