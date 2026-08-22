import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="F1 2025 Racing Analytics",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# F1 THEME + CUSTOM CSS
# ============================================================

st.markdown("""
<style>

/* =========================================================
   GLOBAL
   ========================================================= */

.stApp {

    background:
        radial-gradient(
            circle at 15% 20%,
            rgba(225,6,0,0.12),
            transparent 25%
        ),
        radial-gradient(
            circle at 85% 80%,
            rgba(225,6,0,0.10),
            transparent 25%
        ),
        #0b0b0b;

    color: white;
}


/* =========================================================
   MAIN CONTAINER
   ========================================================= */

.block-container {

    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1500px;

}


/* =========================================================
   F1 HERO
   ========================================================= */

.hero {

    position: relative;

    background:
        linear-gradient(
            135deg,
            rgba(0,0,0,0.97),
            rgba(20,20,20,0.94)
        );

    border-radius: 24px;

    padding: 45px 30px;

    margin-bottom: 25px;

    overflow: hidden;

    border:
        1px solid rgba(255,255,255,0.12);

    box-shadow:
        0 15px 40px rgba(0,0,0,0.45);

}


/* racing stripe */

.hero::before {

    content: "";

    position: absolute;

    left: -5%;

    right: -5%;

    bottom: 15px;

    height: 7px;

    background:

        repeating-linear-gradient(
            90deg,
            #ffffff 0px,
            #ffffff 35px,
            #e10600 35px,
            #e10600 70px
        );

    transform: skewX(-25deg);

    opacity: 0.9;

}


/* red glow */

.hero::after {

    content: "";

    position: absolute;

    width: 300px;

    height: 300px;

    right: -120px;

    top: -150px;

    background: #e10600;

    opacity: 0.15;

    border-radius: 50%;

    filter: blur(50px);

}


.hero-title {

    position: relative;

    z-index: 2;

    font-size: clamp(
        40px,
        7vw,
        72px
    );

    font-weight: 950;

    letter-spacing: 5px;

    color: white;

    text-align: center;

    text-shadow:
        0 0 15px rgba(225,6,0,0.45);

}


.hero-subtitle {

    position: relative;

    z-index: 2;

    text-align: center;

    color: #cfcfcf;

    font-size: 20px;

    margin-top: 8px;

}


.season-badge {

    position: relative;

    z-index: 2;

    display: table;

    margin: 20px auto 0 auto;

    background:
        linear-gradient(
            90deg,
            #e10600,
            #ff3b30
        );

    padding: 10px 22px;

    border-radius: 30px;

    color: white;

    font-size: 13px;

    font-weight: 800;

    letter-spacing: 1px;

    box-shadow:
        0 5px 20px rgba(225,6,0,0.35);

}


/* =========================================================
   SECTION HEADERS
   ========================================================= */

.section-title {

    font-size: 25px;

    font-weight: 800;

    color: white;

    margin-top: 20px;

    margin-bottom: 15px;

}


.red-line {

    height: 4px;

    width: 80px;

    background: #e10600;

    border-radius: 10px;

    margin-bottom: 18px;

}


/* =========================================================
   KPI CARDS
   ========================================================= */

.kpi-card {

    position: relative;

    background:
        linear-gradient(
            145deg,
            #181818,
            #0f0f0f
        );

    border-radius: 18px;

    padding: 22px;

    min-height: 145px;

    overflow: hidden;

    border:
        1px solid rgba(255,255,255,0.08);

    box-shadow:
        0 8px 25px rgba(0,0,0,0.35);

    transition:
        transform 0.25s ease,
        box-shadow 0.25s ease;

}


.kpi-card:hover {

    transform:
        translateY(-7px);

    box-shadow:
        0 15px 35px
        rgba(225,6,0,0.25);

}


.kpi-card::after {

    content: "";

    position: absolute;

    width: 80px;

    height: 80px;

    right: -25px;

    bottom: -25px;

    border-radius: 50%;

    background:
        rgba(225,6,0,0.15);

}


.kpi-icon {

    font-size: 28px;

}


.kpi-title {

    color: #999;

    font-size: 13px;

    text-transform: uppercase;

    letter-spacing: 1px;

    margin-top: 5px;

}


.kpi-value {

    color: white;

    font-size: 32px;

    font-weight: 900;

    margin-top: 5px;

}


.kpi-accent {

    color: #e10600;

}


/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            #080808,
            #141414
        );

    border-right:
        1px solid rgba(225,6,0,0.25);

}


section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label {

    color: white !important;

}


section[data-testid="stSidebar"] p {

    color: #bbbbbb;

}


/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button {

    background:
        linear-gradient(
            90deg,
            #e10600,
            #b30000
        );

    color: white;

    border: none;

    border-radius: 10px;

    font-weight: 800;

    padding: 10px 20px;

    transition: 0.2s;

}


.stButton > button:hover {

    transform: translateY(-2px);

    box-shadow:
        0 8px 20px
        rgba(225,6,0,0.35);

}


/* =========================================================
   DOWNLOAD BUTTON
   ========================================================= */

.stDownloadButton > button {

    background:
        linear-gradient(
            90deg,
            #e10600,
            #b30000
        );

    color: white;

    border: none;

    border-radius: 10px;

    font-weight: 800;

}


/* =========================================================
   TABS
   ========================================================= */

.stTabs [data-baseweb="tab-list"] {

    gap: 8px;

    background: #111111;

    padding: 8px;

    border-radius: 12px;

}


.stTabs [data-baseweb="tab"] {

    color: #bbbbbb;

    font-weight: 700;

    border-radius: 8px;

}


.stTabs [aria-selected="true"] {

    color: white !important;

    background:
        #e10600 !important;

}


/* =========================================================
   DATAFRAME
   ========================================================= */

[data-testid="stDataFrame"] {

    border-radius: 12px;

    overflow: hidden;

}


/* =========================================================
   INFO BOX
   ========================================================= */

.info-box {

    background:
        linear-gradient(
            90deg,
            rgba(225,6,0,0.15),
            rgba(255,255,255,0.03)
        );

    border-left:
        4px solid #e10600;

    padding: 15px;

    border-radius: 8px;

    color: #ddd;

}


/* =========================================================
   FOOTER
   ========================================================= */

.footer {

    text-align: center;

    color: #777;

    padding: 30px 0 10px 0;

    font-size: 13px;

}


.footer span {

    color: #e10600;

    font-weight: 800;

}


/* =========================================================
   MOBILE
   ========================================================= */

@media (max-width: 768px) {

    .hero {

        padding: 30px 15px;

    }

    .hero-subtitle {

        font-size: 15px;

    }

    .season-badge {

        font-size: 10px;

    }

}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HERO HEADER
# ============================================================

st.markdown("""
<div class="hero">

    <div class="hero-title">
        🏎️ FORMULA 1
    </div>

    <div class="hero-subtitle">
        2025 Racing Analytics & Championship Intelligence
    </div>

    <div class="season-badge">
        🔴 2025 SEASON • LIVE DATA • RACE ANALYTICS
    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# API CONFIGURATION
# ============================================================

BASE_URL = "https://api.jolpi.ca/ergast/f1/2025"


# ============================================================
# DATA LOADER
# ============================================================

@st.cache_data(
    ttl=86400,
    show_spinner=False
)
def load_f1_data():

    all_results = []

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


    for race in races:

        round_number = race.get("round")

        race_name = race.get(
            "raceName",
            "Unknown Race"
        )

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

            circuit = race.get(
                "Circuit",
                {}
            )

            location = circuit.get(
                "Location",
                {}
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


                driver_name = (
                    f"{driver.get('givenName', '')} "
                    f"{driver.get('familyName', '')}"
                ).strip()


                all_results.append({

                    "Round":
                        int(round_number),

                    "Venue":
                        race_name,

                    "Circuit":
                        circuit.get(
                            "circuitName",
                            "Unknown"
                        ),

                    "Country":
                        location.get(
                            "country",
                            "Unknown"
                        ),

                    "Driver":
                        driver_name,

                    "DriverCode":
                        driver.get(
                            "code",
                            ""
                        ),

                    "Team":
                        constructor.get(
                            "name",
                            "Unknown"
                        ),

                    "Position":
                        (
                            int(position)
                            if position
                            else None
                        ),

                    "Points":
                        float(
                            result.get(
                                "points",
                                0
                            )
                        ),

                    "Grid":
                        (
                            int(grid)
                            if grid
                            else None
                        ),

                    "Laps":
                        (
                            int(laps)
                            if laps
                            else 0
                        ),

                    "Status":
                        result.get(
                            "status",
                            ""
                        ),

                    "Time":
                        result.get(
                            "Time",
                            {}
                        ).get(
                            "time",
                            ""
                        )
                })


        except Exception:

            continue


    return pd.DataFrame(
        all_results
    )


# ============================================================
# LOAD DATA
# ============================================================

with st.spinner(
    "🏎️ Loading Formula 1 data..."
):

    try:

        df = load_f1_data()

    except Exception as error:

        st.error(
            "❌ Unable to load F1 data."
        )

        st.info(
            "Please refresh the page and try again."
        )

        st.stop()


if df.empty:

    st.error(
        "❌ No Formula 1 data available."
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

df["Grid"] = pd.to_numeric(
    df["Grid"],
    errors="coerce"
)

df["Laps"] = pd.to_numeric(
    df["Laps"],
    errors="coerce"
).fillna(0)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    """
    <h1 style="
        color:#e10600;
        text-align:center;
        font-size:30px;
    ">
        🏎️ F1 CONTROL
    </h1>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown(
    """
    <p style="
        text-align:center;
        color:#888;
    ">
        2025 Racing Dashboard
    </p>
    """,
    unsafe_allow_html=True
)


st.sidebar.markdown("---")


# ============================================================
# REFRESH
# ============================================================

if st.sidebar.button(
    "🔄 Refresh F1 Data",
    use_container_width=True
):

    st.cache_data.clear()

    st.rerun()


# ============================================================
# FILTERS
# ============================================================

st.sidebar.markdown(
    "### 🎛️ Race Filters"
)


venues = sorted(
    df["Venue"]
    .dropna()
    .unique()
)


drivers = sorted(
    df["Driver"]
    .dropna()
    .unique()
)


teams = sorted(
    df["Team"]
    .dropna()
    .unique()
)


selected_venue = st.sidebar.selectbox(
    "🏁 Race",
    ["All Races"] + list(venues)
)


selected_driver = st.sidebar.selectbox(
    "👤 Driver",
    ["All Drivers"] + list(drivers)
)


selected_team = st.sidebar.selectbox(
    "🏢 Team",
    ["All Teams"] + list(teams)
)


# ============================================================
# RESET FILTERS
# ============================================================

if st.sidebar.button(
    "🧹 Clear Filters",
    use_container_width=True
):

    st.session_state.clear()

    st.rerun()


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
# KPI CALCULATIONS
# ============================================================

total_races = df["Venue"].nunique()

total_drivers = df["Driver"].nunique()

total_teams = df["Team"].nunique()

total_points = filtered_df["Points"].sum()

total_laps = filtered_df["Laps"].sum()


# ============================================================
# DASHBOARD OVERVIEW
# ============================================================

st.markdown(
    """
    <div class="section-title">
        📊 SEASON OVERVIEW
    </div>

    <div class="red-line"></div>
    """,
    unsafe_allow_html=True
)


k1, k2, k3, k4 = st.columns(4)


with k1:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-icon">
                🏁
            </div>

            <div class="kpi-title">
                Grand Prix
            </div>

            <div class="kpi-value">
                {total_races}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with k2:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-icon">
                👤
            </div>

            <div class="kpi-title">
                Drivers
            </div>

            <div class="kpi-value">
                {total_drivers}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with k3:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-icon">
                🏢
            </div>

            <div class="kpi-title">
                Constructors
            </div>

            <div class="kpi-value">
                {total_teams}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with k4:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-icon">
                🏆
            </div>

            <div class="kpi-title">
                Selected Points
            </div>

            <div class="kpi-value">
                {total_points:.1f}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# ACTIVE FILTER MESSAGE
# ============================================================

if (
    selected_venue != "All Races"
    or selected_driver != "All Drivers"
    or selected_team != "All Teams"
):

    st.markdown(
        f"""
        <div class="info-box">

        🎯 <b>Active Filters</b><br><br>

        🏁 Race:
        <b>{selected_venue}</b>
        &nbsp;&nbsp; | &nbsp;&nbsp;

        👤 Driver:
        <b>{selected_driver}</b>
        &nbsp;&nbsp; | &nbsp;&nbsp;

        🏢 Team:
        <b>{selected_team}</b>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "🏆 Championship",
        "🏁 Race Analysis",
        "👤 Driver Performance",
        "🏢 Teams",
        "📋 Race Results"
    ]
)


# ============================================================
# TAB 1 — CHAMPIONSHIP
# ============================================================

with tab1:

    st.markdown(
        """
        <div class="section-title">
            🏆 DRIVER CHAMPIONSHIP
        </div>

        <div class="red-line"></div>
        """,
        unsafe_allow_html=True
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


    # --------------------------------------------------------
    # TOP 3
    # --------------------------------------------------------

    top3 = standings.head(3)


    c1, c2, c3 = st.columns(3)


    medals = ["🥇", "🥈", "🥉"]


    for col, (_, row), medal in zip(
        [c1, c2, c3],
        top3.iterrows(),
        medals
    ):

        with col:

            st.markdown(
                f"""
                <div class="kpi-card">

                    <div class="kpi-icon">
                        {medal}
                    </div>

                    <div class="kpi-title">
                        Championship Position {row["Rank"]}
                    </div>

                    <div class="kpi-value">
                        {row["Driver"]}
                    </div>

                    <div style="
                        color:#e10600;
                        font-weight:800;
                        margin-top:5px;
                    ">
                        {row["Points"]:.1f} POINTS
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


    st.markdown("### 📊 Championship Points")


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
        color="Points",
        color_continuous_scale=[
            "#330000",
            "#990000",
            "#e10600"
        ]
    )


    fig.update_traces(
        texttemplate="%{text:.0f}",
        textposition="outside"
    )


    fig.update_layout(
        template="plotly_dark",
        height=700,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        margin=dict(
            l=10,
            r=20,
            t=30,
            b=20
        )
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    st.markdown("### 📋 Championship Leaderboard")


    st.dataframe(
        standings,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 2 — RACE ANALYSIS
# ============================================================

with tab2:

    st.markdown(
        """
        <div class="section-title">
            🏁 RACE ANALYSIS
        </div>

        <div class="red-line"></div>
        """,
        unsafe_allow_html=True
    )


    race_selection = st.selectbox(
        "🏁 Select Race",
        ["All Races"] + list(venues),
        key="race_analysis"
    )


    if race_selection == "All Races":

        race_df = df.copy()

    else:

        race_df = df[
            df["Venue"]
            == race_selection
        ]


    race_points = (
        race_df
        .groupby("Driver")["Points"]
        .sum()
        .reset_index()
        .sort_values(
            "Points",
            ascending=False
        )
    )


    fig = px.bar(
        race_points,
        x="Driver",
        y="Points",
        text="Points",
        color="Points",
        color_continuous_scale=[
            "#330000",
            "#e10600"
        ]
    )


    fig.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )


    fig.update_layout(
        template="plotly_dark",
        height=550,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        xaxis_tickangle=-45
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # TEAM CHAMPIONSHIP
    # --------------------------------------------------------

    st.markdown("### 🏢 Constructor Championship")


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
        color="Points",
        color_continuous_scale=[
            "#330000",
            "#990000",
            "#e10600"
        ]
    )


    fig2.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )


    fig2.update_layout(
        template="plotly_dark",
        height=550,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        xaxis_tickangle=-45
    )


    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# ============================================================
# TAB 3 — DRIVER PERFORMANCE
# ============================================================

with tab3:

    st.markdown(
        """
        <div class="section-title">
            👤 DRIVER PERFORMANCE
        </div>

        <div class="red-line"></div>
        """,
        unsafe_allow_html=True
    )


    if selected_driver == "All Drivers":

        performance_driver = st.selectbox(
            "👤 Choose Driver",
            drivers,
            key="driver_performance"
        )

    else:

        performance_driver = selected_driver


    driver_df = df[
        df["Driver"]
        == performance_driver
    ].sort_values(
        "Round"
    )


    if driver_df.empty:

        st.warning(
            "No data available for this driver."
        )

    else:

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


        # ----------------------------------------------------
        # DRIVER KPI
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # POINTS BY RACE
        # ----------------------------------------------------

        st.markdown(
            "### 📈 Points by Race"
        )


        fig = px.line(
            driver_df,
            x="Venue",
            y="Points",
            markers=True
        )


        fig.update_traces(
            line=dict(
                color="#e10600",
                width=4
            ),
            marker=dict(
                size=9
            )
        )


        fig.update_layout(
            template="plotly_dark",
            height=500,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_tickangle=-45
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


        # ----------------------------------------------------
        # POSITION
        # ----------------------------------------------------

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
            markers=True
        )


        fig2.update_traces(
            line=dict(
                color="#ffffff",
                width=3
            ),
            marker=dict(
                size=9
            )
        )


        fig2.update_yaxes(
            autorange="reversed"
        )


        fig2.update_layout(
            template="plotly_dark",
            height=500,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_tickangle=-45
        )


        st.plotly_chart(
            fig2,
            use_container_width=True
        )


# ============================================================
# TAB 4 — TEAMS
# ============================================================

with tab4:

    st.markdown(
        """
        <div class="section-title">
            🏢 CONSTRUCTOR ANALYTICS
        </div>

        <div class="red-line"></div>
        """,
        unsafe_allow_html=True
    )


    team_summary = (
        df
        .groupby("Team")
        .agg(
            Points=("Points", "sum"),
            Drivers=("Driver", "nunique"),
            Races=("Venue", "nunique"),
            Laps=("Laps", "sum")
        )
        .reset_index()
        .sort_values(
            "Points",
            ascending=False
        )
    )


    team_summary["Rank"] = range(
        1,
        len(team_summary) + 1
    )


    team_summary = team_summary[
        [
            "Rank",
            "Team",
            "Points",
            "Drivers",
            "Races",
            "Laps"
        ]
    ]


    fig = px.bar(
        team_summary.sort_values(
            "Points"
        ),
        x="Points",
        y="Team",
        orientation="h",
        text="Points",
        color="Points",
        color_continuous_scale=[
            "#330000",
            "#e10600"
        ]
    )


    fig.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )


    fig.update_layout(
        template="plotly_dark",
        height=600,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    st.markdown(
        "### 📋 Constructor Standings"
    )


    st.dataframe(
        team_summary,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 5 — RACE RESULTS
# ============================================================

with tab5:

    st.markdown(
        """
        <div class="section-title">
            📋 RACE RESULTS
        </div>

        <div class="red-line"></div>
        """,
        unsafe_allow_html=True
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
        ],
        na_position="last"
    )


    st.write(
        f"🏎️ Showing **{len(results):,} race results**"
    )


    st.dataframe(
        results,
        use_container_width=True,
        hide_index=True,
        height=600
    )


# ============================================================
# DOWNLOAD
# ============================================================

st.sidebar.markdown("---")


st.sidebar.markdown(
    "### 📥 EXPORT DATA"
)


csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")


st.sidebar.download_button(
    label="⬇️ Download Filtered CSV",
    data=csv_data,
    file_name="F1_2025_filtered_results.csv",
    mime="text/csv",
    use_container_width=True
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        🏎️ <span>FORMULA 1</span>
        2025 Racing Analytics Dashboard

        <br><br>

        Built with
        <span>Streamlit</span> •
        <span>Pandas</span> •
        <span>Plotly</span>

        <br>

        Data powered by Jolpica F1 API

    </div>
    """,
    unsafe_allow_html=True
)
