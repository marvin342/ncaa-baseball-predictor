import streamlit as st
import pandas as pd
import requests
import os
import datetime

# --- NEW: IP LOGGING FUNCTION ---
def log_user_activity():
    # Attempt to get IP from headers (works on Hugging Face/Cloud)
    # Most cloud providers use 'X-Forwarded-For'
    headers = st.context.headers
    user_ip = headers.get("X-Forwarded-For", "Unknown IP").split(',')[0]
    
    # Log to the Hugging Face Console (you'll see this in the "Logs" tab)
    if "logged_visit" not in st.session_state:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] ACCESS LOG: User IP {user_ip} connected.")
        st.session_state["logged_visit"] = True
    return user_ip

# --- 1. PASSWORD PROTECTION SYSTEM ---
def check_password():
    def password_entered():
        if st.session_state["password"] == os.getenv("APP_PASSWORD", "admin123"):
            st.session_state["password_correct"] = True
            del st.session_state["password"] 
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter Password to Access AI", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter Password to Access AI", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

# --- 2. THE APP GATE ---
if check_password():
    # Run the logging
    current_user_ip = log_user_activity()
    
    # --- ALL YOUR ORIGINAL CODE STARTS HERE ---
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

    st.set_page_config(layout="wide", page_title="NCAA Diamond AI")
    st.title("⚾ Pro-Grade NCAA Over/Under AI")
    st.sidebar.write(f"Logged in as: {current_user_ip}") # Displays their IP in the sidebar

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
                
                if edge >= 0.6: action = "🔥 BET OVER"
                elif edge <= -0.6: action = "❄️ BET UNDER"
                else: action = "PASS"
                
                results.append({
                    "Matchup": f"{away} @ {home}",
                    "Vegas Line": vegas,
                    "AI Target": ai_val,
                    "Edge": edge,
                    "Action": action
                })
            
            df = pd.DataFrame(results)
            st.table(df)
            st.success("Analysis Complete!")
