import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="F1 2025 | Racing Analytics",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# F1 COLOR PALETTE
# ============================================================

F1_RED = "#E10600"
F1_RED_DARK = "#A30000"
F1_BLACK = "#080808"
F1_DARK = "#111111"
F1_CARD = "#181818"
F1_GREY = "#A7A7A7"
F1_WHITE = "#FFFFFF"
F1_GREEN = "#00D084"
F1_YELLOW = "#FFD700"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    f"""
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    .stApp {{
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(225, 6, 0, 0.18),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 80%,
                rgba(225, 6, 0, 0.10),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #050505 0%,
                #0b0b0b 45%,
                #151515 100%
            );

        color: white;
    }}

    /* Carbon-fiber effect */

    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;

        background-image:
            linear-gradient(
                45deg,
                rgba(255,255,255,0.025) 25%,
                transparent 25%
            ),
            linear-gradient(
                -45deg,
                rgba(255,255,255,0.025) 25%,
                transparent 25%
            );

        background-size: 8px 8px;

        pointer-events: none;

        z-index: 0;
    }}

    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }}


    /* ======================================================
       HEADER
       ====================================================== */

    .hero {{
        background:
            linear-gradient(
                135deg,
                rgba(225,6,0,0.95),
                rgba(120,0,0,0.92)
            );

        border-radius: 22px;

        padding: 35px 40px;

        margin-bottom: 25px;

        box-shadow:
            0 15px 40px rgba(0,0,0,0.45);

        border:
            1px solid rgba(255,255,255,0.12);

        position: relative;

        overflow: hidden;
    }}

    .hero::after {{
        content: "🏎️";

        position: absolute;

        right: 35px;
        bottom: -20px;

        font-size: 130px;

        opacity: 0.12;

        transform: rotate(-5deg);
    }}

    .hero-title {{
        font-size: 48px;
        font-weight: 900;

        letter-spacing: -1px;

        margin: 0;

        color: white;
    }}

    .hero-subtitle {{
        font-size: 17px;

        margin-top: 8px;

        color: rgba(255,255,255,0.82);
    }}

    .season-badge {{
        display: inline-block;

        margin-top: 15px;

        padding: 7px 16px;

        border-radius: 30px;

        background: rgba(0,0,0,0.25);

        border:
            1px solid rgba(255,255,255,0.2);

        font-size: 13px;

        font-weight: 700;

        letter-spacing: 1px;
    }}


    /* ======================================================
       SECTION HEADINGS
       ====================================================== */

    .section-title {{
        font-size: 24px;

        font-weight: 800;

        margin-top: 15px;
        margin-bottom: 18px;

        border-left:
            5px solid {F1_RED};

        padding-left: 12px;
    }}


    /* ======================================================
       KPI CARDS
       ====================================================== */

    .kpi-card {{
        background:
            linear-gradient(
                145deg,
                #1c1c1c,
                #101010
            );

        border-radius: 18px;

        padding: 22px;

        min-height: 135px;

        border:
            1px solid rgba(255,255,255,0.08);

        box-shadow:
            0 10px 25px rgba(0,0,0,0.35);

        transition:
            transform 0.25s ease,
            border-color 0.25s ease;

        position: relative;

        overflow: hidden;
    }}

    .kpi-card:hover {{
        transform: translateY(-5px);

        border-color:
            rgba(225,6,0,0.7);
    }}

    .kpi-card::after {{
        content: "";

        position: absolute;

        width: 80px;
        height: 80px;

        right: -25px;
        bottom: -25px;

        background:
            rgba(225,6,0,0.12);

        border-radius: 50%;
    }}

    .kpi-icon {{
        font-size: 25px;
    }}

    .kpi-title {{
        color: {F1_GREY};

        font-size: 13px;

        margin-top: 5px;

        text-transform: uppercase;

        letter-spacing: 1px;
    }}

    .kpi-value {{
        font-size: 32px;

        font-weight: 900;

        margin-top: 5px;

        color: white;
    }}


    /* ======================================================
       SIDEBAR
       ====================================================== */

    section[data-testid="stSidebar"] {{
        background:
            linear-gradient(
                180deg,
                #080808,
                #111111
            );

        border-right:
            1px solid rgba(255,255,255,0.08);
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: white;
    }}

    section[data-testid="stSidebar"] label {{
        color: #dddddd !important;
    }}


    /* ======================================================
       SELECTBOX
       ====================================================== */

    div[data-baseweb="select"] > div {{
        background-color: #1b1b1b;

        border:
            1px solid #333;

        border-radius: 10px;
    }}


    /* ======================================================
       TABS
       ====================================================== */

    button[data-baseweb="tab"] {{
        color: #bbbbbb;

        font-weight: 700;

        font-size: 15px;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: white;
    }}

    div[data-baseweb="tab-highlight"] {{
        background-color: {F1_RED};
    }}


    /* ======================================================
       METRIC
       ====================================================== */

    div[data-testid="stMetric"] {{
        background:
            linear-gradient(
                145deg,
                #1c1c1c,
                #111111
            );

        padding: 15px;

        border-radius: 15px;

        border:
            1px solid rgba(255,255,255,0.08);
    }}

    div[data-testid="stMetricLabel"] {{
        color: #aaa !important;
    }}

    div[data-testid="stMetricValue"] {{
        color: white !important;
    }}


    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton > button {{
        background:
            linear-gradient(
                90deg,
                {F1_RED},
                {F1_RED_DARK}
            );

        color: white;

        border: none;

        border-radius: 10px;

        font-weight: 700;

        padding: 10px 20px;
    }}

    .stButton > button:hover {{
        background: #ff1b14;

        color: white;
    }}


    /* ======================================================
       DATAFRAME
       ====================================================== */

    div[data-testid="stDataFrame"] {{
        border-radius: 15px;

        overflow: hidden;

        border:
            1px solid #333;
    }}


    /* ======================================================
       FOOTER
       ====================================================== */

    .footer {{
        text-align: center;

        color: #777;

        padding-top: 25px;

        font-size: 13px;
    }}

    .footer strong {{
        color: {F1_RED};
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HERO HEADER
# ============================================================

st.markdown(
    """
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
    """,
    unsafe_allow_html=True
)


# ============================================================
# API
# ============================================================

BASE_URL = "https://api.jolpi.ca/ergast/f1/2025"


# ============================================================
# LOAD DATA
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

        except Exception:

            continue

    return pd.DataFrame(
        all_results
    )


# ============================================================
# LOAD DATA
# ============================================================

try:

    with st.spinner(
        "🏎️ Loading Formula 1 race data..."
    ):

        df = load_f1_data()

except Exception as error:

    st.error(
        "❌ Unable to load F1 data."
    )

    st.exception(error)

    st.stop()


# ============================================================
# VALIDATION
# ============================================================

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
        text-align:center;
        font-size:28px;
        margin-bottom:5px;
    ">
        🏎️ F1 ANALYTICS
    </h1>

    <p style="
        text-align:center;
        color:#999;
        font-size:13px;
    ">
        2025 Championship Dashboard
    </p>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    "### 🎛️ Race Filters"
)

st.sidebar.caption(
    "Use the filters below to explore the championship."
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
# KPI
# ============================================================

st.markdown(
    '<div class="section-title">📊 Season Overview</div>',
    unsafe_allow_html=True
)


total_races = df["Venue"].nunique()

total_drivers = df["Driver"].nunique()

total_teams = df["Team"].nunique()

total_points = filtered_df[
    "Points"
].sum()


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-icon">
                🏁
            </div>

            <div class="kpi-title">
                Total Races
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


with col3:

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


with col4:

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
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🏆 CHAMPIONSHIP",
        "🏁 RACE ANALYSIS",
        "👤 DRIVER PERFORMANCE",
        "📋 RACE RESULTS"
    ]
)


# ============================================================
# TAB 1 — CHAMPIONSHIP
# ============================================================

with tab1:

    st.markdown(
        '<div class="section-title">'
        '🏆 Driver Championship'
        '</div>',
        unsafe_allow_html=True
    )


    standings = (
        df
        .groupby(
            "Driver",
            as_index=False
        )["Points"]
        .sum()
        .sort_values(
            "Points",
            ascending=False
        )
    )


    standings["Rank"] = range(
        1,
        len(standings) + 1
    )


    # --------------------------------------------------------
    # TOP 3
    # --------------------------------------------------------

    top3 = standings.head(3)


    p1, p2, p3 = st.columns(3)


    for index, col in enumerate(
        [p1, p2, p3]
    ):

        if index < len(top3):

            row = top3.iloc[index]

            rank = int(row["Rank"])

            driver = row["Driver"]

            points = row["Points"]


            medal = {
                1: "🥇",
                2: "🥈",
                3: "🥉"
            }.get(
                rank,
                "🏆"
            )


            with col:

                st.markdown(
                    f"""
                    <div class="kpi-card"
                         style="text-align:center;">

                        <div style="
                            font-size:40px;
                        ">
                            {medal}
                        </div>

                        <div style="
                            font-size:18px;
                            font-weight:800;
                        ">
                            {driver}
                        </div>

                        <div style="
                            color:#aaa;
                            margin-top:5px;
                        ">
                            Championship P{rank}
                        </div>

                        <div style="
                            font-size:28px;
                            font-weight:900;
                            color:{F1_RED};
                            margin-top:8px;
                        ">
                            {points:.0f} PTS
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


    st.markdown("")


    # --------------------------------------------------------
    # CHAMPIONSHIP CHART
    # --------------------------------------------------------

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
            "#3b0000",
            "#8b0000",
            "#E10600",
            "#ff3b30"
        ]
    )


    fig.update_traces(
        texttemplate="%{text:.0f}",
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Points: %{x}<extra></extra>"
        )
    )


    fig.update_layout(
        title="2025 Championship Points",
        height=650,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        margin=dict(
            l=20,
            r=50,
            t=70,
            b=20
        )
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # TABLE
    # --------------------------------------------------------

    display_standings = standings[
        [
            "Rank",
            "Driver",
            "Points"
        ]
    ]


    st.dataframe(
        display_standings,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.NumberColumn(
                "🏆 Rank",
                format="%d"
            ),
            "Driver": "👤 Driver",
            "Points": st.column_config.NumberColumn(
                "⭐ Points",
                format="%.1f"
            )
        }
    )


# ============================================================
# TAB 2 — RACE ANALYSIS
# ============================================================

with tab2:

    st.markdown(
        '<div class="section-title">'
        '🏁 Race Analysis'
        '</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # DRIVER RACE POINTS
    # --------------------------------------------------------

    if selected_venue == "All Races":

        race_points = (
            df
            .groupby(
                "Driver",
                as_index=False
            )["Points"]
            .sum()
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
            .groupby(
                "Driver",
                as_index=False
            )["Points"]
            .sum()
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
        color="Points",
        color_continuous_scale=[
            "#420000",
            "#A30000",
            "#E10600",
            "#ff4d45"
        ]
    )


    fig.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )


    fig.update_layout(
        title=chart_title,
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

    st.markdown(
        '<div class="section-title">'
        '🏢 Constructor Championship'
        '</div>',
        unsafe_allow_html=True
    )


    team_points = (
        df
        .groupby(
            "Team",
            as_index=False
        )["Points"]
        .sum()
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
            "#320000",
            "#780000",
            "#E10600",
            "#ff5b55"
        ]
    )


    fig2.update_traces(
        texttemplate="%{text:.0f}",
        textposition="outside"
    )


    fig2.update_layout(
        title="Constructor Championship",
        template="plotly_dark",
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        xaxis_tickangle=-35
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
        '<div class="section-title">'
        '👤 Driver Performance'
        '</div>',
        unsafe_allow_html=True
    )


    if selected_driver == "All Drivers":

        performance_driver = st.selectbox(
            "Select Driver",
            drivers,
            key="performance_driver"
        )

    else:

        performance_driver = selected_driver


    driver_df = (
        df[
            df["Driver"]
            == performance_driver
        ]
        .sort_values("Round")
        .copy()
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
        "📊 Avg Points",
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
    # POINTS CHART
    # --------------------------------------------------------

    st.markdown(
        "### 📈 Points Progression"
    )


    fig = px.area(
        driver_df,
        x="Venue",
        y="Points",
        markers=True
    )


    fig.update_traces(
        line=dict(
            color=F1_RED,
            width=4
        ),
        marker=dict(
            size=8,
            color=F1_RED
        ),
        fillcolor="rgba(225,6,0,0.18)"
    )


    fig.update_layout(
        title=(
            f"{performance_driver} — "
            "Points by Race"
        ),
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


    # --------------------------------------------------------
    # POSITION CHART
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
        markers=True
    )


    fig2.update_traces(
        line=dict(
            color=F1_YELLOW,
            width=3
        ),
        marker=dict(
            size=9,
            color=F1_YELLOW
        )
    )


    fig2.update_yaxes(
        autorange="reversed"
    )


    fig2.update_layout(
        title=(
            f"{performance_driver} — "
            "Race Finishing Position"
        ),
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
# TAB 4 — RACE RESULTS
# ============================================================

with tab4:

    st.markdown(
        '<div class="section-title">'
        '📋 Race Results'
        '</div>',
        unsafe_allow_html=True
    )


    result_columns = [
        "Round",
        "Venue",
        "Driver",
        "Team",
        "Position",
        "Grid",
        "Points",
        "Laps",
        "Status"
    ]


    results = (
        filtered_df[
            result_columns
        ]
        .sort_values(
            [
                "Round",
                "Position"
            ]
        )
    )


    st.info(
        f"🏎️ Showing "
        f"**{len(results):,}** race results"
    )


    st.dataframe(
        results,
        use_container_width=True,
        hide_index=True,
        height=600,
        column_config={

            "Round": st.column_config.NumberColumn(
                "🏁 Round"
            ),

            "Venue": "🏆 Grand Prix",

            "Driver": "👤 Driver",

            "Team": "🏢 Team",

            "Position": st.column_config.NumberColumn(
                "📍 Position"
            ),

            "Grid": st.column_config.NumberColumn(
                "🚦 Grid"
            ),

            "Points": st.column_config.NumberColumn(
                "⭐ Points",
                format="%.1f"
            ),

            "Laps": st.column_config.NumberColumn(
                "🔄 Laps"
            ),

            "Status": "📊 Status"
        }
    )


# ============================================================
# SIDEBAR EXPORT
# ============================================================

st.sidebar.markdown("---")

st.sidebar.markdown(
    "### 📥 Export Data"
)


csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")


st.sidebar.download_button(
    label="⬇️ Download CSV",
    data=csv_data,
    file_name="F1_2025_Analytics.csv",
    mime="text/csv",
    use_container_width=True
)


# ============================================================
# REFRESH
# ============================================================

st.sidebar.markdown("---")


if st.sidebar.button(
    "🔄 Refresh F1 Data",
    use_container_width=True
):

    st.cache_data.clear()

    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        🏎️ <strong>FORMULA 1 ANALYTICS</strong>

        <br><br>

        2025 Championship Dashboard

        <br>

        Built with Streamlit • Pandas • Plotly

    </div>
    """,
    unsafe_allow_html=True
)
