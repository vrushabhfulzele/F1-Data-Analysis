import streamlit as st
import pandas as pd
import plotly.express as px
import requests


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="F1 2025 Analytics Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #f5f7fa;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #6c757d;
    font-size: 18px;
    margin-bottom: 30px;
}

.kpi-card {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.kpi-title {
    color: #6c757d;
    font-size: 15px;
}

.kpi-value {
    font-size: 30px;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🏎️ Formula 1 — 2025 Analytics</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Explore drivers, races, teams and championship performance'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# API
# ============================================================

BASE_URL = "https://api.jolpi.ca/ergast/f1/2025"


# ============================================================
# LOAD F1 DATA
# ============================================================

@st.cache_data(ttl=86400, show_spinner=False)
def load_f1_data():

    all_results = []

    # --------------------------------------------------------
    # Get 2025 race schedule
    # --------------------------------------------------------

    schedule_url = (
        f"{BASE_URL}/races.json?limit=100"
    )

    response = requests.get(
        schedule_url,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    races = (
        data
        .get("MRData", {})
        .get("RaceTable", {})
        .get("Races", [])
    )

    if not races:
        return pd.DataFrame()

    # --------------------------------------------------------
    # Load each race
    # --------------------------------------------------------

    for race in races:

        round_number = race["round"]

        race_name = race["raceName"]

        race_url = (
            f"{BASE_URL}/{round_number}"
            "/results.json?limit=100"
        )

        try:

            race_response = requests.get(
                race_url,
                timeout=30
            )

            race_response.raise_for_status()

            race_data = race_response.json()

            race_list = (
                race_data
                .get("MRData", {})
                .get("RaceTable", {})
                .get("Races", [])
            )

            if not race_list:
                continue

            results = race_list[0].get(
                "Results",
                []
            )

            for result in results:

                driver = result.get(
                    "Driver",
                    {}
                )

                constructor = result.get(
                    "Constructor",
                    {}
                )

                position = result.get(
                    "position"
                )

                grid = result.get(
                    "grid"
                )

                laps = result.get(
                    "laps"
                )

                all_results.append({

                    "Round": int(
                        round_number
                    ),

                    "Venue": race_name,

                    "Circuit": race[
                        "Circuit"
                    ]["circuitName"],

                    "Country": race[
                        "Circuit"
                    ]["Location"]["country"],

                    "Driver": (
                        driver.get(
                            "givenName",
                            ""
                        )
                        + " "
                        + driver.get(
                            "familyName",
                            ""
                        )
                    ).strip(),

                    "DriverCode": driver.get(
                        "code",
                        ""
                    ),

                    "Team": constructor.get(
                        "name",
                        "Unknown"
                    ),

                    "Position": (
                        int(position)
                        if position
                        else None
                    ),

                    "Points": float(
                        result.get(
                            "points",
                            0
                        )
                    ),

                    "Grid": (
                        int(grid)
                        if grid
                        else None
                    ),

                    "Laps": (
                        int(laps)
                        if laps
                        else 0
                    ),

                    "Status": result.get(
                        "status",
                        ""
                    ),

                    "Time": result.get(
                        "Time",
                        {}
                    ).get(
                        "time",
                        ""
                    )
                })

        except requests.RequestException as error:

            print(
                f"Could not load "
                f"{race_name}: {error}"
            )

        except Exception as error:

            print(
                f"Unexpected error in "
                f"{race_name}: {error}"
            )

    return pd.DataFrame(
        all_results
    )


# ============================================================
# LOAD DATA
# ============================================================

try:

    with st.spinner(
        "🏎️ Loading 2025 Formula 1 data..."
    ):

        df = load_f1_data()

except Exception as error:

    st.error(
        "❌ Unable to load F1 data."
    )

    st.warning(
        "Please check your internet connection "
        "or try again later."
    )

    st.stop()


# ============================================================
# VALIDATE DATA
# ============================================================

if df.empty:

    st.error(
        "❌ No race data was returned."
    )

    st.stop()


# ============================================================
# CLEAN DATA
# ============================================================

df["Points"] = pd.to_numeric(
    df["Points"],
    errors="coerce"
).fillna(0)

df["Position"] = pd.to_numeric(
    df["Position"],
    errors="coerce"
)

df["Laps"] = pd.to_numeric(
    df["Laps"],
    errors="coerce"
).fillna(0)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🎛️ Dashboard Filters")

st.sidebar.caption(
    "Select filters to explore the 2025 F1 season."
)


# ------------------------------------------------------------
# RACE
# ------------------------------------------------------------

venues = sorted(
    df["Venue"].dropna().unique()
)

selected_venue = st.sidebar.selectbox(
    "🏁 Select Race",
    ["All Races"] + list(venues)
)


# ------------------------------------------------------------
# DRIVER
# ------------------------------------------------------------

drivers = sorted(
    df["Driver"].dropna().unique()
)

selected_driver = st.sidebar.selectbox(
    "👤 Select Driver",
    ["All Drivers"] + list(drivers)
)


# ------------------------------------------------------------
# TEAM
# ------------------------------------------------------------

teams = sorted(
    df["Team"].dropna().unique()
)

selected_team = st.sidebar.selectbox(
    "🏢 Select Team",
    ["All Teams"] + list(teams)
)


# ============================================================
# FILTER DATA
# ============================================================

filtered_df = df.copy()


if selected_venue != "All Races":

    filtered_df = filtered_df[
        filtered_df["Venue"]
        == selected_venue
    ]


if selected_driver != "All Drivers":

    filtered_df = filtered_df[
        filtered_df["Driver"]
        == selected_driver
    ]


if selected_team != "All Teams":

    filtered_df = filtered_df[
        filtered_df["Team"]
        == selected_team
    ]


# ============================================================
# KPI SECTION
# ============================================================

st.markdown(
    "### 📊 Season Overview"
)

total_races = df["Venue"].nunique()

total_drivers = df["Driver"].nunique()

total_teams = df["Team"].nunique()

filtered_points = filtered_df[
    "Points"
].sum()


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">
                🏁 Total Races
            </div>
            <div class="kpi-value">
                {total_races}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">
                👤 Drivers
            </div>
            <div class="kpi-value">
                {total_drivers}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">
                🏢 Teams
            </div>
            <div class="kpi-value">
                {total_teams}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">
                🏆 Selected Points
            </div>
            <div class="kpi-value">
                {filtered_points:.1f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🏆 Championship",
        "🏁 Race Analysis",
        "👤 Driver Performance",
        "📋 Race Results"
    ]
)


# ============================================================
# TAB 1 — CHAMPIONSHIP
# ============================================================

with tab1:

    st.subheader(
        "🏆 2025 Driver Championship"
    )

    standings = (
        df
        .groupby("Driver")["Points"]
        .sum()
        .sort_values(
            ascending=False
        )
        .reset_index()
    )

    standings["Rank"] = range(
        1,
        len(standings) + 1
    )

    standings = standings[
        [
            "Rank",
            "Driver",
            "Points"
        ]
    ]

    chart_data = standings.sort_values(
        "Points",
        ascending=True
    )

    fig = px.bar(
        chart_data,
        x="Points",
        y="Driver",
        orientation="h",
        text="Points",
        title="Driver Championship Points"
    )

    fig.update_traces(
        texttemplate="%{text:.0f}",
        textposition="outside"
    )

    fig.update_layout(
        height=700
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "📋 Championship Standings"
    )

    st.dataframe(
        standings,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 2 — RACE ANALYSIS
# ============================================================

with tab2:

    st.subheader(
        "🏁 Race Analysis"
    )

    if selected_venue == "All Races":

        race_points = (
            df
            .groupby("Driver")["Points"]
            .sum()
            .reset_index()
            .sort_values(
                "Points",
                ascending=False
            )
        )

        chart_title = (
            "Total Driver Points"
        )

    else:

        race_points = (
            df[
                df["Venue"]
                == selected_venue
            ]
            .groupby("Driver")["Points"]
            .sum()
            .reset_index()
            .sort_values(
                "Points",
                ascending=False
            )
        )

        chart_title = (
            f"{selected_venue} — Driver Points"
        )


    fig = px.bar(
        race_points,
        x="Driver",
        y="Points",
        text="Points",
        title=chart_title
    )

    fig.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=600
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # TEAM ANALYSIS
    # --------------------------------------------------------

    st.subheader(
        "🏢 Constructor Championship"
    )

    team_points = (
        df
        .groupby("Team")["Points"]
        .sum()
        .reset_index()
        .sort_values(
            "Points",
            ascending=False
        )
    )

    fig2 = px.bar(
        team_points,
        x="Team",
        y="Points",
        text="Points",
        title="Constructor Championship"
    )

    fig2.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )

    fig2.update_layout(
        xaxis_tickangle=-45,
        height=550
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# ============================================================
# TAB 3 — DRIVER PERFORMANCE
# ============================================================

with tab3:

    st.subheader(
        "👤 Driver Performance"
    )

    if selected_driver == "All Drivers":

        performance_driver = st.selectbox(
            "Select a Driver",
            drivers,
            key="performance_driver"
        )

    else:

        performance_driver = selected_driver


    driver_df = df[
        df["Driver"]
        == performance_driver
    ].sort_values(
        "Round"
    )


    # --------------------------------------------------------
    # DRIVER KPIs
    # --------------------------------------------------------

    driver_points = driver_df[
        "Points"
    ].sum()

    race_count = driver_df[
        "Venue"
    ].nunique()

    average_points = driver_df[
        "Points"
    ].mean()

    valid_positions = (
        driver_df["Position"]
        .dropna()
    )

    if not valid_positions.empty:

        best_finish = int(
            valid_positions.min()
        )

    else:

        best_finish = None


    c1, c2, c3, c4 = st.columns(4)


    c1.metric(
        "🏆 Total Points",
        f"{driver_points:.1f}"
    )

    c2.metric(
        "🏁 Races",
        race_count
    )

    c3.metric(
        "📊 Average Points",
        f"{average_points:.1f}"
    )

    c4.metric(
        "🥇 Best Finish",
        (
            f"P{best_finish}"
            if best_finish
            else "N/A"
        )
    )


    # --------------------------------------------------------
    # POINTS BY RACE
    # --------------------------------------------------------

    st.markdown(
        "### 📈 Points by Race"
    )

    fig = px.line(
        driver_df,
        x="Venue",
        y="Points",
        markers=True,
        title=(
            f"{performance_driver} — "
            "Points by Race"
        )
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=550
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # FINISHING POSITION
    # --------------------------------------------------------

    st.markdown(
        "### 🏁 Finishing Position"
    )

    position_df = driver_df.dropna(
        subset=["Position"]
    )

    fig2 = px.line(
        position_df,
        x="Venue",
        y="Position",
        markers=True,
        title=(
            f"{performance_driver} — "
            "Finishing Position"
        )
    )

    fig2.update_yaxes(
        autorange="reversed"
    )

    fig2.update_layout(
        xaxis_tickangle=-45,
        height=550
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# ============================================================
# TAB 4 — RESULTS
# ============================================================

with tab4:

    st.subheader(
        "📋 Race Results"
    )

    result_columns = [
        "Round",
        "Venue",
        "Driver",
        "Team",
        "Position",
        "Points",
        "Laps",
        "Status"
    ]

    results = filtered_df[
        result_columns
    ].sort_values(
        [
            "Round",
            "Position"
        ]
    )

    st.write(
        f"Showing **{len(results):,} results**"
    )

    st.dataframe(
        results,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# DOWNLOAD
# ============================================================

st.sidebar.markdown("---")

st.sidebar.subheader(
    "📥 Export"
)

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.sidebar.download_button(
    label="⬇️ Download CSV",
    data=csv_data,
    file_name="f1_2025_results.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center;color:#777;">
        🏎️ F1 2025 Analytics Dashboard<br>
        Built with Streamlit • Pandas • Plotly
    </div>
    """,
    unsafe_allow_html=True
)
