# pages/live_matches.py - Displays live match data from Cricbuzz API

import streamlit as st
import pandas as pd
import requests

def show():
    """Display live cricket match scorecards"""
    
    st.title("🏏 Cricket Scorecard Viewer")

    # -------- Function to fetch API data -------
    @st.cache_data(ttl=300)
    def fetch_api_data(endpoint, params=None):
        url = f"https://cricbuzz-cricket.p.rapidapi.com/{endpoint}"
        headers = {
            "X-RapidAPI-Key": "ccd5e07057mshc46e980e731a93bp1a6172jsn2a725cb7e614",
            "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Error {response.status_code}: {response.text}"}

    # ------------ Fetch different match types --------
    def get_matches_by_type(endpoint, limit=2):
        data = fetch_api_data(endpoint)
        result = []
        for type_match in data.get("typeMatches", []):
            for series_match in type_match.get("seriesMatches", []):
                series_data = series_match.get("seriesAdWrapper", {})
                series_name = series_data.get("seriesName")
                series_id = series_data.get("seriesId")

                for match in series_data.get("matches", []):
                    info = match.get("matchInfo", {})
                    match_id = info.get("matchId")
                    team1 = info.get("team1", {}).get("teamName")
                    team2 = info.get("team2", {}).get("teamName")
                    match_format = info.get("matchFormat")
                    match_state = info.get("state")

                    venue_info = info.get("venueInfo", {})
                    venue_ground = venue_info.get("ground")
                    venue_country = venue_info.get("city")

                    result.append({
                        "team1": team1,
                        "team2": team2,
                        "format": match_format,
                        "state": match_state,
                        "match_id": match_id,
                        "series_id": series_id,
                        "series_name": series_name,
                        "ground": venue_ground,
                        "country": venue_country
                    })
        return result[:limit]

    # -------- Fetch scorecard by match_id ------------
    def scorecard(match_id):
        data = fetch_api_data(f"mcenter/v1/{match_id}/scard")

        innings_data = {}
        for idx, i in enumerate(data.get("scorecard", [])):
            runs = i.get("total") or i.get("runs") or i.get("score") or i.get("runsScored") or None
            wickets = i.get("wickets")
            if runs is None or runs == "":
                runs = "0"
            if wickets is None or wickets == "":
                wickets = "0"
            team_overs = i.get("overs", "0")

            score_string = f"{runs}/{wickets}"

            innings_name = i.get("inningsName")
            if not innings_name or innings_name.lower() == "none":
                innings_name = f"Innings {s_innings if (s_innings := i.get('inningsId')) else idx+1}"

            batting_scorecard = []
            bowling_scorecard = []

            for j in i.get("batsman", []):
                batting_scorecard.append({
                    "Batsman": j.get("name"),
                    "Runs": j.get("runs"),
                    "Balls": j.get("balls"),
                    "4s": j.get("fours"),
                    "6s": j.get("sixes"),
                    "SR": j.get("strkrate"),
                    "Dismissal": j.get("outdec")
                })

            for z in i.get("bowler", []):
                bowling_scorecard.append({
                    "Bowler": z.get("name"),
                    "Overs": z.get("overs"),
                    "Runs": z.get("runs"),
                    "Wickets": z.get("wickets"),
                    "Economy": z.get("economy")
                })

            innings_data[innings_name] = {
                "Batting": pd.DataFrame(batting_scorecard),
                "Bowling": pd.DataFrame(bowling_scorecard),
                "Score": f"{score_string} in {team_overs} overs"
            }

        st.markdown("### Score card")
        for innings_name, details in innings_data.items():
            st.subheader(f"🏏 {innings_name} - Team Score: {details['Score']}")
            st.subheader(f"🏏 {innings_name} - Batting")
            st.dataframe(details["Batting"])
            st.subheader(f"🎯 {innings_name} - Bowling")
            st.dataframe(details["Bowling"])

    # ------------ URL TO FETCH ---------------
    live_matches = get_matches_by_type("matches/v1/live", limit=2)
    recent_matches = get_matches_by_type("matches/v1/recent", limit=2)
    upcoming_matches = get_matches_by_type("matches/v1/upcoming", limit=2)

    matches = live_matches + recent_matches + upcoming_matches

    # ---------- Streamlit display --------------
    if matches:
        match_options = [f"{m['team1']} vs {m['team2']} ({m['state']})" for m in matches]
        match_map = {f"{m['team1']} vs {m['team2']} ({m['state']})": m['match_id'] for m in matches}

        selected_match = st.selectbox("Select a Match:", match_options)
        selected_match_id = match_map[selected_match]

        match_details = next((m for m in matches if m['match_id'] == selected_match_id), None)

        if match_details:
            st.subheader(f"{match_details['team1']} vs {match_details['team2']}")
            st.success(f"Series: {match_details['series_name']}")
            st.success(f"State: {match_details['state']}")
            st.success(f"Venue: {match_details['ground']} -- {match_details['country']}")
            st.success(f"Format: {match_details['format']}")

            if "innings_data_global" not in st.session_state:
                st.session_state.innings_data_global = None

            if st.button("Fetch Scorecard"):
                scorecard(selected_match_id)
    else:
        st.warning("No matches found")
