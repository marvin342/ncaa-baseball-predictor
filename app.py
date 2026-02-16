import streamlit as st
import pandas as pd
import requests
import os

# --- 1. THE BRAIN: 2026 TOP TEAM STATS ---
# This stops the AI from giving the same "14.4" to every game.
TEAM_INTEL = {
    "LSU Tigers": {"era": 3.4, "offense": 1.4},      # High strikeout pitching, massive bats
    "Oregon St Beavers": {"era": 3.6, "offense": 1.3},# Balanced powerhouse
    "Arkansas Razorbacks": {"era": 3.1, "offense": 1.1}, # Elite defense, fewer runs
    "Air Force Falcons": {"era": 6.1, "offense": 1.6},  # High altitude = OVER MACHINE
    "Tennessee Volunteers": {"era": 3.7, "offense": 1.5}, # Home run heavy
    "Wake Forest Demon Deacons": {"era": 3.3, "offense": 1.7}, # Launchpad stadium
    "Texas Longhorns": {"era": 3.9, "offense": 1.2},
    "Vanderbilt Commodores": {"era": 3.2, "offense": 0.9}, # Pitcher's duel team
}

def get_pro_prediction(home, away):
    # If team is not in list, use NCAA average (5.2 ERA, 1.1 Offense)
    h = TEAM_INTEL.get(home, {"era": 5.2, "offense": 1.1})
    a = TEAM_INTEL.get(away, {"era": 5.4, "offense": 1.1})
    
    # Logic: (Combined Pitching Weakness) * (Offensive Intensity) * Base Runs
    # This formula is more sensitive to high-scoring teams
    projection = ((h['era'] + a['era']) / 8.8) * ((h['offense'] + a['offense']) / 2) * 11.8
    return round(max(7.5, min(projection, 19.5)), 1)

# --- 2. THE INTERFACE ---
st.set_page_config(layout="wide", page_title="NCAA Diamond AI")
st.title("⚾ Pro-Grade NCAA Over/Under AI")
st.markdown("### Strategy: *Aggressive Value Detection (0.6 Run Edge)*")

API_KEY = os.getenv("ODDS_API_KEY")

if st.button('🚀 RUN FULL ANALYSIS'):
    url = f"https://api.the-odds-api.com/v4/sports/baseball_ncaa/odds/?apiKey={API_KEY}&regions=us&markets=totals"
    data = requests.get(url).json()
    
    if not data:
        st.warning("No live lines found. Vegas usually posts 2-4 hours before first pitch.")
    else:
        results = []
        for game in data:
            home, away = game['home_team'], game['away_team']
            try:
                vegas = game['bookmakers'][0]['markets'][0]['outcomes'][0]['point']
            except: continue
                
            ai_val = get_pro_prediction(home, away)
            edge = round(ai_val - vegas, 1)
            
            # ACTION LOGIC: Lowered to 0.6 so you get WAY more Over/Under calls
            if edge >= 0.6: 
                action = "🔥 BET OVER"
                color = "green"
            elif edge <= -0.6: 
                action = "❄️ BET UNDER"
                color = "red"
            else: 
                action = "PASS"
                color = "gray"
            
            results.append({
                "Matchup": f"{away} @ {home}",
                "Vegas Line": vegas,
                "AI Target": ai_val,
                "Edge": edge,
                "Action": action
            })
        
        df = pd.DataFrame(results)
        
        # Display as a clean table with Bold Recommendations
        st.table(df)
        st.success("Analysis Complete! Higher 'Edge' numbers mean more confidence.")
