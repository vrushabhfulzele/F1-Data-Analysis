import streamlit as st
import pandas as pd
import plotly.express as px
import fastf1


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="F1 2025 Analytics",
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
    background: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.08);
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
# LOAD DATA
# ============================================================

@st.cache_data(
    show_spinner=False,
    ttl=86400
)
def load_f1_data():

    schedule = fastf1.get_event_schedule(2025)

    # Only completed/actual race rounds
    races = schedule[
        schedule["RoundNumber"].notna()
    ].copy()

    all_results = []

    for _, race in races.iterrows():

        round_number = int(
            race["RoundNumber"]
        )

        event_name = race["EventName"]

        try:

            session = fastf1.get_session(
                2025,
                round_number,
                "R"
            )

            session.load(
                telemetry=False,
                weather=False,
                messages=False,
                laps=False
            )

            results = session.results.copy()

            required_columns = [
                "TeamName",
                "FullName",
                "Position",
                "Time",
                "Status",
                "Points",
                "Laps"
            ]

            results = results[
                required_columns
            ]

            results["Venue"] = event_name

            results["Round"] = round_number

            all_results.append(results)

        except Exception as error:

            # Continue loading other races
            print(
                f"Error loading {event_name}: {error}"
            )

    if not all_results:

        return pd.DataFrame()

    final = pd.concat(
        all_results,
        ignore_index=True
    )

    return final


# ============================================================
# LOAD DATA
# ============================================================

with st.spinner(
    "🏎️ Loading Formula 1 2025 race data..."
):

    final = load_f1_data()


# ============================================================
# DATA VALIDATION
# ============================================================

if final.empty:

    st.error(
        "❌ No F1 data could be loaded."
    )

    st.info(
        "Please check your internet connection "
        "and restart the Streamlit app."
    )

    st.stop()


# ============================================================
# DATA CLEANING
# ============================================================

final["Points"] = pd.to_numeric(
    final["Points"],
    errors="coerce"
).fillna(0)

final["Position"] = pd.to_numeric(
    final["Position"],
    errors="coerce"
)

final["Laps"] = pd.to_numeric(
    final["Laps"],
    errors="coerce"
).fillna(0)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🎛️ Dashboard Filters")

st.sidebar.caption(
    "Select the options below to explore the F1 season."
)


# ============================================================
# RACE SELECTOR
# ============================================================

venues = (
    final["Venue"]
    .dropna()
    .unique()
    .tolist()
)

venues = sorted(venues)


selected_venue = st.sidebar.selectbox(
    "🏁 Select Race",
    ["All Races"] + venues
)


# ============================================================
# DRIVER SELECTOR
# ============================================================

drivers = (
    final["FullName"]
    .dropna()
    .unique()
    .tolist()
)

drivers = sorted(drivers)


selected_driver = st.sidebar.selectbox(
    "👤 Select Driver",
    ["All Drivers"] + drivers
)


# ============================================================
# TEAM SELECTOR
# ============================================================

teams = (
    final["TeamName"]
    .dropna()
    .unique()
    .tolist()
)

teams = sorted(teams)


selected_team = st.sidebar.selectbox(
    "🏢 Select Team",
    ["All Teams"] + teams
)


# ============================================================
# FILTER DATA
# ============================================================

filtered = final.copy()


if selected_venue != "All Races":

    filtered = filtered[
        filtered["Venue"] == selected_venue
    ]


if selected_driver != "All Drivers":

    filtered = filtered[
        filtered["FullName"] == selected_driver
    ]


if selected_team != "All Teams":

    filtered = filtered[
        filtered["TeamName"] == selected_team
    ]


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_races = final["Venue"].nunique()

total_drivers = final["FullName"].nunique()

total_teams = final["TeamName"].nunique()

selected_points = filtered["Points"].sum()


# ============================================================
# KPI CARDS
# ============================================================

st.markdown("### 📊 Season Overview")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">
                🏁 Races
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
                {selected_points:.1f}
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

    driver_points = (
        final
        .groupby("FullName")["Points"]
        .sum()
        .sort_values(
            ascending=False
        )
        .reset_index()
    )

    driver_points["Rank"] = range(
        1,
        len(driver_points) + 1
    )

    driver_points = driver_points[
        [
            "Rank",
            "FullName",
            "Points"
        ]
    ]

    # --------------------------------------------
    # CHART
    # --------------------------------------------

    chart_data = driver_points.sort_values(
        "Points",
        ascending=True
    )

    fig = px.bar(
        chart_data,
        x="Points",
        y="FullName",
        orientation="h",
        text="Points",
        title="Driver Championship Points",
        labels={
            "FullName": "Driver",
            "Points": "Points"
        }
    )

    fig.update_traces(
        texttemplate="%{text:.0f}",
        textposition="outside"
    )

    fig.update_layout(
        height=700,
        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------
    # TABLE
    # --------------------------------------------

    st.subheader(
        "📋 Championship Standings"
    )

    st.dataframe(
        driver_points,
        use_container_width=True,
        hide_index=True,
        column_config={

            "Rank":
                st.column_config.NumberColumn(
                    "🏅 Rank"
                ),

            "FullName":
                "👤 Driver",

            "Points":
                st.column_config.NumberColumn(
                    "🏆 Points",
                    format="%.1f"
                )
        }
    )


# ============================================================
# TAB 2 — RACE ANALYSIS
# ============================================================

with tab2:

    st.subheader("🏁 Race Analysis")

    if selected_venue == "All Races":

        race_points = (
            final
            .groupby("FullName")["Points"]
            .sum()
            .sort_values(
                ascending=False
            )
            .reset_index()
        )

        title = "Total Points by Driver"

    else:

        race_points = (
            final[
                final["Venue"]
                == selected_venue
            ]
            .groupby("FullName")["Points"]
            .sum()
            .sort_values(
                ascending=False
            )
            .reset_index()
        )

        title = (
            f"{selected_venue} — Driver Points"
        )

    fig = px.bar(
        race_points,
        x="FullName",
        y="Points",
        text="Points",
        title=title,
        labels={
            "FullName": "Driver",
            "Points": "Points"
        }
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


    # ========================================================
    # TEAM ANALYSIS
    # ========================================================

    st.subheader(
        "🏢 Constructor Championship"
    )

    team_points = (
        final
        .groupby("TeamName")["Points"]
        .sum()
        .sort_values(
            ascending=False
        )
        .reset_index()
    )

    fig2 = px.bar(
        team_points,
        x="TeamName",
        y="Points",
        text="Points",
        title="Team Championship Points",
        labels={
            "TeamName": "Team",
            "Points": "Points"
        }
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
            "Choose a driver",
            drivers,
            key="performance_driver"
        )

    else:

        performance_driver = selected_driver


    driver_data = final[
        final["FullName"]
        == performance_driver
    ].copy()


    # --------------------------------------------
    # DRIVER METRICS
    # --------------------------------------------

    total_driver_points = (
        driver_data["Points"].sum()
    )

    races = driver_data["Venue"].nunique()

    average_points = (
        driver_data["Points"].mean()
    )

    valid_positions = (
        driver_data["Position"]
        .dropna()
    )

    if not valid_positions.empty:

        best_position = int(
            valid_positions.min()
        )

    else:

        best_position = None


    c1, c2, c3, c4 = st.columns(4)


    c1.metric(
        "🏆 Total Points",
        f"{total_driver_points:.1f}"
    )

    c2.metric(
        "🏁 Races",
        races
    )

    c3.metric(
        "📊 Average Points",
        f"{average_points:.1f}"
    )

    c4.metric(
        "🥇 Best Finish",
        (
            f"P{best_position}"
            if best_position
            else "N/A"
        )
    )


    # --------------------------------------------
    # POINTS BY RACE
    # --------------------------------------------

    st.markdown(
        "### 📈 Points by Race"
    )

    driver_data = driver_data.sort_values(
        "Round"
    )

    fig = px.line(
        driver_data,
        x="Venue",
        y="Points",
        markers=True,
        title=(
            f"{performance_driver} — "
            "Points by Race"
        ),
        labels={
            "Venue": "Race",
            "Points": "Points"
        }
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=550
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------
    # FINISHING POSITION
    # --------------------------------------------

    st.markdown(
        "### 🏁 Finishing Position"
    )

    position_data = driver_data.dropna(
        subset=["Position"]
    )

    fig2 = px.line(
        position_data,
        x="Venue",
        y="Position",
        markers=True,
        title=(
            f"{performance_driver} — "
            "Finishing Position"
        ),
        labels={
            "Venue": "Race",
            "Position": "Position"
        }
    )

    # P1 at the top
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


    # --------------------------------------------
    # DRIVER RESULTS
    # --------------------------------------------

    st.markdown(
        "### 📋 Race-by-Race Results"
    )

    driver_table = driver_data[
        [
            "Venue",
            "TeamName",
            "Position",
            "Points",
            "Laps",
            "Status"
        ]
    ]

    st.dataframe(
        driver_table,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 4 — RACE RESULTS
# ============================================================

with tab4:

    st.subheader(
        "📋 Race Results"
    )

    display_data = filtered[
        [
            "Round",
            "Venue",
            "FullName",
            "TeamName",
            "Position",
            "Points",
            "Laps",
            "Status"
        ]
    ].copy()

    display_data = display_data.sort_values(
        [
            "Round",
            "Position"
        ]
    )

    st.write(
        f"Showing **{len(display_data):,} results**"
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
        column_config={

            "Round":
                st.column_config.NumberColumn(
                    "Round"
                ),

            "Venue":
                "🏁 Race",

            "FullName":
                "👤 Driver",

            "TeamName":
                "🏢 Team",

            "Position":
                st.column_config.NumberColumn(
                    "🏆 Position"
                ),

            "Points":
                st.column_config.NumberColumn(
                    "⭐ Points",
                    format="%.1f"
                ),

            "Laps":
                st.column_config.NumberColumn(
                    "🔄 Laps"
                ),

            "Status":
                "📌 Status"
        }
    )


# ============================================================
# DOWNLOAD
# ============================================================

st.sidebar.markdown("---")

st.sidebar.subheader(
    "📥 Export Data"
)

csv_data = filtered.to_csv(
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
    <div style="text-align:center; color:#777;">
        🏎️ F1 2025 Analytics Dashboard<br>
        Built with FastF1 • Streamlit • Pandas • Plotly
    </div>
    """,
    unsafe_allow_html=True
)
