import streamlit as st
import pandas as pd
import mysql.connector as my
from utils.db_connection import get_connection

def show():
    """Display SQL queries and analytics interface"""
    
    st.title("🔍 SQL Queries & Analytics")
    
    # ----------------------
    # Questions List
    # ----------------------
    questions = [
        "Q1:Players from India: name, role, bat, bowl style",
        "Q2:Recent matches: desc, teams, venue, date, sort recent",
        "Q3:Top 10 ODI run scorers: name, runs, avg",
        "Q4:Venues >30k: name, city, country, capacity, sort large",
        "Q5:Team wins: name, win count, sort most wins",
        "Q6:Player roles: role, count",
        "Q7:Highest score: format, score",
        "Q8:2024 series: name, host, type, date, match count",
        "Q9:All-rounders: >1000 runs & >50 wickets",
        "Q10:Last 20 matches: desc, teams, winner, margin, venue",
        "Q11:Player format compare: Test/ODI/T20 runs, overall avg",
        "Q12:Home vs away wins: team, win count",
        "Q13:Partnerships >100 (adjacent bats): names, runs, innings",
        "Q14:Bowler venue stats: economy, wickets, matches",
        "Q15:Close matches: player avg runs, matches, wins",
        "Q16:Yearly stats: avg runs, strike rate, year, ≥5 matches",
        "Q17:Toss win %: by decision (bat/bowl first)",
        "Q18:Economical bowlers: ODI/T20, economy, wickets",
        "Q19:Consistent batsmen: avg runs, std dev",
        "Q20:Matches & avg: Test, ODI, T20 (≥20 all formats)",
        "Q21:Player ranking: weighted bat/bowl/field score",
        "Q22:Head-to-head: matches, wins, margin, conditions, win%",
        "Q23:Recent form: last 10, avg runs, strike rate, 50+, const, form type",
        "Q24:Best partnerships: avg, 50+, highest, success rate",
        "Q25:Trends: runs, rate, up/down/stable, trajectory"
    ]
    
    selected_question = st.selectbox("Select a query:", questions)
    
    # ----------------------
    # SQL Queries Mapping
    # ----------------------
    queries = {
        "Q1:Players from India: name, role, bat, bowl style": """
            SELECT 
                full_name AS player_name,
                playing_role AS role,
                batting_style,
                bowling_style
            FROM players
            WHERE country = 'India';
        """,

        "Q2:Recent matches: desc, teams, venue, date, sort recent": """
            SELECT 
                match_id,
                team1,
                team2,
                venue,
                match_date,
                format
            FROM combined_matches
            ORDER BY match_date DESC
            LIMIT 20;
        """,

        "Q3:Top 10 ODI run scorers: name, runs, avg": """
            SELECT 
                playerName,
                matches,
                runs,
                average
            FROM top_batting_stats
            WHERE matchFormat = 'ODI'
            ORDER BY runs DESC
            LIMIT 10;
        """,

        "Q4:Venues >30k: name, city, country, capacity, sort large": """
            SELECT 
                venue_name AS stadium_name,
                city,
                country,
                capacity
            FROM venues
            WHERE capacity > 30000
            ORDER BY capacity DESC;
        """,

        "Q5:Team wins: name, win count, sort most wins": """
            SELECT 
                match_winner AS team_name,
                COUNT(*) AS total_wins
            FROM combined_matches
            GROUP BY team_name
            ORDER BY total_wins DESC;
        """,

        "Q6:Player roles: role, count": """
            SELECT 
                playing_role,
                COUNT(*) AS player_count
            FROM players
            GROUP BY playing_role;
        """,

        "Q7:Highest score: format, score": """
            SELECT 
                playerName,
                matchFormat,
                MAX(runs) AS highestScore
            FROM top_batting_stats
            WHERE matchFormat IN ('test', 'odi', 't20')
            GROUP BY playerName, matchFormat
            ORDER BY highestScore DESC;
        """,

        "Q8:2024 series: name, host, type, date, match count": """
            SELECT 
                series_name AS series,
                venue AS venue_name,
                match_format AS format,
                start_date AS match_date
            FROM series_matches
            WHERE YEAR(start_date) = 2024
            ORDER BY match_date;
        """,

        "Q9:All-rounders: >1000 runs & >50 wickets": """
            SELECT 
                name AS player,
                total_runs AS RUNS,
                total_wickets AS WICKETS
            FROM players
            WHERE total_runs > 1000
            AND total_wickets > 50;
        """,

        "Q10:Last 20 matches: desc, teams, winner, margin, venue": """
            SELECT 
                series_name,
                format,
                team1,
                team2,
                match_winner,
                win_margin,
                CASE 
                    WHEN win_margin LIKE '%runs%' THEN 'Runs'
                    WHEN win_margin LIKE '%wkts%' OR win_margin LIKE '%wickets%' THEN 'Wickets'
                    ELSE 'Other'
                END AS victory_type,
                venue
            FROM combined_matches
            WHERE match_winner IS NOT NULL 
            AND match_winner <> 'Match drawn'
            ORDER BY match_id DESC
            LIMIT 20;
        """,

        "Q11:Player format compare: Test/ODI/T20 runs, overall avg": """
            SELECT
                player_id,
                player_name,
                role,
                test_runs,
                odi_runs,
                t20_runs,
                (CASE WHEN test_runs > 0 THEN 1 ELSE 0 END +
                CASE WHEN odi_runs > 0 THEN 1 ELSE 0 END +
                CASE WHEN t20_runs > 0 THEN 1 ELSE 0 END) AS formats_played,
                (IFNULL(test_runs,0) + IFNULL(odi_runs,0) + IFNULL(t20_runs,0)) AS total_runs,
                ROUND(
                    (IFNULL(test_runs,0) + IFNULL(odi_runs,0) + IFNULL(t20_runs,0)) /
                    (CASE WHEN test_runs > 0 THEN 1 ELSE 0 END +
                    CASE WHEN odi_runs > 0 THEN 1 ELSE 0 END +
                    CASE WHEN t20_runs > 0 THEN 1 ELSE 0 END),
                    2
                ) AS overall_batting_average
            FROM players_stats
            WHERE (
                (CASE WHEN test_runs > 0 THEN 1 ELSE 0 END +
                CASE WHEN odi_runs > 0 THEN 1 ELSE 0 END +
                CASE WHEN t20_runs > 0 THEN 1 ELSE 0 END) >= 2
            );
        """,

        "Q12:Home vs away wins: team, win count": """
            SELECT 
                team,
                home_or_away,
                COUNT(*) AS total_wins
            FROM (
                SELECT 
                    team1 AS team,
                    CASE 
                        WHEN status LIKE CONCAT(team1, ' won%')
                            AND series_name LIKE CONCAT('%tour of ', team1, '%') THEN 'Home'
                        WHEN status LIKE CONCAT(team1, ' won%') THEN 'Away'
                    END AS home_or_away
                FROM series_matches
                WHERE status LIKE '%won%'

                UNION ALL

                SELECT 
                    team2 AS team,
                    CASE 
                        WHEN status LIKE CONCAT(team2, ' won%')
                            AND series_name LIKE CONCAT('%tour of ', team2, '%') THEN 'Home'
                        WHEN status LIKE CONCAT(team2, ' won%') THEN 'Away'
                    END AS home_or_away
                FROM series_matches
                WHERE status LIKE '%won%'
            ) AS results
            WHERE home_or_away IS NOT NULL
            GROUP BY team, home_or_away
            ORDER BY team, home_or_away;
        """,

        "Q13:Partnerships >100 (adjacent bats): names, runs, innings": """
            SELECT 
                p1.match_id,
                p1.innings_no,
                p1.batter1_name AS batter1,
                p1.batter2_name AS batter2,
                p1.runs_partnership + p2.runs_partnership AS combined_runs
            FROM partnerships_data p1
            JOIN partnerships_data p2
                ON p1.match_id = p2.match_id
            AND p1.innings_no = p2.innings_no
            AND p1.wicket_fallen + 1 = p2.wicket_fallen
            WHERE (p1.runs_partnership + p2.runs_partnership) >= 100
            ORDER BY p1.match_id, p1.innings_no, p1.wicket_fallen;
        """,

        "Q14:Bowler venue stats: economy, wickets, matches": """
            SELECT 
                player_name,
                venue,
                COUNT(DISTINCT match_id) AS matches_played,
                SUM(wickets) AS total_wickets,
                ROUND(AVG(economy_rate), 2) AS avg_economy_rate
            FROM bowling_record
            WHERE overs >= 4
            GROUP BY player_name, venue
            HAVING COUNT(DISTINCT match_id) >= 2
            ORDER BY total_wickets desc;
        """,

        "Q15:Close matches: player avg runs, matches, wins": """
            WITH close_matches AS (
                SELECT 
                    match_id, team1, team2, match_winner, win_margin
                FROM combined_matches
                WHERE match_winner IS NOT NULL
                AND win_margin NOT LIKE '%drawn%'
                AND (
                        (win_margin LIKE '%runs%' AND win_margin NOT LIKE '%innings%'
                        AND CAST(REGEXP_REPLACE(win_margin, '[^0-9]', '') AS UNSIGNED) < 50)
                        OR
                        (win_margin LIKE '%wkt%'
                        AND CAST(REGEXP_REPLACE(win_margin, '[^0-9]', '') AS UNSIGNED) < 5)
                    )
            ),
            player_batting_in_close_matches AS (
                SELECT 
                    s.player_id, 
                    s.player_name, 
                    s.match_id, 
                    s.runs,
                    cm.match_winner, 
                    cm.team1, 
                    cm.team2,
                    CASE 
                        WHEN cm.match_winner = cm.team1 OR cm.match_winner = cm.team2 THEN 1 
                        ELSE 0 
                    END AS team_won_when_batted
                FROM scoreboard s
                INNER JOIN close_matches cm 
                    ON s.match_id = cm.match_id
                WHERE s.record_type = 'batsman' 
                AND s.runs IS NOT NULL
            ),
            player_stats AS (
                SELECT 
                    player_id, 
                    player_name,
                    COUNT(DISTINCT match_id) AS total_close_matches_played,
                    ROUND(AVG(runs), 2) AS avg_runs_in_close_matches,
                    SUM(team_won_when_batted) AS close_matches_won_when_batted,
                    ROUND(SUM(team_won_when_batted) * 100.0 / COUNT(DISTINCT match_id), 2) AS win_percentage_when_batted,
                    SUM(runs) AS total_runs_in_close_matches
                FROM player_batting_in_close_matches
                GROUP BY player_id, player_name
                HAVING COUNT(DISTINCT match_id) >= 2
            )
            SELECT 
                player_id,
                player_name AS full_name,
                total_close_matches_played,
                avg_runs_in_close_matches,
                close_matches_won_when_batted,
                win_percentage_when_batted,
                total_runs_in_close_matches
            FROM player_stats
            ORDER BY avg_runs_in_close_matches DESC, 
                    win_percentage_when_batted DESC,
                    total_close_matches_played DESC;
        """,

        "Q16:Yearly stats: avg runs, strike rate, year, ≥5 matches": """
            SELECT
                playerId,
                playerName,
                SUM(matches) AS total_matches_2020_2025,
                SUM(runs) AS total_runs_2020_2025,
                (SUM(runs) / SUM(matches)) AS average_runs_per_match
            FROM
                stats_of_player
            WHERE
                year BETWEEN 2020 AND 2025
            GROUP BY
                playerId, playerName
            HAVING
                total_matches_2020_2025 > 5
            ORDER BY
                average_runs_per_match DESC;
        """,

        "Q17:Toss win %: by decision (bat/bowl first)": """
            SELECT 
                toss_decision AS 'Toss Decision',
                COUNT(*) AS 'Total Matches',
                SUM(CASE WHEN toss_winner = match_winner THEN 1 ELSE 0 END) AS 'Matches Won by Toss Winner',
                ROUND(
                    (SUM(CASE WHEN toss_winner = match_winner THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 
                    2
                ) AS 'Toss Advantage %'
            FROM combined_matches
            WHERE match_winner IS NOT NULL 
            AND match_winner NOT IN ('Match drawn', 'No result')
            AND toss_decision IN ('Batting', 'Bowling')
            GROUP BY toss_decision
            ORDER BY `Toss Advantage %` DESC;
        """,

        "Q18:Economical bowlers: ODI/T20, economy, wickets": """
            SELECT
                playerId,
                playerName,
                SUM(CASE WHEN match_format = 'ODI' THEN matches ELSE 0 END) AS odi_matches,
                SUM(CASE WHEN match_format = 'ODI' THEN wickets ELSE 0 END) AS odi_wickets,
                CASE 
                    WHEN SUM(CASE WHEN match_format = 'ODI' THEN wickets ELSE 0 END) > 0 
                    THEN SUM(CASE WHEN match_format = 'ODI' THEN average * wickets ELSE 0 END) /
                        SUM(CASE WHEN match_format = 'ODI' THEN wickets ELSE 0 END)
                    ELSE 0
                END AS odi_average,
                SUM(CASE WHEN match_format = 'T20' THEN matches ELSE 0 END) AS t20_matches,
                SUM(CASE WHEN match_format = 'T20' THEN wickets ELSE 0 END) AS t20_wickets,
                CASE
                    WHEN SUM(CASE WHEN match_format = 'T20' THEN wickets ELSE 0 END) > 0 
                    THEN SUM(CASE WHEN match_format = 'T20' THEN average * wickets ELSE 0 END) /
                        SUM(CASE WHEN match_format = 'T20' THEN wickets ELSE 0 END)
                    ELSE 0
                END AS t20_average
            FROM player_bowling_stats
            WHERE match_format IN ('ODI', 'T20')
            GROUP BY playerId, playerName
            HAVING SUM(CASE WHEN match_format = 'ODI' THEN matches ELSE 0 END) >= 10
            OR SUM(CASE WHEN match_format = 'T20' THEN matches ELSE 0 END) >= 10
            ORDER BY playerName;
        """,

        "Q19:Consistent batsmen: avg runs, std dev": """
            WITH player_innings AS (
                SELECT 
                    player_id, 
                    player_name, 
                    match_id, 
                    runs, 
                    balls_faced
                FROM batting_data
                WHERE balls_faced >= 10
            ),
            player_stats AS (
                SELECT 
                    player_id, 
                    player_name, 
                    COUNT(DISTINCT match_id) AS innings_played,
                    AVG(runs) AS avg_runs, 
                    STDDEV(runs) AS run_stddev
                FROM player_innings
                GROUP BY 
                    player_id, 
                    player_name
                HAVING COUNT(DISTINCT match_id) >= 2
            )
            SELECT 
                player_name, 
                innings_played, 
                ROUND(avg_runs, 2) AS avg_runs,
                ROUND(run_stddev, 2) AS run_stddev
            FROM player_stats
            ORDER BY 
                run_stddev ASC, 
                avg_runs ASC;
        """,

        "Q20:Matches & avg: Test, ODI, T20 (≥20 all formats)": """
            SELECT 
                playerId,
                playerName,
                CASE WHEN matchFormat = 'test' THEN matches ELSE 0 END AS total_test_matches,
                CASE WHEN matchFormat = 'test' THEN average ELSE NULL END AS test_batting_avg,
                CASE WHEN matchFormat = 'odi' THEN matches ELSE 0 END AS total_odi_matches,
                CASE WHEN matchFormat = 'odi' THEN average ELSE NULL END AS odi_batting_avg,
                CASE WHEN matchFormat = 't20' THEN matches ELSE 0 END AS total_t20_matches,
                CASE WHEN matchFormat = 't20' THEN average ELSE NULL END AS t20_batting_avg,
                SUM(matches) AS total_matches
            FROM top_batting_stats
            GROUP BY playerId, playerName
            HAVING SUM(matches) >= 20
            ORDER BY total_matches DESC;
        """,

        "Q21:Player ranking: weighted bat/bowl/field score": """
            SELECT
                id,
                match_id,
                player_id,
                player_name,
                runs,
                balls_faced,
                strike_rate,
                overs,
                runs_conceded,
                wickets,
                economy_rate,
                catches,
                stumpings,
                
                -- Batting average (avoids division by zero)
                CASE 
                    WHEN balls_faced > 0 THEN ROUND(runs / balls_faced, 2)
                    ELSE 0 
                END AS batting_average,

                -- Bowling average (avoids division by zero)
                CASE 
                    WHEN wickets > 0 THEN ROUND(runs_conceded / wickets, 2)
                    ELSE 0 
                END AS bowling_average,

                -- Total weighted performance points
                ROUND(
                    (
                        -- Batting points
                        (runs * 0.01)
                        + (
                            (CASE WHEN balls_faced > 0 THEN runs / balls_faced ELSE 0 END) * 0.5
                        )
                        + (strike_rate * 0.3)

                        -- Bowling points
                        + (wickets * 2)
                        + (
                            (50 - (CASE WHEN wickets > 0 THEN runs_conceded / wickets ELSE 0 END)) * 0.5
                        )
                        + ((6 - economy_rate) * 2)

                        -- Fielding points
                        + (catches * 1)
                        + (stumpings * 2)
                    ), 2
                ) AS total_points

            FROM
                player_performance

            ORDER BY
                total_points DESC;
        """,

        "Q22:Head-to-head: matches, wins, margin, conditions, win%": """
            -- Head-to-Head Stats: Matches, Wins, Average Victory Margin, Overall Win %
            SELECT
                LEAST(team1, team2) AS team_a,
                GREATEST(team1, team2) AS team_b,
                COUNT(*) AS matches_played,
                
                -- Wins for each team
                SUM(CASE WHEN status LIKE CONCAT(team1, ' won%') THEN 1 ELSE 0 END) AS team1_wins,
                SUM(CASE WHEN status LIKE CONCAT(team2, ' won%') THEN 1 ELSE 0 END) AS team2_wins,
                
                -- Average victory margin in runs
                AVG(CASE
                    WHEN status LIKE CONCAT(team1, ' won%runs') THEN team1_runs - team2_runs
                    WHEN status LIKE CONCAT(team2, ' won%runs') THEN team2_runs - team1_runs
                    ELSE NULL
                END) AS avg_victory_margin_runs,
                
                -- Average victory margin in wickets
                AVG(CASE
                    WHEN status LIKE CONCAT(team1, ' won%wkts') THEN team2_runs - team1_runs
                    WHEN status LIKE CONCAT(team2, ' won%wkts') THEN team1_runs - team2_runs
                    ELSE NULL
                END) AS avg_victory_margin_wkts,
                
                -- Win percentages
                ROUND(
                    100 * SUM(CASE WHEN status LIKE CONCAT(team1, ' won%') THEN 1 ELSE 0 END) / COUNT(*),
                2) AS team1_win_pct,
                
                ROUND(
                    100 * SUM(CASE WHEN status LIKE CONCAT(team2, ' won%') THEN 1 ELSE 0 END) / COUNT(*),
                2) AS team2_win_pct

            FROM
                series_matches_2022
            WHERE
                `state` = 'complete'
                AND startDate >= DATE_SUB(CURDATE(), INTERVAL 3 YEAR)
                AND team1 IS NOT NULL
                AND team2 IS NOT NULL
            GROUP BY
                LEAST(team1, team2),
                GREATEST(team1, team2)
            HAVING
                matches_played >= 5
            ORDER BY
                matches_played DESC,
                team_a,
                team_b;
        """,

        "Q23:Recent form: last 10, avg runs, strike rate, 50+, const, form type": """
            WITH ranked AS (
            SELECT
                *,
                ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY id DESC) AS rn
            FROM batting_data
            ),
            last10 AS (
            SELECT *
            FROM ranked
            WHERE rn <= 10
            ),
            last5 AS (
            SELECT *
            FROM ranked
            WHERE rn <= 5
            ),
            agg10 AS (
            SELECT
                player_id,
                player_name,
                AVG(runs) AS avg_runs_10,
                STDDEV(runs) AS stddev_runs_10,
                SUM(CASE WHEN runs >= 50 THEN 1 ELSE 0 END) AS num_50plus_10,
                AVG(strike_rate) AS avg_sr_10
            FROM last10
            GROUP BY player_id, player_name
            ),
            agg5 AS (
            SELECT
                player_id,
                AVG(runs) AS avg_runs_5,
                AVG(strike_rate) AS avg_sr_5
            FROM last5
            GROUP BY player_id
            )
            SELECT
            agg10.player_id,
            agg10.player_name,
            agg5.avg_runs_5,
            agg10.avg_runs_10,
            agg5.avg_sr_5,
            agg10.avg_sr_10,
            agg10.num_50plus_10,
            agg10.stddev_runs_10,
            CASE
                WHEN agg5.avg_runs_5 >= 50 AND agg10.stddev_runs_10 < 15 THEN 'Excellent Form'
                WHEN agg5.avg_runs_5 >= 35 AND agg10.stddev_runs_10 < 25 THEN 'Good Form'
                WHEN agg5.avg_runs_5 >= 20 THEN 'Average Form'
                ELSE 'Poor Form'
            END AS form_category
            FROM agg10
            JOIN agg5 ON agg10.player_id = agg5.player_id
            ORDER BY agg10.avg_runs_10 DESC;
        """,

        "Q24:Best partnerships: avg, 50+, highest, success rate": """
            WITH partnerships_tagged AS (
                SELECT
                    partnership_id,
                    match_id,
                    innings_no,
                    batter1_id,
                    batter2_id,
                    batter1_name,
                    batter2_name,
                    runs_partnership,
                    balls_faced,
                    wicket_fallen,
                    
                    wicket_fallen + 1 AS pos2,
                    wicket_fallen AS pos1
                FROM partnerships_data
            ),
            consecutive_batsmen_partnerships AS (
                SELECT
                    LEAST(batter1_id, batter2_id) AS player1_id,
                    GREATEST(batter1_id, batter2_id) AS player2_id,
                    LEAST(batter1_name, batter2_name) AS player1_name,
                    GREATEST(batter1_name, batter2_name) AS player2_name,
                    runs_partnership
                FROM partnerships_tagged
                WHERE
                    ABS(pos2 - pos1) = 1
            ),
            partnerships_aggregate AS (
                SELECT
                    player1_id,
                    player2_id,
                    player1_name,
                    player2_name,
                    COUNT(*) AS partnership_count,
                    AVG(runs_partnership) AS avg_partnership_runs,
                    SUM(CASE WHEN runs_partnership > 50 THEN 1 ELSE 0 END) AS partnerships_above_50,
                    MAX(runs_partnership) AS highest_partnership,
                    100.0 * SUM(CASE WHEN runs_partnership > 50 THEN 1 ELSE 0 END) / COUNT(*) AS success_rate
                FROM consecutive_batsmen_partnerships
                GROUP BY player1_id, player2_id, player1_name, player2_name
                HAVING COUNT(*) >= 5
            )
            SELECT
                player1_name,
                player2_name,
                partnership_count,
                avg_partnership_runs,
                partnerships_above_50,
                highest_partnership,
                success_rate
            FROM partnerships_aggregate;
        """,

        "Q25:Trends: runs, rate, up/down/stable, trajectory": """
            WITH yearly_data AS (
                SELECT
                    playerId,
                    playerName,
                    matchFormat,
                    team,
                    year,
                    SUM(matches) AS total_matches,
                    SUM(runs) AS total_runs,
                    AVG(average) AS avg_strike_rate   -- using 'average' as batting metric
                FROM crudtrail.stats_of_player
                WHERE matchFormat = 'odi'
                GROUP BY playerId, playerName, matchFormat, team, year
            ),
            performance_change AS (
                SELECT
                    playerId,
                    playerName,
                    year,
                    total_runs,
                    avg_strike_rate,
                    LAG(total_runs) OVER (PARTITION BY playerId ORDER BY year) AS prev_runs,
                    LAG(avg_strike_rate) OVER (PARTITION BY playerId ORDER BY year) AS prev_strike_rate
                FROM yearly_data
            ),
            trend_analysis AS (
                SELECT
                    playerId,
                    playerName,
                    year,
                    total_runs,
                    avg_strike_rate,
                    CASE 
                        WHEN prev_runs IS NULL THEN 'N/A'
                        WHEN total_runs > prev_runs AND avg_strike_rate > prev_strike_rate THEN 'Improving'
                        WHEN total_runs < prev_runs AND avg_strike_rate < prev_strike_rate THEN 'Declining'
                        ELSE 'Stable'
                    END AS year_trend
                FROM performance_change
            ),
            career_summary AS (
                SELECT
                    playerId,
                    playerName,
                    SUM(CASE WHEN year_trend = 'Improving' THEN 1 ELSE 0 END) AS improving_years,
                    SUM(CASE WHEN year_trend = 'Declining' THEN 1 ELSE 0 END) AS declining_years,
                    SUM(CASE WHEN year_trend = 'Stable' THEN 1 ELSE 0 END) AS stable_years,
                    COUNT(*) AS total_years
                FROM trend_analysis
                GROUP BY playerId, playerName
            ),
            career_phase AS (
                SELECT
                    playerId,
                    playerName,
                    CASE
                        WHEN improving_years > declining_years * 1.5 THEN 'Career Ascending'
                        WHEN declining_years > improving_years * 1.5 THEN 'Career Declining'
                        ELSE 'Career Stable'
                    END AS career_phase
                FROM career_summary
            )
            SELECT 
                t.playerId,
                t.playerName,
                t.year,
                t.total_runs,
                t.avg_strike_rate,
                t.year_trend,
                c.career_phase
            FROM trend_analysis t
            LEFT JOIN career_phase c USING (playerId, playerName)
            ORDER BY t.playerName, t.year;
        """
    }
    
    # ----------------------
    # Execute Query Button
    # ----------------------
    if st.button("▶️ Run Query", type="primary"):
        if selected_question in queries:
            try:
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
                
                with st.spinner("Executing query..."):
                    cursor.execute(queries[selected_question])
                    results = cursor.fetchall()
                
                cursor.close()
                conn.close()

                if results:
                    df = pd.DataFrame(results)
                    st.success(f"✅ Query executed successfully! Found {len(results)} records.")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("⚠️ No data found for this query.")
                    
            except Exception as e:
                st.error(f"❌ Error executing query: {str(e)}")
                st.info("💡 Make sure the required tables exist in your database.")
        else:
            st.error("Query not found!")
    
    # Show query preview
    with st.expander("👁️ View SQL Query"):
        if selected_question in queries:
            st.code(queries[selected_question], language="sql")