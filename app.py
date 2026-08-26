import streamlit as st
import fastf1
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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
    background-color: #08080b;
    color: white;
}

/* HERO */
.hero {
    background: linear-gradient(
        135deg,
        #111116 0%,
        #210000 50%,
        #0b0b0f 100%
    );

    padding: 35px;
    border-radius: 20px;
    border: 1px solid #3a3a40;
    margin-bottom: 25px;
    box-shadow: 0px 10px 35px rgba(0,0,0,0.6);
}

.hero-title {
    font-size: 46px;
    font-weight: 900;
    letter-spacing: 3px;
}

.hero-subtitle {
    color: #bbbbbb;
    font-size: 18px;
    margin-top: 5px;
}

.red-line {
    height: 4px;
    background: #e10600;
    margin-top: 20px;
    border-radius: 10px;
}

/* KPI */
.kpi-card {
    background: linear-gradient(
        145deg,
        #17171d,
        #0f0f13
    );

    padding: 22px;
    border-radius: 16px;

    border: 1px solid #303038;

    text-align: center;

    box-shadow:
        0px 8px 20px rgba(0,0,0,0.4);

    min-height: 110px;
}

.kpi-title {
    color: #999999;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.kpi-value {
    font-size: 28px;
    font-weight: 800;
    color: white;
    margin-top: 8px;
}

/* SECTION */
.section-title {
    font-size: 25px;
    font-weight: 800;
    margin-top: 30px;
    margin-bottom: 15px;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #101014;
}

/* BUTTON */
.stButton > button {
    background-color: #e10600;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 700;
}

.stButton > button:hover {
    background-color: #ff1f18;
    color: white;
}

/* INFO BOX */
.comparison-card {
    background: linear-gradient(
        145deg,
        #17171c,
        #0e0e12
    );

    padding: 25px;

    border-radius: 18px;

    border: 1px solid #33333a;

    text-align: center;

    box-shadow: 0px 8px 25px rgba(0,0,0,0.5);
}

.driver-name {
    font-size: 25px;
    font-weight: 800;
}

.vs {
    font-size: 28px;
    font-weight: 900;
    color: #e10600;
    padding-top: 20px;
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
        [
            "Country",
            "Location",
            "EventDate",
            "EventName"
        ]
    ]

    all_results = []

    for _, event in schedule.iterrows():

        event_name = event["EventName"]

        try:

            session = fastf1.get_session(
                2025,
                event_name,
                "R"
            )

            session.load(
                laps=False,
                telemetry=False,
                weather=False,
                messages=False
            )

            results = session.results

            if results is None or results.empty:
                continue

            columns = [
                "TeamName",
                "FullName",
                "Position",
                "Time",
                "Status",
                "Points",
                "Laps"
            ]

            available_columns = [
                c for c in columns
                if c in results.columns
            ]

            results = results[
                available_columns
            ].copy()

            results["Venue"] = event_name
            results["Country"] = event["Country"]
            results["Location"] = event["Location"]
            results["EventDate"] = event["EventDate"]

            all_results.append(results)

        except Exception:
            continue

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

with st.spinner("🏎️ Loading Formula 1 2025 data..."):

    final = load_f1_data()


if final.empty:

    st.error(
        "❌ Unable to load F1 data using FastF1."
    )

    st.stop()


# ============================================================
# CLEAN DATA
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

final["EventDate"] = pd.to_datetime(
    final["EventDate"],
    errors="coerce"
)


# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="hero">

    <div class="hero-title">
        🏎️ FORMULA 1
    </div>

    <div class="hero-subtitle">
        2025 Racing Analytics & Championship Intelligence
    </div>

    <div class="red-line"></div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "# 🏎️ F1 DASHBOARD"
)

st.sidebar.markdown(
    "### 2025 Season"
)

st.sidebar.write(
    "Explore race results, driver performance and head-to-head comparisons."
)

st.sidebar.markdown("---")


venues = sorted(
    final["Venue"].dropna().unique()
)

selected_venue = st.sidebar.selectbox(
    "🏁 Select Race",
    venues
)


drivers = sorted(
    final["FullName"].dropna().unique()
)

selected_driver = st.sidebar.selectbox(
    "👤 Driver",
    ["All Drivers"] + drivers
)


st.sidebar.markdown("---")

st.sidebar.info(
    "Data source: FastF1"
)


# ============================================================
# RACE FILTER
# ============================================================

race_data = final[
    final["Venue"] == selected_venue
].copy()


# ============================================================
# KPI
# ============================================================

st.markdown(
    '<div class="section-title">📊 Race Overview</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)


num_drivers = race_data[
    "FullName"
].nunique()


total_points = race_data[
    "Points"
].sum()


winner_data = race_data.sort_values(
    "Position"
)

winner = "N/A"

if not winner_data.empty:
    winner = winner_data.iloc[0]["FullName"]


highest_points = race_data[
    "Points"
].max()


with col1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Race</div>
            <div class="kpi-value">
                {selected_venue}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Drivers</div>
            <div class="kpi-value">
                {num_drivers}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Race Winner</div>
            <div class="kpi-value">
                {winner}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Top Points</div>
            <div class="kpi-value">
                {highest_points}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DRIVER POINTS
# ============================================================

st.markdown(
    '<div class="section-title">🏆 Driver Points</div>',
    unsafe_allow_html=True
)


chart_data = race_data.sort_values(
    "Points",
    ascending=True
)


fig = px.bar(
    chart_data,
    x="Points",
    y="FullName",
    orientation="h",
    text="Points",
    hover_data=[
        "TeamName",
        "Position",
        "Status",
        "Laps"
    ]
)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    template="plotly_dark",
    height=600,
    paper_bgcolor="#08080b",
    plot_bgcolor="#08080b",
    font=dict(color="white"),
    xaxis_title="Points",
    yaxis_title="Driver"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# DRIVER PERFORMANCE
# ============================================================

if selected_driver != "All Drivers":

    st.markdown(
        '<div class="section-title">👤 Driver Performance</div>',
        unsafe_allow_html=True
    )

    driver_data = final[
        final["FullName"] == selected_driver
    ].copy()

    driver_data = driver_data.sort_values(
        "EventDate"
    )

    fig_driver = px.line(
        driver_data,
        x="Venue",
        y="Points",
        markers=True,
        title=f"{selected_driver} — Race Points"
    )

    fig_driver.update_layout(
        template="plotly_dark",
        paper_bgcolor="#08080b",
        plot_bgcolor="#08080b",
        font=dict(color="white"),
        height=450
    )

    st.plotly_chart(
        fig_driver,
        use_container_width=True
    )


# ============================================================
# ============================================================
# DRIVER VS DRIVER COMPARISON
# ============================================================
# ============================================================

st.markdown(
    '<div class="section-title">⚔️ Driver vs Driver Comparison</div>',
    unsafe_allow_html=True
)

st.write(
    "Select two drivers to compare their 2025 season performance."
)


compare_col1, compare_col2 = st.columns(2)


with compare_col1:

    driver_1 = st.selectbox(
        "🔴 Driver 1",
        drivers,
        key="driver_1"
    )


with compare_col2:

    driver_2 = st.selectbox(
        "⚫ Driver 2",
        drivers,
        index=1 if len(drivers) > 1 else 0,
        key="driver_2"
    )


# Prevent same driver
if driver_1 == driver_2:

    st.warning(
        "⚠️ Please select two different drivers."
    )

else:

    # --------------------------------------------------------
    # DRIVER DATA
    # --------------------------------------------------------

    d1 = final[
        final["FullName"] == driver_1
    ].copy()

    d2 = final[
        final["FullName"] == driver_2
    ].copy()

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    d1_points = d1["Points"].sum()
    d2_points = d2["Points"].sum()

    d1_wins = (
        d1["Position"] == 1
    ).sum()

    d2_wins = (
        d2["Position"] == 1
    ).sum()

    d1_podiums = (
        d1["Position"] <= 3
    ).sum()

    d2_podiums = (
        d2["Position"] <= 3
    ).sum()

    d1_avg_position = d1[
        "Position"
    ].mean()

    d2_avg_position = d2[
        "Position"
    ].mean()

    d1_laps = d1["Laps"].sum()
    d2_laps = d2["Laps"].sum()


    # ========================================================
    # DRIVER HEADER
    # ========================================================

    c1, c2, c3 = st.columns([4, 2, 4])


    with c1:

        st.markdown(
            f"""
            <div class="comparison-card">

                <div class="driver-name">
                    🔴 {driver_1}
                </div>

                <p>
                    {d1["TeamName"].mode().iloc[0]}
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )


    with c2:

        st.markdown(
            """
            <div class="comparison-card">

                <div class="vs">
                    VS
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with c3:

        st.markdown(
            f"""
            <div class="comparison-card">

                <div class="driver-name">
                    ⚫ {driver_2}
                </div>

                <p>
                    {d2["TeamName"].mode().iloc[0]}
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # COMPARISON KPIs
    # ========================================================

    st.markdown(
        "### 📊 Head-to-Head Statistics"
    )


    stats = [
        (
            "Championship Points",
            d1_points,
            d2_points
        ),
        (
            "Race Wins",
            d1_wins,
            d2_wins
        ),
        (
            "Podiums",
            d1_podiums,
            d2_podiums
        ),
        (
            "Average Finish",
            round(d1_avg_position, 2),
            round(d2_avg_position, 2)
        ),
        (
            "Total Laps",
            d1_laps,
            d2_laps
        )
    ]


    for stat_name, value1, value2 in stats:

        col_a, col_b, col_c = st.columns([4, 3, 4])


        with col_a:

            st.markdown(
                f"""
                <div class="kpi-card">

                    <div class="kpi-title">
                        {stat_name}
                    </div>

                    <div class="kpi-value">
                        {value1}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


        with col_b:

            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    padding-top:35px;
                    font-weight:800;
                    color:#777;
                ">
                    VS
                </div>
                """,
                unsafe_allow_html=True
            )


        with col_c:

            st.markdown(
                f"""
                <div class="kpi-card">

                    <div class="kpi-title">
                        {stat_name}
                    </div>

                    <div class="kpi-value">
                        {value2}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


    # ========================================================
    # POINTS COMPARISON
    # ========================================================

    st.markdown(
        "### 📈 Race-by-Race Points Comparison"
    )


    comparison = pd.merge(
        d1[
            [
                "Venue",
                "EventDate",
                "Points"
            ]
        ],
        d2[
            [
                "Venue",
                "EventDate",
                "Points"
            ]
        ],
        on=["Venue", "EventDate"],
        how="outer",
        suffixes=(
            f"_{driver_1}",
            f"_{driver_2}"
        )
    )


    comparison = comparison.sort_values(
        "EventDate"
    )


    fig_points = go.Figure()


    fig_points.add_trace(
        go.Scatter(
            x=comparison["Venue"],
            y=comparison[
                f"Points_{driver_1}"
            ],
            mode="lines+markers",
            name=driver_1
        )
    )


    fig_points.add_trace(
        go.Scatter(
            x=comparison["Venue"],
            y=comparison[
                f"Points_{driver_2}"
            ],
            mode="lines+markers",
            name=driver_2
        )
    )


    fig_points.update_layout(
        template="plotly_dark",
        height=500,
        paper_bgcolor="#08080b",
        plot_bgcolor="#08080b",
        title="Points Per Race",
        xaxis_title="Race",
        yaxis_title="Points"
    )


    st.plotly_chart(
        fig_points,
        use_container_width=True
    )


    # ========================================================
    # FINISHING POSITION COMPARISON
    # ========================================================

    st.markdown(
        "### 🏁 Finishing Position Comparison"
    )


    position_comparison = pd.merge(
        d1[
            [
                "Venue",
                "EventDate",
                "Position"
            ]
        ],
        d2[
            [
                "Venue",
                "EventDate",
                "Position"
            ]
        ],
        on=["Venue", "EventDate"],
        how="outer",
        suffixes=(
            f"_{driver_1}",
            f"_{driver_2}"
        )
    )


    position_comparison = position_comparison.sort_values(
        "EventDate"
    )


    fig_position = go.Figure()


    fig_position.add_trace(
        go.Scatter(
            x=position_comparison["Venue"],
            y=position_comparison[
                f"Position_{driver_1}"
            ],
            mode="lines+markers",
            name=driver_1
        )
    )


    fig_position.add_trace(
        go.Scatter(
            x=position_comparison["Venue"],
            y=position_comparison[
                f"Position_{driver_2}"
            ],
            mode="lines+markers",
            name=driver_2
        )
    )


    fig_position.update_yaxes(
        autorange="reversed"
    )


    fig_position.update_layout(
        template="plotly_dark",
        height=500,
        paper_bgcolor="#08080b",
        plot_bgcolor="#08080b",
        title="Race Finishing Position",
        xaxis_title="Race",
        yaxis_title="Finishing Position"
    )


    st.plotly_chart(
        fig_position,
        use_container_width=True
    )


    # ========================================================
    # HEAD TO HEAD TABLE
    # ========================================================

    st.markdown(
        "### 🏆 Head-to-Head Race Results"
    )


    h2h = pd.merge(
        d1[
            [
                "Venue",
                "Position",
                "Points"
            ]
        ],
        d2[
            [
                "Venue",
                "Position",
                "Points"
            ]
        ],
        on="Venue",
        how="outer",
        suffixes=(
            f"_{driver_1}",
            f"_{driver_2}"
        )
    )


    h2h["Winner"] = np.where(

        h2h[
            f"Position_{driver_1}"
        ]
        <
        h2h[
            f"Position_{driver_2}"
        ],

        driver_1,

        np.where(

            h2h[
                f"Position_{driver_2}"
            ]
            <
            h2h[
                f"Position_{driver_1}"
            ],

            driver_2,

            "Tie"
        )
    )


    st.dataframe(
        h2h,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TEAM PERFORMANCE
# ============================================================

st.markdown(
    '<div class="section-title">🏢 Team Performance</div>',
    unsafe_allow_html=True
)


team_points = (
    race_data
    .groupby("TeamName")["Points"]
    .sum()
    .reset_index()
    .sort_values(
        "Points",
        ascending=False
    )
)


fig_team = px.bar(
    team_points,
    x="TeamName",
    y="Points",
    text="Points",
    title=f"Team Points — {selected_venue}"
)


fig_team.update_traces(
    textposition="outside"
)


fig_team.update_layout(
    template="plotly_dark",
    paper_bgcolor="#08080b",
    plot_bgcolor="#08080b",
    font=dict(color="white"),
    height=450
)


st.plotly_chart(
    fig_team,
    use_container_width=True
)


# ============================================================
# RACE RESULTS
# ============================================================

st.markdown(
    '<div class="section-title">📋 Race Results</div>',
    unsafe_allow_html=True
)


display_columns = [
    "Position",
    "FullName",
    "TeamName",
    "Points",
    "Laps",
    "Status"
]


display_columns = [
    c for c in display_columns
    if c in race_data.columns
]


results_display = race_data[
    display_columns
].sort_values(
    "Position"
)


st.dataframe(
    results_display,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DOWNLOAD
# ============================================================

st.markdown(
    '<div class="section-title">📥 Export Data</div>',
    unsafe_allow_html=True
)


csv = race_data.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="⬇️ Download Race Data",
    data=csv,
    file_name=f"{selected_venue}_2025.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align:center;
        color:#777;
        padding:20px;
    ">

        🏎️ Formula 1 2025 Racing Analytics

        <br><br>

        Built with
        <b>Streamlit</b> +
        <b>FastF1</b> +
        <b>Plotly</b>

    </div>
    """,
    unsafe_allow_html=True
)
