import streamlit as st
import pandas as pd
import requests

def show():
    """Display top player statistics and profiles"""
    
    st.title("🏏 Top Player Stats")

    # -------- Generic fetch function --------
    def fetch_api_data(endpoint):
        url = f"https://cricbuzz-cricket.p.rapidapi.com/{endpoint}"
        headers = {
            "x-rapidapi-key": "1ad8ad45bbmsh2d7900607b85972p1a6bf9jsnc5396b7aa21e",
            "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception:
            return {}

    # -------- Search for players by name --------
    def fetch_player_search(name):
        url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/search"
        querystring = {"plrN": name}
        headers = {
            "x-rapidapi-key": "1ad8ad45bbmsh2d7900607b85972p1a6bf9jsnc5396b7aa21e",
            "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
        }
        try:
            response = requests.get(url, headers=headers, params=querystring)
            data = response.json()
            players = []
            for i in data.get("player", []):
                players.append({
                    "player_id": i.get("id", "N/A"),
                    "player_name": i.get("name", "N/A"),
                    "player_team": i.get("teamName", "N/A"),
                    "player_dob": i.get("dob", "N/A")
                })
            return players
        except Exception:
            return []

    # -------- Player Profile --------
    def player_profile(player_id):
        endpoint = f"stats/v1/player/{player_id}"
        raw_data = fetch_api_data(endpoint) or {}
        profile = {
            "id": raw_data.get("id", "N/A"),
            "name": raw_data.get("name", "N/A"),
            "nickName": raw_data.get("nickName", "N/A"),
            "role": raw_data.get("role", "N/A"),
            "bat": raw_data.get("bat", "N/A"),
            "bowl": raw_data.get("bowl", "N/A"),
            "height": raw_data.get("height", "N/A"),
            "birthPlace": raw_data.get("birthPlace", "N/A"),
            "intlTeam": raw_data.get("intlTeam", "N/A"),
            "teams": raw_data.get("teams", []),
            "raw_data": raw_data
        }
        return profile

    # -------- Batting Stats --------
    def batterstat(player_id):
        endpoint = f"stats/v1/player/{player_id}/batting"
        data = fetch_api_data(endpoint)
        if not data:
            return pd.DataFrame()
        try:
            formats = data["headers"][1:]
            rows = data["values"][:7]
            tables = {}
            for ind, val in enumerate(formats):
                bat_stats = {}
                for row in rows:
                    label = row["values"][0]
                    value = row["values"][ind + 1]
                    bat_stats[label] = value
                tables[val] = bat_stats
            df = pd.DataFrame(tables).T.reset_index().rename(columns={"index": "Format"})
            return df
        except Exception:
            return pd.DataFrame()

    # -------- Bowling Stats --------
    def bowlerstat(player_id):
        endpoint = f"stats/v1/player/{player_id}/bowling"
        data = fetch_api_data(endpoint)
        if not data:
            return pd.DataFrame()
        try:
            formats = data["headers"][1:]
            rows = data["values"][:5]
            tables = {}
            for ind, val in enumerate(formats):
                bowl_stats = {}
                for row in rows:
                    label = row["values"][0]
                    value = row["values"][ind + 1]
                    bowl_stats[label] = value
                tables[val] = bowl_stats
            df = pd.DataFrame(tables).T.reset_index().rename(columns={"index": "Format"})
            return df
        except Exception:
            return pd.DataFrame()

    # -------- Streamlit Layout --------
    st.title("🏏 Cricket Player Search & Profile")
    st.markdown("---")

    player_name_input = st.text_input("Enter player name (e.g., Dhoni, Kohli, Rohit):")

    if player_name_input:
        with st.spinner("Searching for players..."):
            players_list = fetch_player_search(player_name_input)

        if players_list:
            display_options = [f"{p['player_name']} ({p['player_team']})" for p in players_list]
            selected_option = st.selectbox("Select a player:", display_options)

            if selected_option:
                idx = display_options.index(selected_option)
                selected_player = players_list[idx]

                # Top-level info
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.success(f"**NAME:** {selected_player['player_name']}")
                with col2:
                    st.success(f"**TEAM:** {selected_player['player_team']}")
                with col3:
                    st.success(f"**DOB:** {selected_player['player_dob']}")

                st.markdown("---")

                # Tabs
                tabs = ["**PLAYER INFO**", "**BATTING RECORD**", "**BOWLING RECORD**"]
                tab_info, tab_bat, tab_bowl = st.tabs(tabs)

                # Player Info
                with tab_info:
                    profile = player_profile(selected_player["player_id"])
                    st.subheader("📋 Player Details")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Name", profile["name"])
                    with col2:
                        st.metric("Nickname", profile["nickName"])
                    with col3:
                        st.metric("Birth Place", profile["birthPlace"])

                    col4, col5, col6 = st.columns(3)
                    with col4:
                        st.markdown("**Role**")
                        st.info(profile["role"])
                    with col5:
                        st.markdown("**Batting Style**")
                        st.info(profile["bat"])
                    with col6:
                        st.markdown("**Bowling Style**")
                        st.info(profile["bowl"])

                    col7, col8 = st.columns(2)
                    with col7:
                        st.write("**International Team:**")
                        st.info(profile["intlTeam"])
                    with col8:
                        st.write("**Domestic Teams:**")
                        st.info(profile["teams"])

                # Batting Tab
                with tab_bat:
                    df_bat = batterstat(selected_player["player_id"])
                    if not df_bat.empty:
                        st.subheader("📊 Batting Record")
                        st.dataframe(df_bat, use_container_width=True)
                    else:
                        st.warning("No batting statistics found.")

                # Bowling Tab
                with tab_bowl:
                    df_bowl = bowlerstat(selected_player["player_id"])
                    if not df_bowl.empty:
                        st.subheader("🎯 Bowling Record")
                        st.dataframe(df_bowl, use_container_width=True)
                    else:
                        st.warning("No bowling statistics found.")
