import streamlit as st

def show():
    # Main title and description
    st.markdown("## Welcome to Cricbuzz LiveStats Dashboard!🏏")
    
    home_choice = [
        "About project",
        "Live Match",
        "Top Player Stats",
        "SQL Queries & Analytics",
        "CRUD Operations ",
        "Project Information"
    ]
    
    tab_about, tab_live, tab_stats, tab_sql, tab_crud, tab_proinfo = st.tabs(home_choice)

    with tab_about:
        st.header("About Project")
        st.markdown("""
                ### 🏏Project Overview
                **Cricbuzz LiveStats** is a dynamic, interactive web application that serves as a complete cricket analytics dashboard.
                It seamlessly fuses live data pulled directly from the Cricbuzz API with a robust **SQL database**, allowing users to
                explore and analyze real-time match statistics.
                🎯 Core Objectives & Deliverables
                - ⚡ **Real-time match updates**
                - 📊 **Detailed player statistics** 
                - 🔍 **SQL-driven analytics**
                - 🛠️ **Full CRUD operations** for data management
                - 🌐 **Interactive Web App**
                """)
                
    with tab_live:
        st.header("🏏 Live Match")
        st.markdown(""" This page provide **real-time updates** and detailed data for matches currently **in progress**,
                    sourced directly from the Cricbuzz API.""")
        st.markdown("""
                    -⚡ **Real-time Scorecards**

                    -📊 **Live Match Status**

                    -🔍 **Detailed Batting & Bowling Info**

                    -🏟️ **Venue Details**
                    """)
    
    with tab_stats:
        st.header("📊 Top Player Stats")
        st.markdown(""" This page showcases the leading performers in the world of cricket,
                     drawing comprehensive **statistical data** directly from the Cricbuzz API.""")         
        st.markdown("""
                     🔎 **Search players by name**
                    
                    🏆 **Leaderboards**

                    🔢 **Key Metrics**: Batting 🏏,Bowling 📉
                    
                    👤**View comprehensive player profiles**
                    """)

    with tab_sql:
        st.header("🔍 SQL Queries & Analytics")
        st.markdown(""" This dedicated section serves as a **SQL analytical interface** where users 
                    can leverage the depth of the SQL database for advanced cricket insights.""")
        st.markdown("""
                    🔢 **25+ pre-built SQL queries** for immediate analysis.
                    
                    ⭐ **Beginner to advanced difficulty levels** to cater to all analytical skill sets.

                    ▶️ **Interactive query execution** with direct output display within the dashboard.
                    """)
        
    with tab_crud:
        st.header("🛠️ CRUD Operations")
        st.markdown("""This page provides an administrative interface for **demonstrating and 
                    practicing full database manipulation** using the dedicated SQL """)
        st.markdown("""
                    🆕 **Create new player records**

                    📚 **View all players in database**
                    
                    ✏️ **Update existing player information**

                    🗑️ **Delete player records safely**
                    """)

    with tab_proinfo:
        st.header("📋Project Information: Cricbuzz LiveStats📊")
        st.subheader("""🛠️ Technology Stack""")
        st.markdown("""
                    
                    **Frontend**    ---     🖥️**Streamlit**

                    **Backend**     ---     🐍**Python** • **Pandas**

                    **Database**    ---     🗄️**MySQL**

                    **APIs**        ---     🔗**Cricbuzz API**
                    """)
        st.markdown("""
                    
                    **Core Skills Demonstrated**:

                     **Python** 🐍 
                    
                     **SQL** 💾 
                    
                     **Streamlit** ⚙️ 
                    
                     **JSON** 📄 
                    
                     **REST API** 🌐
                    
                     Domain: **Sports Analytics** 🏏

                    """)

