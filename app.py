import streamlit as st
import pandas as pd
import requests
import os

# --- 1. PASSWORD PROTECTION SYSTEM ---
def check_password():
    """Returns True if the user had the correct password."""
    def password_entered():
        # This looks for the secret you set in Hugging Face Settings
        if st.session_state["password"] == os.getenv("APP_PASSWORD", "admin123"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input("Enter Password to Access AI", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Enter Password to Access AI", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

# --- 2. THE APP GATE ---
if check_password():
    # --- ALL YOUR ORIGINAL CODE STARTS HERE ---
    
    # --- THE BRAIN: 2026 TOP TEAM STATS ---
    TEAM_INTEL = {
        "LSU Tigers": {"era": 3.4, "offense": 1.4},      
        "Oregon St Beavers": {"era": 3.6, "offense": 1.3},
        "Arkansas Razorbacks": {"era": 3.1, "offense": 1.1}, 
        "Air Force Falcons": {"era": 6.1, "offense": 1.6},  
        "Tennessee Volunteers": {"era": 3.7, "offense": 1.5}, 
        "Wake Forest Demon Deacons": {"era": 3.3, "offense": 1.7}, 
        "Texas Longhorns": {"era": 3.9, "offense": 1.2},
        "Vanderbilt Commodores": {"era": 3.2, "offense": 0.9}, 
    }

    def get_pro_prediction(home, away):
        h = TEAM_INTEL.get(home, {"era": 5.2, "offense": 1.1})
        a = TEAM_INTEL.get(away, {"era": 5.4, "offense": 1.1})
        projection = ((h['era'] + a['era']) / 8.8) * ((h['offense'] + a['offense']) / 2) * 11.8
        return round(max(7.5, min(projection, 19.5)), 1)

    # --- THE INTERFACE ---
    st.set_page_config(layout="wide", page_title="NCAA Diamond AI")
    st.title("⚾ Pro-Grade NCAA Over/Under AI")
    st.markdown("### Strategy: *Aggressive Value Detection (0.6 Run Edge)*")

    # Logout button in the sidebar
    if st.sidebar.button("🔒 Logout"):
        st.session_state["password_correct"] = False
        st.rerun()

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
                
                if edge >= 0.6: 
                    action = "🔥 BET OVER"
                elif edge <= -0.6: 
                    action = "❄️ BET UNDER"
                else: 
                    action = "PASS"
                
                results.append({
                    "Matchup": f"{away} @ {home}",
                    "Vegas Line": vegas,
                    "AI Target": ai_val,
                    "Edge": edge,
                    "Action": action
                })
            
            df = pd.DataFrame(results)
            st.table(df)
            st.success("Analysis Complete! Higher 'Edge' numbers mean more confidence.")
