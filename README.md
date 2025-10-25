# README.md - Project overview and setup instructions

# 🏏 Cricbuzz LiveStats Dashboard

A dynamic, interactive cricket analytics web application that combines live data from the Cricbuzz API with SQL database analytics.

## 📋 Project Overview

**Cricbuzz LiveStats** is a comprehensive cricket analytics dashboard that provides:
- ⚡ Real-time match updates
- 📊 Detailed player statistics
- 🔍 SQL-driven analytics with 25+ pre-built queries
- 🛠️ Full CRUD operations for data management
- 🌐 Interactive Streamlit web interface

## 🛠️ Technology Stack

- **Frontend:** Streamlit
- **Backend:** Python, Pandas
- **Database:** MySQL
- **APIs:** Cricbuzz API (via RapidAPI)

## 📁 Project Structure

```
cricbuzz_livestats/
├── app.py                          # Main entry point
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
│
├── pages/                          # Streamlit pages
│   ├── home.py                     # Overview and About
│   ├── live_matches.py             # Live match data
│   ├── top_stats.py                # Player statistics
│   ├── sql_queries.py              # SQL analytics interface
│   └── crud_operations.py          # CRUD operations
│
├── utils/                          # Utility files
│   └── db_connection.py            # Database connection
│
└── notebooks/                      # Practice notebooks (Optional)
    └── data_fetching.ipynb         # API testing
```


## 📊 Features

### 1. Home Page
- Project overview and documentation
- Feature descriptions
- Technology stack information

### 2. Live Match Page
- Real-time scoreboards
- Live match status
- Detailed batting & bowling information
- Venue details

### 3. Top Player Stats
- Player search functionality
- Comprehensive player profiles
- Batting and bowling statistics
- Career records across formats

### 4. SQL Queries & Analytics
- 25+ pre-built SQL queries
- Beginner to advanced analytics
- Interactive query execution
- Data-driven insights

### 5. CRUD Operations
- Create new player records
- View all players
- Update player information
- Delete player records

## 🎯 Core Skills Demonstrated

- **Python Programming** 🐍
- **SQL Database Management** 💾
- **Streamlit Web Development** ⚙️
- **REST API Integration** 🌐
- **JSON Data Processing** 📄
- **Sports Analytics** 🏏

## 📝 Usage

1. **Navigate** using the sidebar menu
2. **Select** the desired page
3. **Interact** with filters, search boxes, and buttons
4. **View** real-time data and analytics


