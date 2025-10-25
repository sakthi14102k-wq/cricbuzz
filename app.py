# app.py - Main entry point for the Streamlit app

import streamlit as st
import mysql.connector as my
import pandas as pd
import requests

# Import pages
from pages import home, live_matches, top_stats, sql_queries, crud_operations
from utils.db_connection import get_connection

# Streamlit Menu page
operation_choice = st.sidebar.selectbox("Choose Menu:", [
    "Home Page",
    "Live Match Page",
    "Top Player Stats Page",
    "SQL Queries & Analytics Page",
    "CRUD Operations Page",
])

# Route to appropriate page
if operation_choice == "Home Page":
    home.show()

elif operation_choice == "Live Match Page":
    live_matches.show()

elif operation_choice == "Top Player Stats Page":
    top_stats.show()

elif operation_choice == "SQL Queries & Analytics Page":
    sql_queries.show()

elif operation_choice == "CRUD Operations Page":
    crud_operations.show()