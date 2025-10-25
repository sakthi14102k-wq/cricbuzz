# pages/crud_operations.py - Perform CRUD on player stats

import streamlit as st
import pandas as pd
import mysql.connector as my
from utils.db_connection import get_connection

def show():
    """Display CRUD operations interface"""
    
    st.title("🛠️ CRUD OPERATION ZONE")
    st.markdown("---")
    
    # ========== SHOW TABLE FIRST ==========
    st.subheader("📊 Current Top Batting Stats Table")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM top_batting_stats LIMIT 20")
        table_data = cursor.fetchall()
        
        columns = [col[0] for col in cursor.description]
        cursor.close()
        conn.close()
        if st.button("SHOW PLAYERS"):
            if table_data:
                df = pd.DataFrame(table_data, columns=columns)
                st.dataframe(df, use_container_width=True)
                st.info(f"📌 Total records shown: {len(table_data)} (Displaying first 20)")
            else:
                st.warning("⚠️ Table is empty")
    except Exception as e:
        st.error(f"❌ Error fetching table: {str(e)}")
    
    st.markdown("---")
    
    # ========== CRUD OPERATIONS ==========
    crud_choice = st.radio("Choose action:", [
        "➕ Create a Player",
        "📖 Read/View Players",
        "✏️ Update Player",
        "🗑️ Delete Player"
    ], horizontal=True)

    # ========== CREATE A PLAYER ==========
    if crud_choice == "➕ Create a Player":
        st.subheader("➕ Add New Player Record")
        
        col1, col2 = st.columns(2)
        
        with col1:
            player_id = st.number_input("Player ID", min_value=1, step=1, value=1)
            player_name = st.text_input("Player Name")
            match_format = st.selectbox("Match Format", ["odi", "test", "t20"])
        
        with col2:
            matches = st.number_input("Matches", min_value=0, step=1, value=0)
            innings = st.number_input("Innings", min_value=0, step=1, value=0)
            runs = st.number_input("Runs", min_value=0, step=1, value=0)
            average = st.number_input("Average", min_value=0.0, step=0.01, value=0.0, format="%.2f")
        
        if st.button("✅ Add Player", type="primary"):
            if player_name:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO top_batting_stats 
                        (playerId, playerName, matchFormat, matches, innings, runs, average) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (player_id, player_name, match_format, matches, innings, runs, average))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success(f"✅ Player {player_name} added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please enter player name")

    # ========== READ/VIEW PLAYERS ==========
    elif crud_choice == "📖 Read/View Players":
        st.subheader("📖 View Players")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            format_filter = st.selectbox("Filter by Format:", ["All", "odi", "test", "t20"])
        with col2:
            limit = st.number_input("Number of records:", min_value=5, max_value=100, value=20, step=5)
        
        if st.button("🔍 Fetch Players", type="primary"):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                if format_filter == "All":
                    query = f"SELECT * FROM top_batting_stats LIMIT {limit}"
                    cursor.execute(query)
                else:
                    query = f"SELECT * FROM top_batting_stats WHERE matchFormat = %s LIMIT {limit}"
                    cursor.execute(query, (format_filter,))
                
                read_players = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                cursor.close()
                conn.close()

                if read_players:
                    df = pd.DataFrame(read_players, columns=columns)
                    st.dataframe(df, use_container_width=True)
                    st.success(f"✅ Found {len(read_players)} records")
                else:
                    st.warning("⚠️ No players found")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    # ========== UPDATE PLAYER ==========
    elif crud_choice == "✏️ Update Player":
        st.subheader("✏️ Update Player Details")

        search_name = st.text_input("🔍 Enter Player Name to Search", "")

        if "player_data" not in st.session_state:
            st.session_state.player_data = None

        if st.button("🔍 Search Player"):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT playerId, playerName, matchFormat, matches, innings, runs, average 
                    FROM top_batting_stats 
                    WHERE playerName LIKE %s
                """, (f"%{search_name}%",))
                players = cursor.fetchall()
                cursor.close()
                conn.close()

                if players:
                    st.session_state.player_data = players
                    st.success(f"✅ Found {len(players)} player(s)")
                else:
                    st.session_state.player_data = None
                    st.error("❌ Player not found!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                
        if st.session_state.player_data:
            # Show all matching players
            player_options = [f"{p[1]} - {p[2]} (ID: {p[0]})" for p in st.session_state.player_data]
            selected_player = st.selectbox("Select player to update:", player_options)
            
            # Get the selected player's index
            selected_idx = player_options.index(selected_player)
            player_id, old_name, old_format, old_matches, old_innings, old_runs, old_avg = st.session_state.player_data[selected_idx]

            # Show current data
            st.info("📋 Current Data:")
            df_current = pd.DataFrame([{
                "Player ID": player_id,
                "Player Name": old_name,
                "Format": old_format,
                "Matches": old_matches,
                "Innings": old_innings,
                "Runs": old_runs,
                "Average": old_avg
            }])
            st.dataframe(df_current, use_container_width=True)

            st.markdown("### ✏️ Update Fields:")
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Player Name", old_name)
                match_format = st.selectbox("Match Format", ["odi", "test", "t20"], 
                                           index=["odi", "test", "t20"].index(old_format) if old_format in ["odi", "test", "t20"] else 0)
                matches = st.number_input("Matches", min_value=0, value=int(old_matches) if old_matches else 0)
            
            with col2:
                innings = st.number_input("Innings", min_value=0, value=int(old_innings) if old_innings else 0)
                runs = st.number_input("Runs", min_value=0, value=int(old_runs) if old_runs else 0)
                avg = st.number_input("Average", min_value=0.0, value=float(old_avg) if old_avg else 0.0, format="%.2f")
                  
            if st.button("💾 Update Player", type="primary"):
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE top_batting_stats 
                        SET playerName=%s, matchFormat=%s, matches=%s, innings=%s, runs=%s, average=%s
                        WHERE playerId=%s
                    """, (name, match_format, matches, innings, runs, avg, player_id))
                    conn.commit()
                    cursor.close()
                    conn.close()

                    st.success(f"✅ Player {search_name} updated successfully!")
                    st.session_state.player_data = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    # ========== DELETE PLAYER ==========
    elif crud_choice == "🗑️ Delete Player":
        st.subheader("🗑️ Delete Player")

        search_name = st.text_input("🔍 Enter Player Name to Search", "")

        if "player_data" not in st.session_state:
            st.session_state.player_data = None
            
        if st.button("🔍 Search Player"):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT playerId, playerName, matchFormat, matches, innings, runs, average 
                    FROM top_batting_stats 
                    WHERE playerName LIKE %s
                """, (f"%{search_name}%",))
                players = cursor.fetchall()
                cursor.close()
                conn.close()

                if players:
                    st.session_state.player_data = players
                    st.success(f"✅ Found {len(players)} player(s)")
                else:
                    st.session_state.player_data = None
                    st.error("❌ Player not found!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                
        if st.session_state.player_data:
            # Show all matching players
            player_options = [f"{p[1]} - {p[2]} (ID: {p[0]})" for p in st.session_state.player_data]
            selected_player = st.selectbox("Select player to delete:", player_options)
            
            # Get the selected player's index
            selected_idx = player_options.index(selected_player)
            player_id, old_name, old_format, old_matches, old_innings, old_runs, old_avg = st.session_state.player_data[selected_idx]

            # Show data to be deleted
            st.warning("⚠️ Player to be deleted:")
            df_delete = pd.DataFrame([{
                "Player ID": player_id,
                "Player Name": old_name,
                "Format": old_format,
                "Matches": old_matches,
                "Innings": old_innings,
                "Runs": old_runs,
                "Average": old_avg
            }])
            st.dataframe(df_delete, use_container_width=True)
            
            st.error("⚠️ This action cannot be undone!")
            
            if st.button("🗑️ CONFIRM DELETE", type="primary"):
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM top_batting_stats WHERE playerId=%s", (player_id,))
                    conn.commit()
                    cursor.close()
                    conn.close()

                    st.success(f"✅ Player {old_name} was removed successfully!")
                    st.session_state.player_data = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
