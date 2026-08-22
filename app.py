import streamlit as st
import fastf1
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="F1 2025 Analytics Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.dashboard-title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 5px;
}

.dashboard-subtitle {
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
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}

.kpi-title {
    color: #6c757d;
    font-size: 15px;
}

.kpi-value {
    font-size: 30px;
    font-weight: 700;
}

.section-title {
    font-size: 25px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    '<div class="dashboard-title">🏎️ Formula 1 — 2025 Analytics</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Explore driver performance, race results, teams and championship points'
    '</div>',
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_f1_data():

    schedule = fastf1.get_event_schedule(2025)

    races = schedule[
        ['Country', 'Location', 'EventDate', 'EventName']
    ]

    results = []

    for race in races['RoundNumber']:

        # Skip non-standard events if required
        if pd.isna(race):
            continue

        try:

            session = fastf1.get_session(
                2025,
                int(race),
                'R'
            )

            session.load(
                telemetry=False,
                weather=False,
                messages=False,
                laps=False
            )

            race_results = session.results

            race_results = race_results[
                [
                    'TeamName',
                    'FullName',
                    'Position',
                    'Time',
                    'Status',
                    'Points',
                    'Laps'
                ]
            ].copy()

            event_name = session.event.EventName

            race_results['Venue'] = event_name

            results.append(race_results)

        except Exception as e:
            st.warning(
                f"Could not load race {race}: {e}"
            )

    if results:

        final = pd.concat(
            results,
            ignore_index=True
        )

        return final

    return pd.DataFrame()


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

with st.spinner("🏎️ Loading Formula 1 2025 data..."):

    final = load_f1_data()


# ---------------------------------------------------------
# CHECK DATA
# ---------------------------------------------------------

if final.empty:

    st.error(
        "Unable to load Formula 1 data. "
        "Please check your internet connection and try again."
    )

    st.stop()


# ---------------------------------------------------------
# CLEAN DATA
# ---------------------------------------------------------

final['Points'] = pd.to_numeric(
    final['Points'],
    errors='coerce'
).fillna(0)

final['Position'] = pd.to_numeric(
    final['Position'],
    errors='coerce'
)

final['Laps'] = pd.to_numeric(
    final['Laps'],
    errors='coerce'
).fillna(0)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("🎛️ Dashboard Controls")

st.sidebar.markdown(
    "Use the filters below to explore the 2025 F1 season."
)

# Driver selection
drivers = sorted(
    final['FullName'].dropna().unique()
)

selected_driver = st.sidebar.selectbox(
    "👤 Select Driver",
    ["All Drivers"] + drivers
)

# Venue selection
venues = sorted(
    final['Venue'].dropna().unique()
)

selected_venue = st.sidebar.selectbox(
    "🏁 Select Race",
    ["All Races"] + venues
)

# Team selection
teams = sorted(
    final['TeamName'].dropna().unique()
)

selected_team = st.sidebar.selectbox(
    "🏢 Select Team",
    ["All Teams"] + teams
)


# ---------------------------------------------------------
# FILTER DATA
# ---------------------------------------------------------

filtered_data = final.copy()

if selected_driver != "All Drivers":

    filtered_data = filtered_data[
        filtered_data['FullName'] == selected_driver
    ]

if selected_venue != "All Races":

    filtered_data = filtered_data[
        filtered_data['Venue'] == selected_venue
    ]

if selected_team != "All Teams":

    filtered_data = filtered_data[
        filtered_data['TeamName'] == selected_team
    ]


# ---------------------------------------------------------
# KPI SECTION
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">📊 Season Overview</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

total_races = final['Venue'].nunique()

total_drivers = final['FullName'].nunique()

total_teams = final['TeamName'].nunique()

total_points = final['Points'].sum()


with col1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">🏁 Total Races</div>
            <div class="kpi-value">{total_races}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">👤 Drivers</div>
            <div class="kpi-value">{total_drivers}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">🏢 Teams</div>
            <div class="kpi-value">{total_teams}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">🏆 Total Points</div>
            <div class="kpi-value">{total_points:.1f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🏆 Driver Standings",
        "🏁 Race Analysis",
        "📈 Driver Performance",
        "📋 Race Results"
    ]
)


# =========================================================
# TAB 1 — DRIVER STANDINGS
# =========================================================

with tab1:

    st.subheader("🏆 2025 Driver Championship")

    driver_points = (
        final
        .groupby('FullName')['Points']
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    driver_points['Rank'] = range(
        1,
        len(driver_points) + 1
    )

    fig = px.bar(
        driver_points.sort_values(
            'Points',
            ascending=True
        ),
        x='Points',
        y='FullName',
        orientation='h',
        text='Points',
        title="Driver Championship Points",
        labels={
            'FullName': 'Driver',
            'Points': 'Points'
        }
    )

    fig.update_traces(
        texttemplate='%{text:.0f}',
        textposition='outside'
    )

    fig.update_layout(
        height=700,
        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("📋 Championship Table")

    standings = driver_points[
        ['Rank', 'FullName', 'Points']
    ]

    standings['Points'] = standings['Points'].round(1)

    st.dataframe(
        standings,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# TAB 2 — RACE ANALYSIS
# =========================================================

with tab2:

    st.subheader("🏁 Race Analysis")

    race_points = (
        final
        .groupby('FullName')['Points']
        .sum()
        .sort_values(
            ascending=False
        )
        .reset_index()
    )

    fig = px.bar(
        race_points,
        x='FullName',
        y='Points',
        text='Points',
        title="Points by Driver",
        labels={
            'FullName': 'Driver',
            'Points': 'Total Points'
        }
    )

    fig.update_traces(
        texttemplate='%{text:.0f}',
        textposition='outside'
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=600
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    st.subheader("🏢 Team Performance")

    team_points = (
        final
        .groupby('TeamName')['Points']
        .sum()
        .sort_values(
            ascending=False
        )
        .reset_index()
    )

    fig2 = px.bar(
        team_points,
        x='TeamName',
        y='Points',
        text='Points',
        title="Constructor Points",
        labels={
            'TeamName': 'Team',
            'Points': 'Points'
        }
    )

    fig2.update_traces(
        texttemplate='%{text:.0f}',
        textposition='outside'
    )

    fig2.update_layout(
        xaxis_tickangle=-45,
        height=550
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# =========================================================
# TAB 3 — DRIVER PERFORMANCE
# =========================================================

with tab3:

    st.subheader("📈 Driver Performance")

    if selected_driver == "All Drivers":

        st.info(
            "👈 Select a driver from the sidebar "
            "to view their race-by-race performance."
        )

        driver_for_chart = st.selectbox(
            "Select Driver",
            drivers,
            key="performance_driver"
        )

    else:

        driver_for_chart = selected_driver


    driver_data = final[
        final['FullName'] == driver_for_chart
    ].copy()


    if not driver_data.empty:

        # ---------------------------------------------
        # DRIVER KPI
        # ---------------------------------------------

        total_driver_points = driver_data['Points'].sum()

        races_participated = driver_data['Venue'].nunique()

        average_points = driver_data['Points'].mean()

        best_position = driver_data['Position'].min()


        c1, c2, c3, c4 = st.columns(4)


        c1.metric(
            "🏆 Total Points",
            f"{total_driver_points:.1f}"
        )

        c2.metric(
            "🏁 Races",
            races_participated
        )

        c3.metric(
            "📊 Avg Points",
            f"{average_points:.1f}"
        )

        c4.metric(
            "🥇 Best Position",
            f"P{int(best_position)}"
            if pd.notna(best_position)
            else "N/A"
        )


        # ---------------------------------------------
        # POINTS BY RACE
        # ---------------------------------------------

        fig = px.line(
            driver_data,
            x='Venue',
            y='Points',
            markers=True,
            title=f"{driver_for_chart} — Points by Race",
            labels={
                'Venue': 'Race',
                'Points': 'Points'
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


        # ---------------------------------------------
        # POSITION BY RACE
        # ---------------------------------------------

        fig2 = px.line(
            driver_data,
            x='Venue',
            y='Position',
            markers=True,
            title=f"{driver_for_chart} — Finishing Position",
            labels={
                'Venue': 'Race',
                'Position': 'Position'
            }
        )

        # Lower position number is better
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


# =========================================================
# TAB 4 — RACE RESULTS
# =========================================================

with tab4:

    st.subheader("📋 Race Results")

    display_data = filtered_data[
        [
            'Venue',
            'FullName',
            'TeamName',
            'Position',
            'Points',
            'Laps',
            'Status'
        ]
    ].copy()

    display_data = display_data.sort_values(
        ['Venue', 'Position']
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Venue": "🏁 Race",
            "FullName": "👤 Driver",
            "TeamName": "🏢 Team",
            "Position": st.column_config.NumberColumn(
                "🏆 Position"
            ),
            "Points": st.column_config.NumberColumn(
                "⭐ Points",
                format="%.1f"
            ),
            "Laps": "🔄 Laps",
            "Status": "📌 Status"
        }
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:#777;">
        🏎️ Formula 1 2025 Analytics Dashboard |
        Built with Streamlit, FastF1 & Plotly
    </div>
    """,
    unsafe_allow_html=True
)
