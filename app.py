import streamlit as st
import fastf1
import pandas as pd
import plotly.express as px

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="F1 Racing Analytics",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# FASTF1 CACHE
# ============================================================

fastf1.Cache.enable_cache("fastf1_cache")


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800&display=swap'
);

html, body, [class*="css"] {
    font-family: 'Orbitron', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at top right,
            rgba(225, 6, 0, 0.18),
            transparent 35%
        ),
        radial-gradient(
            circle at bottom left,
            rgba(225, 6, 0, 0.10),
            transparent 30%
        ),
        #080808;

    color: white;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #0b0b0b,
        #151515
    );

    border-right: 1px solid #292929;
}

/* Hero */

.hero {
    background:
        linear-gradient(
            135deg,
            rgba(225,6,0,0.95),
            rgba(15,15,15,0.96)
        );

    padding: 35px;

    border-radius: 20px;

    margin-bottom: 25px;

    border: 1px solid #3b3b3b;

    box-shadow:
        0 15px 45px rgba(0,0,0,0.6);
}

.hero-title {
    font-size: 44px;

    font-weight: 800;

    letter-spacing: 4px;

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

    font-size: 12px;
}

/* Section headings */

.section-title {
    font-size: 21px;

    font-weight: 700;

    margin-top: 28px;

    margin-bottom: 18px;

    border-left: 4px solid #e10600;

    padding-left: 12px;
}

/* KPI */

.kpi-card {
    background:
        linear-gradient(
            145deg,
            #171717,
            #0b0b0b
        );

    border: 1px solid #2d2d2d;

    border-left: 4px solid #e10600;

    border-radius: 15px;

    padding: 20px;

    min-height: 125px;

    box-shadow:
        0 8px 25px rgba(0,0,0,0.4);

    transition: 0.3s;
}

.kpi-card:hover {
    transform: translateY(-5px);

    box-shadow:
        0 12px 35px rgba(225,6,0,0.25);
}

.kpi-title {
    font-size: 11px;

    color: #999;

    text-transform: uppercase;

    letter-spacing: 1px;
}

.kpi-value {
    font-size: 29px;

    font-weight: 800;

    margin-top: 8px;

    color: white;
}

.kpi-subtitle {
    font-size: 10px;

    color: #777;

    margin-top: 5px;
}

/* Footer */

.footer {
    text-align: center;

    color: #666;

    font-size: 11px;

    padding: 30px;

    margin-top: 40px;

    border-top: 1px solid #222;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD F1 DATA
# ============================================================

@st.cache_data(show_spinner=False)
def load_f1_data():

    schedule = fastf1.get_event_schedule(2025)

    schedule = schedule[
        schedule["RoundNumber"] > 0
    ].copy()

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

    total_races = len(schedule)

    progress = st.progress(0)

    for count, (_, race) in enumerate(
        schedule.iterrows(),
        start=1
    ):

        round_number = int(
            race["RoundNumber"]
        )

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

            required_columns = [
                "DriverNumber",
                "Abbreviation",
                "FullName",
                "TeamName",
                "Position",
                "Time",
                "Status",
                "Points",
                "Laps"
            ]

            available_columns = [
                column
                for column in required_columns
                if column in race_results.columns
            ]

            race_results = race_results[
                available_columns
            ].copy()

            race_results["Round"] = round_number

            race_results["Venue"] = race[
                "Location"
            ]

            race_results["Country"] = race[
                "Country"
            ]

            race_results["EventName"] = race[
                "EventName"
            ]

            race_results["EventDate"] = race[
                "EventDate"
            ]

            results.append(
                race_results
            )

        except Exception:
            pass

        progress.progress(
            count / total_races
        )

    progress.empty()

    if not results:

        return pd.DataFrame()

    final = pd.concat(
        results,
        ignore_index=True
    )

    # Numeric conversions

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

    return final


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
        🔴 FASTF1 • LIVE-STYLE ANALYTICS • PERFORMANCE DATA
    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# LOAD DATA
# ============================================================

with st.spinner(
    "🏁 Loading 2025 Formula 1 race data..."
):

    final = load_f1_data()


if final.empty:

    st.error(
        """
        ❌ No Formula 1 data could be loaded.

        Please check your internet connection and
        restart the Streamlit application.
        """
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "# 🏎️ F1 CONTROL CENTER"
)

st.sidebar.markdown("---")


# Driver filter

drivers = sorted(
    final["FullName"]
    .dropna()
    .unique()
)

selected_driver = st.sidebar.selectbox(
    "👤 Driver",
    ["All Drivers"] + drivers
)


# Race filter

races = (
    final[
        ["Round", "Venue", "EventName"]
    ]
    .drop_duplicates()
    .sort_values("Round")
)

venues = races["Venue"].tolist()

selected_venue = st.sidebar.selectbox(
    "🏁 Race",
    ["All Races"] + venues
)


# Team filter

teams = sorted(
    final["TeamName"]
    .dropna()
    .unique()
)

selected_team = st.sidebar.selectbox(
    "🏢 Team",
    ["All Teams"] + teams
)


# ============================================================
# FILTER DATA
# ============================================================

filtered = final.copy()

if selected_driver != "All Drivers":

    filtered = filtered[
        filtered["FullName"]
        == selected_driver
    ]

if selected_venue != "All Races":

    filtered = filtered[
        filtered["Venue"]
        == selected_venue
    ]

if selected_team != "All Teams":

    filtered = filtered[
        filtered["TeamName"]
        == selected_team
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
# KPI SECTION
# ============================================================

st.markdown(
    '<div class="section-title">📊 Season Overview</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4, c5, c6 = st.columns(6)


def kpi_card(
    title,
    value,
    subtitle
):

    return f"""
    <div class="kpi-card">

        <div class="kpi-title">
            {title}
        </div>

        <div class="kpi-value">
            {value}
        </div>

        <div class="kpi-subtitle">
            {subtitle}
        </div>

    </div>
    """


with c1:

    st.markdown(
        kpi_card(
            "Races",
            total_races,
            "2025 Season"
        ),
        unsafe_allow_html=True
    )


with c2:

    st.markdown(
        kpi_card(
            "Drivers",
            total_drivers,
            "Participants"
        ),
        unsafe_allow_html=True
    )


with c3:

    st.markdown(
        kpi_card(
            "Teams",
            total_teams,
            "Constructors"
        ),
        unsafe_allow_html=True
    )


with c4:

    st.markdown(
        kpi_card(
            "Points",
            f"{total_points:.0f}",
            "Selected Filter"
        ),
        unsafe_allow_html=True
    )


with c5:

    st.markdown(
        kpi_card(
            "Wins",
            wins,
            "Race Victories"
        ),
        unsafe_allow_html=True
    )


with c6:

    st.markdown(
        kpi_card(
            "Podiums",
            podiums,
            "Top 3 Finishes"
        ),
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

        Wins=(
            "Position",
            lambda x: (x == 1).sum()
        ),

        Podiums=(
            "Position",
            lambda x: (x <= 3).sum()
        ),

        Races=(
            "Round",
            "nunique"
        )
    )
    .sort_values(
        "Points",
        ascending=False
    )
)

leaderboard.insert(
    0,
    "Rank",
    range(
        1,
        len(leaderboard) + 1
    )
)

leaderboard["Points"] = (
    leaderboard["Points"]
    .round(0)
)

st.dataframe(
    leaderboard,
    use_container_width=True,
    hide_index=True,
    height=420
)


# ============================================================
# TOP DRIVERS + TEAMS
# ============================================================

col1, col2 = st.columns(2)


# ============================================================
# TOP DRIVERS
# ============================================================

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
        paper_bgcolor="#080808",
        plot_bgcolor="#080808",
        xaxis_title="Championship Points",
        yaxis_title=""
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# TEAM PERFORMANCE
# ============================================================

with col2:

    st.markdown(
        '<div class="section-title">🏢 Constructor Performance</div>',
        unsafe_allow_html=True
    )

    team_points = (
        final
        .groupby(
            "TeamName",
            as_index=False
        )["Points"]
        .sum()
        .sort_values(
            "Points",
            ascending=False
        )
        .head(10)
    )

    team_points = team_points.sort_values(
        "Points"
    )

    fig = px.bar(
        team_points,
        x="Points",
        y="TeamName",
        orientation="h",
        text="Points"
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        template="plotly_dark",
        height=450,
        paper_bgcolor="#080808",
        plot_bgcolor="#080808",
        xaxis_title="Points",
        yaxis_title=""
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# DRIVER ANALYTICS
# ============================================================

st.markdown(
    '<div class="section-title">👤 Driver Analytics</div>',
    unsafe_allow_html=True
)

if selected_driver == "All Drivers":

    analysis_driver = drivers[0]

else:

    analysis_driver = selected_driver


driver_data = final[
    final["FullName"]
    == analysis_driver
].copy()


# ============================================================
# DRIVER POINTS
# ============================================================

fig = px.line(
    driver_data.sort_values("Round"),
    x="Round",
    y="Points",
    markers=True,
    hover_data=[
        "Venue",
        "Position",
        "TeamName"
    ],
    title=f"{analysis_driver} — Race Points"
)

fig.update_layout(
    template="plotly_dark",
    height=450,
    paper_bgcolor="#080808",
    plot_bgcolor="#080808",
    xaxis_title="Race Round",
    yaxis_title="Points"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# RACE PERFORMANCE
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.markdown(
        '<div class="section-title">🏁 Race Points</div>',
        unsafe_allow_html=True
    )

    race_points = (
        final
        .groupby(
            ["Venue", "Round"],
            as_index=False
        )["Points"]
        .sum()
        .sort_values("Round")
    )

    fig = px.bar(
        race_points,
        x="Venue",
        y="Points",
        text="Points"
    )

    fig.update_layout(
        template="plotly_dark",
        height=500,
        paper_bgcolor="#080808",
        plot_bgcolor="#080808",
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with col2:

    st.markdown(
        '<div class="section-title">📈 Finishing Position</div>',
        unsafe_allow_html=True
    )

    fig = px.line(
        driver_data.sort_values("Round"),
        x="Round",
        y="Position",
        markers=True,
        hover_data=[
            "Venue",
            "Points"
        ]
    )

    fig.update_yaxes(
        autorange="reversed"
    )

    fig.update_layout(
        template="plotly_dark",
        height=500,
        paper_bgcolor="#080808",
        plot_bgcolor="#080808",
        xaxis_title="Race Round",
        yaxis_title="Finishing Position"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# RACE ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">🏁 Race Analysis</div>',
    unsafe_allow_html=True
)

if selected_venue != "All Races":

    race_data = final[
        final["Venue"]
        == selected_venue
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

        race_date = pd.to_datetime(
            race_info["EventDate"]
        )

        st.metric(
            "📅 Date",
            race_date.strftime(
                "%d %b %Y"
            )
        )

    with r4:

        st.metric(
            "🏆 Winner",
            race_data.iloc[0]["FullName"]
        )

    race_display = race_data[
        [
            "Position",
            "FullName",
            "TeamName",
            "Status",
            "Points",
            "Laps"
        ]
    ]

    st.dataframe(
        race_display,
        use_container_width=True,
        hide_index=True,
        height=450
    )

else:

    st.info(
        "👈 Select a race from the sidebar "
        "to see detailed race results."
    )


# ============================================================
# DRIVER COMPARISON
# ============================================================

st.markdown(
    '<div class="section-title">⚔️ Driver Comparison</div>',
    unsafe_allow_html=True
)

compare_drivers = st.multiselect(
    "Select drivers",
    drivers,
    default=drivers[:2]
)

if len(compare_drivers) >= 2:

    comparison = final[
        final["FullName"].isin(
            compare_drivers
        )
    ]

    comparison = (
        comparison
        .groupby(
            ["FullName", "Round"],
            as_index=False
        )["Points"]
        .sum()
    )

    fig = px.line(
        comparison,
        x="Round",
        y="Points",
        color="FullName",
        markers=True,
        title="Driver Points Comparison"
    )

    fig.update_layout(
        template="plotly_dark",
        height=500,
        paper_bgcolor="#080808",
        plot_bgcolor="#080808"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.warning(
        "Please select at least two drivers."
    )


# ============================================================
# RAW DATA
# ============================================================

with st.expander("🔍 View Raw F1 Data"):

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

🏎️ <b>FORMULA 1 RACING ANALYTICS</b>
<br><br>

2025 Formula 1 Performance Dashboard
<br>

Built with Streamlit • FastF1 • Pandas • Plotly

</div>
""", unsafe_allow_html=True)
