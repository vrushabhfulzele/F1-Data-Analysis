import streamlit as st
import fastf1
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="F1 Racing Analytics",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS - F1 STYLE
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Orbitron', sans-serif;
}

/* Main background */
.stApp {
    background:
        radial-gradient(circle at top right, rgba(225, 6, 0, 0.18), transparent 35%),
        radial-gradient(circle at bottom left, rgba(225, 6, 0, 0.10), transparent 30%),
        #080808;
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d0d, #151515);
    border-right: 1px solid #292929;
}

/* Hero */
.hero {
    background:
        linear-gradient(135deg, rgba(225,6,0,0.95), rgba(20,20,20,0.95)),
        repeating-linear-gradient(
            45deg,
            transparent,
            transparent 10px,
            rgba(255,255,255,0.03) 10px,
            rgba(255,255,255,0.03) 20px
        );
    padding: 35px;
    border-radius: 18px;
    margin-bottom: 25px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 15px 40px rgba(0,0,0,0.5);
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    letter-spacing: 3px;
    color: white;
}

.hero-subtitle {
    font-size: 15px;
    color: #dddddd;
    margin-top: 8px;
    letter-spacing: 1px;
}

.hero-badge {
    display: inline-block;
    margin-top: 18px;
    padding: 8px 18px;
    background: #111111;
    border: 1px solid #444;
    border-radius: 30px;
    font-size: 13px;
}

/* KPI Cards */
.kpi-card {
    background: linear-gradient(145deg, #151515, #0c0c0c);
    border: 1px solid #2d2d2d;
    border-left: 4px solid #e10600;
    border-radius: 14px;
    padding: 20px;
    min-height: 125px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.35);
    transition: all 0.3s ease;
}

.kpi-card:hover {
    transform: translateY(-5px);
    border-left-color: #ff2b20;
    box-shadow: 0 12px 35px rgba(225,6,0,0.2);
}

.kpi-title {
    font-size: 12px;
    color: #999;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.kpi-value {
    font-size: 30px;
    font-weight: 800;
    margin-top: 8px;
    color: white;
}

.kpi-subtitle {
    font-size: 11px;
    color: #777;
    margin-top: 5px;
}

/* Section headings */
.section-title {
    font-size: 22px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 15px;
    border-left: 4px solid #e10600;
    padding-left: 12px;
}

/* Select boxes */
div[data-baseweb="select"] > div {
    background-color: #161616 !important;
    border-color: #333 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #e10600, #b30500);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 700;
}

/* Dataframe */
div[data-testid="stDataFrame"] {
    border: 1px solid #333;
    border-radius: 10px;
}

/* Footer */
.footer {
    text-align: center;
    color: #666;
    font-size: 11px;
    padding: 25px;
    margin-top: 40px;
    border-top: 1px solid #222;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# FASTF1 CACHE
# ============================================================

fastf1.Cache.enable_cache("fastf1_cache")


# ============================================================
# LOAD 2025 RACE DATA
# ============================================================

@st.cache_data(show_spinner=False)
def load_f1_data():

    schedule = fastf1.get_event_schedule(2025)

    schedule = schedule[
        [
            "RoundNumber",
            "Country",
            "Location",
            "EventDate",
            "EventName"
        ]
    ]

    results = []

    progress_bar = st.progress(0)

    race_schedule = schedule[
        schedule["RoundNumber"] > 0
    ].copy()

    total_races = len(race_schedule)

    for index, row in race_schedule.iterrows():

        round_number = int(row["RoundNumber"])

        try:

            session = fastf1.get_session(
                2025,
                round_number,
                "R"
            )

            session.load(
                telemetry=False,
                weather=False,
                messages=False
            )

            race_results = session.results

            if race_results.empty:
                continue

            columns = [
                "DriverNumber",
                "Abbreviation",
                "FullName",
                "TeamName",
                "Position",
                "Points",
                "Status",
                "Laps",
                "Time"
            ]

            available_columns = [
                col for col in columns
                if col in race_results.columns
            ]

            race_results = race_results[available_columns].copy()

            race_results["Round"] = round_number
            race_results["Venue"] = row["Location"]
            race_results["Country"] = row["Country"]
            race_results["EventName"] = row["EventName"]
            race_results["EventDate"] = row["EventDate"]

            results.append(race_results)

            progress_bar.progress(
                min(
                    int((len(results) / total_races) * 100),
                    100
                )
            )

        except Exception:
            continue

    progress_bar.empty()

    if not results:
        return pd.DataFrame(), schedule

    final = pd.concat(
        results,
        ignore_index=True
    )

    final["Position"] = pd.to_numeric(
        final["Position"],
        errors="coerce"
    )

    final["Points"] = pd.to_numeric(
        final["Points"],
        errors="coerce"
    ).fillna(0)

    final["Laps"] = pd.to_numeric(
        final["Laps"],
        errors="coerce"
    ).fillna(0)

    final["EventDate"] = pd.to_datetime(
        final["EventDate"],
        errors="coerce"
    )

    final = final.sort_values(
        ["Round", "Position"]
    )

    return final, schedule


# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="hero">

    <div class="hero-title">
        🏎️ FORMULA 1
    </div>

    <div class="hero-subtitle">
        2025 RACING ANALYTICS & CHAMPIONSHIP INTELLIGENCE
    </div>

    <div class="hero-badge">
        🔴 FASTF1 • RACE DATA • PERFORMANCE ANALYTICS
    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# LOAD DATA
# ============================================================

with st.spinner("🏁 Loading Formula 1 race data..."):

    final, schedule = load_f1_data()


if final.empty:

    st.error(
        "Unable to load Formula 1 data. "
        "Please check your internet connection and try again."
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "## 🏎️ F1 CONTROL CENTER"
)

st.sidebar.markdown(
    "---"
)

# Driver selector
drivers = sorted(
    final["FullName"]
    .dropna()
    .unique()
)

selected_driver = st.sidebar.selectbox(
    "👤 Select Driver",
    ["All Drivers"] + drivers
)

# Race selector
venues = list(
    final[
        ["Round", "Venue", "EventName"]
    ]
    .drop_duplicates()
    .sort_values("Round")["Venue"]
)

selected_venue = st.sidebar.selectbox(
    "🏁 Select Race",
    ["All Races"] + venues.tolist()
)

# Team selector
teams = sorted(
    final["TeamName"]
    .dropna()
    .unique()
)

selected_team = st.sidebar.selectbox(
    "🏢 Select Team",
    ["All Teams"] + teams
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    """
### 📊 Dashboard Features

- 🏆 Championship Standings
- 👤 Driver Analytics
- 🏢 Team Performance
- 🏁 Race Analysis
- 📈 Points Progression
- 📊 Interactive Charts
"""
)


# ============================================================
# FILTER DATA
# ============================================================

filtered = final.copy()

if selected_driver != "All Drivers":

    filtered = filtered[
        filtered["FullName"] == selected_driver
    ]

if selected_venue != "All Races":

    filtered = filtered[
        filtered["Venue"] == selected_venue
    ]

if selected_team != "All Teams":

    filtered = filtered[
        filtered["TeamName"] == selected_team
    ]


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_races = final["Round"].nunique()

total_drivers = final["FullName"].nunique()

total_teams = final["TeamName"].nunique()

total_points = filtered["Points"].sum()

wins = (
    filtered["Position"] == 1
).sum()

podiums = (
    filtered["Position"] <= 3
).sum()


# ============================================================
# KPI CARDS
# ============================================================

st.markdown(
    '<div class="section-title">📊 Season Overview</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Races</div>
            <div class="kpi-value">{total_races}</div>
            <div class="kpi-subtitle">2025 Season</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Drivers</div>
            <div class="kpi-value">{total_drivers}</div>
            <div class="kpi-subtitle">Participants</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Teams</div>
            <div class="kpi-value">{total_teams}</div>
            <div class="kpi-subtitle">Constructors</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Points</div>
            <div class="kpi-value">{total_points:.0f}</div>
            <div class="kpi-subtitle">Selected Filter</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c5:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Wins</div>
            <div class="kpi-value">{wins}</div>
            <div class="kpi-subtitle">Race Victories</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c6:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Podiums</div>
            <div class="kpi-value">{podiums}</div>
            <div class="kpi-subtitle">Top 3 Finishes</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# CHAMPIONSHIP LEADERBOARD
# ============================================================

st.markdown(
    '<div class="section-title">🏆 Championship Leaderboard</div>',
    unsafe_allow_html=True
)

leaderboard = (
    final
    .groupby(
        ["FullName", "TeamName"],
        as_index=False
    )
    .agg(
        Points=("Points", "sum"),
        Wins=("Position", lambda x: (x == 1).sum()),
        Podiums=("Position", lambda x: (x <= 3).sum()),
        Races=("Round", "nunique")
    )
    .sort_values(
        "Points",
        ascending=False
    )
)

leaderboard["Rank"] = range(
    1,
    len(leaderboard) + 1
)

leaderboard = leaderboard[
    [
        "Rank",
        "FullName",
        "TeamName",
        "Points",
        "Wins",
        "Podiums",
        "Races"
    ]
]

leaderboard["Points"] = leaderboard["Points"].round(0)

st.dataframe(
    leaderboard,
    use_container_width=True,
    hide_index=True,
    height=400
)


# ============================================================
# TOP DRIVERS + TEAM POINTS
# ============================================================

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# DRIVER CHART
# ------------------------------------------------------------

with col1:

    st.markdown(
        '<div class="section-title">🥇 Top Drivers</div>',
        unsafe_allow_html=True
    )

    top_drivers = (
        leaderboard
        .head(10)
        .sort_values("Points")
    )

    fig = px.bar(
        top_drivers,
        x="Points",
        y="FullName",
        orientation="h",
        text="Points",
        hover_data=[
            "TeamName",
            "Wins",
            "Podiums"
        ]
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        template="plotly_dark",
        height=450,
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=20
        ),
        paper_bgcolor="#080808",
        plot_bgcolor="#080808",
        xaxis_title="Championship Points",
        yaxis_title=""
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ------------------------------------------------------------
# TEAM CHART
# ------------------------------------------------------------

with col2:

    st.markdown(
        '<div class="section-title">🏢 Constructor Performance</div>',
        unsafe_allow_html=True
    )

    team_points = (
        final
        .groupby("TeamName", as_index=False)
        ["Points"]
        .sum()
        .sort_values(
            "Points",
            ascending=False
        )
        .head(10)
    )

    fig_team = px.bar(
        team_points.sort_values("Points"),
        x="Points",
        y="TeamName",
        orientation="h",
        text="Points"
    )

    fig_team.update_traces(
        textposition="outside"
    )

    fig_team.update_layout(
        template="plotly_dark",
        height=450,
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=20
        ),
        paper_bgcolor="#080808",
        plot_bgcolor="#080808",
        xaxis_title="Points",
        yaxis_title=""
    )

    st.plotly_chart(
        fig_team,
        use_container_width=True
    )


# ============================================================
# DRIVER ANALYTICS
# ============================================================

st.markdown(
    '<div class="section-title">👤 Driver Performance Analysis</div>',
    unsafe_allow_html=True
)

driver_data = final.copy()

if selected_driver != "All Drivers":

    driver_data = driver_data[
        driver_data["FullName"] == selected_driver
    ]

else:

    driver_data = driver_data[
        driver_data["FullName"] == drivers[0]
    ]


# ============================================================
# DRIVER POINTS PROGRESSION
# ============================================================

fig_driver = px.line(
    driver_data.sort_values("Round"),
    x="Round",
    y="Points",
    markers=True,
    hover_data=[
        "Venue",
        "Position",
        "TeamName"
    ],
    title=f"{driver_data['FullName'].iloc[0]} - Race Points"
)

fig_driver.update_layout(
    template="plotly_dark",
    height=450,
    paper_bgcolor="#080808",
    plot_bgcolor="#080808",
    xaxis_title="Race Round",
    yaxis_title="Points"
)

st.plotly_chart(
    fig_driver,
    use_container_width=True
)


# ============================================================
# RACE PERFORMANCE
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.markdown(
        '<div class="section-title">🏁 Race-by-Race Points</div>',
        unsafe_allow_html=True
    )

    race_points = (
        final
        .groupby(
            ["Venue", "Round"],
            as_index=False
        )
        ["Points"]
        .sum()
        .sort_values("Round")
    )

    fig_race = px.bar(
        race_points,
        x="Venue",
        y="Points",
        text="Points"
    )

    fig_race.update_layout(
        template="plotly_dark",
        height=500,
        paper_bgcolor="#080808",
        plot_bgcolor="#080808",
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        fig_race,
        use_container_width=True
    )


with col2:

    st.markdown(
        '<div class="section-title">📈 Finishing Position</div>',
        unsafe_allow_html=True
    )

    position_data = driver_data.copy()

    fig_position = px.line(
        position_data.sort_values("Round"),
        x="Round",
        y="Position",
        markers=True,
        hover_data=[
            "Venue",
            "Points"
        ]
    )

    fig_position.update_yaxes(
        autorange="reversed"
    )

    fig_position.update_layout(
        template="plotly_dark",
        height=500,
        paper_bgcolor="#080808",
        plot_bgcolor="#080808",
        yaxis_title="Finishing Position",
        xaxis_title="Race Round"
    )

    st.plotly_chart(
        fig_position,
        use_container_width=True
    )


# ============================================================
# SELECTED RACE ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">🏁 Race Analysis</div>',
    unsafe_allow_html=True
)

if selected_venue != "All Races":

    race_data = final[
        final["Venue"] == selected_venue
    ].copy()

    race_data = race_data.sort_values(
        "Position"
    )

    race_info = race_data.iloc[0]

    r1, r2, r3, r4 = st.columns(4)

    with r1:

        st.metric(
            "🏁 Circuit",
            race_info["Venue"]
        )

    with r2:

        st.metric(
            "🌍 Country",
            race_info["Country"]
        )

    with r3:

        st.metric(
            "📅 Date",
            race_info["EventDate"].strftime(
                "%d %b %Y"
            )
        )

    with r4:

        winner = race_data.iloc[0]["FullName"]

        st.metric(
            "🏆 Winner",
            winner
        )

    st.markdown("### 🏎️ Race Results")

    race_display = race_data[
        [
            "Position",
            "FullName",
            "TeamName",
            "Status",
            "Points",
            "Laps"
        ]
    ].copy()

    race_display["Position"] = (
        race_display["Position"]
        .fillna(0)
        .astype(int)
    )

    st.dataframe(
        race_display,
        use_container_width=True,
        hide_index=True,
        height=450
    )

else:

    st.info(
        "👈 Select a specific race from the sidebar "
        "to view detailed race results."
    )


# ============================================================
# DRIVER COMPARISON
# ============================================================

st.markdown(
    '<div class="section-title">⚔️ Driver Comparison</div>',
    unsafe_allow_html=True
)

compare_drivers = st.multiselect(
    "Select drivers to compare",
    drivers,
    default=drivers[:2] if len(drivers) >= 2 else drivers
)

if len(compare_drivers) >= 2:

    comparison = final[
        final["FullName"].isin(compare_drivers)
    ]

    comparison = (
        comparison
        .groupby(
            ["FullName", "Round"],
            as_index=False
        )
        ["Points"]
        .sum()
    )

    fig_compare = px.line(
        comparison,
        x="Round",
        y="Points",
        color="FullName",
        markers=True,
        title="Driver Points Comparison"
    )

    fig_compare.update_layout(
        template="plotly_dark",
        height=500,
        paper_bgcolor="#080808",
        plot_bgcolor="#080808",
        xaxis_title="Race Round",
        yaxis_title="Points"
    )

    st.plotly_chart(
        fig_compare,
        use_container_width=True
    )

else:

    st.warning(
        "Select at least two drivers to compare."
    )


# ============================================================
# RAW DATA
# ============================================================

with st.expander("🔍 View Raw Race Data"):

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">

🏎️ <b>FORMULA 1 RACING ANALYTICS</b><br><br>

Built with Streamlit + FastF1 + Plotly + Pandas<br>

2025 Formula 1 Performance Dashboard

</div>
""", unsafe_allow_html=True)
