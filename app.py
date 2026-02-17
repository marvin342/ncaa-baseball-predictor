import streamlit as st
import pandas as pd
import requests
import os
import datetime

# --- 1. IP LOGGING ---
def log_user_activity():
    headers = st.context.headers
    user_ip = headers.get("X-Forwarded-For", "Unknown IP").split(',')[0]
    if "logged_visit" not in st.session_state:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] ACCESS LOG: User IP {user_ip} connected.")
        st.session_state["logged_visit"] = True
    return user_ip

# --- 2. PASSWORD PROTECTION ---
def check_password():
    def password_entered():
        if st.session_state["password"] == os.getenv("APP_PASSWORD", "admin123"):
            st.session_state["password_correct"] = True
            del st.session_state["password"] 
        else:
            st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    return True

# --- 3. THE APP GATE ---
if check_password():
    current_user_ip = log_user_activity()
    
    # --- EXPANDED TEAM BRAIN (SEC, ACC, BIG12, PAC12) ---
    TEAM_INTEL = {
        # SEC
        "LSU Tigers": {"era": 3.4, "offense": 1.4}, "Arkansas Razorbacks": {"era": 3.1, "offense": 1.1},
        "Florida Gators": {"era": 3.9, "offense": 1.3}, "Tennessee Volunteers": {"era": 3.7, "offense": 1.5},
        "Vanderbilt Commodores": {"era": 3.2, "offense": 0.9}, "Texas A&M Aggies": {"era": 3.8, "offense": 1.3},
        "Mississippi State Bulldogs": {"era": 3.9, "offense": 1.1}, "South Carolina Gamecocks": {"era": 4.1, "offense": 1.2},
        "Ole Miss Rebels": {"era": 4.5, "offense": 1.2}, "Georgia Bulldogs": {"era": 4.8, "offense": 1.3},
        "Auburn Tigers": {"era": 4.6, "offense": 1.2}, "Alabama Crimson Tide": {"era": 4.2, "offense": 1.1},
        
        # ACC
        "Wake Forest Demon Deacons": {"era": 3.3, "offense": 1.7}, "Clemson Tigers": {"era": 3.9, "offense": 1.3},
        "Virginia Cavaliers": {"era": 4.0, "offense": 1.4}, "Florida State Seminoles": {"era": 4.2, "offense": 1.4},
        "Duke Blue Devils": {"era": 3.8, "offense": 1.2}, "NC State Wolfpack": {"era": 4.3, "offense": 1.3},
        "North Carolina Tar Heels": {"era": 4.1, "offense": 1.3}, "Miami Hurricanes": {"era": 4.7, "offense": 1.2},
        
        # Big 12 / Pac-12 / Others
        "Texas Longhorns": {"era": 3.9, "offense": 1.2}, "TCU Horned Frogs": {"era": 4.1, "offense": 1.1},
        "Oklahoma State Cowboys": {"era": 4.3, "offense": 1.3}, "Texas Tech Red Raiders": {"era": 4.9, "offense": 1.5},
        "Oregon St Beavers": {"era": 3.6, "offense": 1.3}, "Stanford Cardinal": {"era": 4.2, "offense": 1.0},
        "Arizona State Sun Devils": {"era": 5.1, "offense": 1.4}, "UCLA Bruins": {"era": 3.9, "offense": 0.9},
        "Air Force Falcons": {"era": 6.1, "offense": 1.6}, "East Carolina Pirates": {"era": 3.5, "offense": 1.1},
        "Coastal Carolina Chanticleers": {"era": 4.8, "offense": 1.5}, "Dallas Baptist Patriots": {"era": 4.0, "offense": 1.3}
    }

    def get_pro_prediction(home, away):
        h = TEAM_INTEL.get(home, {"era": 5.2, "offense": 1.1})
        a = TEAM_INTEL.get(away, {"era": 5.4, "offense": 1.1})
        # Score Projection Formula
        projection = ((h['era'] + a['era']) / 8.8) * ((h['offense'] + a['offense']) / 2) * 11.8
        return round(max(7.5, min(projection, 19.5)), 1)

    st.set_page_config(layout="wide", page_title="NCAA Diamond AI")
    st.title("⚾ Pro-Grade NCAA Over/Under AI")
    st.sidebar.write(f"Logged: {current_user_ip}")

    if st.sidebar.button("🔒 Logout"):
        st.session_state["password_correct"] = False
        st.rerun()

    API_KEY = os.getenv("ODDS_API_KEY")

    if st.button('🚀 RUN FULL ANALYSIS'):
        url = f"https://api.the-odds-api.com/v4/sports/baseball_ncaa/odds/?apiKey={API_KEY}&regions=us&markets=totals"
        data = requests.get(url).json()
        
        if not data:
            st.warning("No live lines found. Check back tomorrow for Midweek games!")
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
                
                results.append({"Matchup": f"{away} @ {home}", "Vegas": vegas, "AI": ai_val, "Edge": edge, "Action": action})
            
            st.table(pd.DataFrame(results))
            st.success("Analysis Complete!")
