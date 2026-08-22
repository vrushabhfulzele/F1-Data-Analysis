import streamlit as st
import numpy as np

# ============================================================
# FASTF1 / NUMPY COMPATIBILITY FIX
# ============================================================
#
# Some FastF1 versions still reference np.NaN.
# NumPy 2.x removed np.NaN and uses np.nan instead.
#
# This patch must happen BEFORE importing fastf1.
# ============================================================

if not hasattr(np, "NaN"):
    np.NaN = np.nan

# ============================================================
# IMPORT FASTF1 AFTER THE PATCH
# ============================================================

try:
    import fastf1
except Exception as e:

    st.error("❌ FastF1 could not be loaded.")

    st.code(str(e))

    st.info(
        """
        FastF1 encountered a NumPy compatibility issue.

        The application attempted to apply the NumPy
        compatibility patch before loading FastF1.
        """
    )

    st.stop()


import pandas as pd
import plotly.express as px


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
# FASTF1 CACHE
# ============================================================

try:

    fastf1.Cache.enable_cache(
        "fastf1_cache"
    )

except Exception:
    pass


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800&display=swap'
    );

    .stApp {

        background:
            radial-gradient(
                circle at top right,
                rgba(225, 6, 0, 0.20),
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


    html,
    body,
    [class*="css"] {

        font-family:
            'Orbitron',
            sans-serif;
    }


    /* SIDEBAR */

    section[data-testid="stSidebar"] {

        background:
            linear-gradient(
                180deg,
                #090909,
                #151515
            );

        border-right:
            1px solid #292929;
    }


    /* HERO */

    .hero {

        padding: 40px;

        border-radius: 20px;

        margin-bottom: 25px;

        background:
            linear-gradient(
                135deg,
                rgba(225,6,0,0.95),
                rgba(12,12,12,0.98)
            );

        border:
            1px solid #3b3b3b;

        box-shadow:
            0 15px 45px
            rgba(0,0,0,0.60);
    }


    .hero-title {

        font-size: 45px;

        font-weight: 800;

        letter-spacing: 5px;

        color: white;
    }


    .hero-subtitle {

        margin-top: 8px;

        color: #dddddd;

        font-size: 14px;

        letter-spacing: 1px;
    }


    .hero-badge {

        display: inline-block;

        margin-top: 20px;

        padding:
            8px 18px;

        border-radius: 25px;

        background:
            rgba(0,0,0,0.45);

        border:
            1px solid #555;

        font-size: 11px;
    }


    /* SECTION */

    .section-title {

        margin-top: 30px;

        margin-bottom: 18px;

        padding-left: 12px;

        border-left:
            4px solid #e10600;

        font-size: 21px;

        font-weight: 700;
    }


    /* KPI */

    .kpi-card {

        padding: 20px;

        min-height: 125px;

        border-radius: 15px;

        background:
            linear-gradient(
                145deg,
                #181818,
                #0b0b0b
            );

        border:
            1px solid #303030;

        border-left:
            4px solid #e10600;

        box-shadow:
            0 8px 25px
            rgba(0,0,0,0.40);

        transition:
            all 0.25s ease;
    }


    .kpi-card:hover {

        transform:
            translateY(-5px);

        border-left-color:
            #ff2b20;

        box-shadow:
            0 12px 35px
            rgba(225,6,0,0.25);
    }


    .kpi-label {

        color: #888;

        font-size: 10px;

        text-transform:
            uppercase;

        letter-spacing: 1px;
    }


    .kpi-value {

        margin-top: 8px;

        font-size: 28px;

        font-weight: 800;

        color: white;
    }


    .kpi-subtitle {

        margin-top: 5px;

        color: #666;

        font-size: 10px;
    }


    /* FOOTER */

    .footer {

        margin-top: 45px;

        padding: 30px;

        text-align: center;

        color: #666;

        border-top:
            1px solid #222;

        font-size: 11px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-title">
            🏎️ FORMULA 1
        </div>

        <div class="hero-subtitle">
            2025 RACING ANALYTICS & CHAMPIONSHIP INTELLIGENCE
        </div>

        <div class="hero-badge">
            🔴 FASTF1 • STREAMLIT • PLOTLY • DATA ANALYTICS
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data(
    ttl=86400,
    show_spinner=False
)
def load_f1_data():

    schedule = fastf1.get_event_schedule(
        2025
    )

    # Keep actual race rounds only

    schedule = schedule[
        schedule["RoundNumber"] > 0
    ].copy()

    results_list = []

    total_races = len(schedule)

    progress = st.progress(
        0,
        text="Loading 2025 F1 races..."
    )

    for index, (_, race) in enumerate(
        schedule.iterrows(),
        start=1
    ):

        try:

            round_number = int(
                race["RoundNumber"]
            )

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

            results = session.results

            if results is None:
                continue

            if results.empty:
                continue


            columns = [

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

                for column in columns

                if column in results.columns

            ]


            race_results = results[
                available_columns
            ].copy()


            race_results["Round"] = (
                round_number
            )


            race_results["Venue"] = (
                race["Location"]
            )


            race_results["Country"] = (
                race["Country"]
            )


            race_results["EventName"] = (
                race["EventName"]
            )


            race_results["EventDate"] = (
                race["EventDate"]
            )


            results_list.append(
                race_results
            )


        except Exception:

            # If a particular race fails,
            # continue with the remaining races.

            continue


        progress.progress(
            index / total_races,
            text=(
                f"Loading race "
                f"{index}/{total_races}"
            )
        )


    progress.empty()


    if not results_list:

        return pd.DataFrame()


    final = pd.concat(
        results_list,
        ignore_index=True
    )


    # --------------------------------------------------------
    # CLEAN DATA
    # --------------------------------------------------------

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


    final["Round"] = pd.to_numeric(
        final["Round"],
        errors="coerce"
    )


    final["EventDate"] = pd.to_datetime(
        final["EventDate"],
        errors="coerce"
    )


    final = final.sort_values(
        [
            "Round",
            "Position"
        ]
    )


    return final


# ============================================================
# LOAD DATA
# ============================================================

with st.spinner(
    "🏁 Preparing Formula 1 analytics..."
):

    df = load_f1_data()


if df.empty:

    st.error(
        """
        ❌ No Formula 1 race data was loaded.

        Please refresh the application and try again.
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


drivers = sorted(
    df["FullName"]
    .dropna()
    .unique()
    .tolist()
)


teams = sorted(
    df["TeamName"]
    .dropna()
    .unique()
    .tolist()
)


venues = (
    df[
        [
            "Round",
            "Venue"
        ]
    ]
    .drop_duplicates()
    .sort_values("Round")
    ["Venue"]
    .tolist()
)


selected_driver = st.sidebar.selectbox(
    "👤 Select Driver",
    ["All Drivers"] + drivers
)


selected_team = st.sidebar.selectbox(
    "🏢 Select Team",
    ["All Teams"] + teams
)


selected_venue = st.sidebar.selectbox(
    "🏁 Select Race",
    ["All Races"] + venues
)


# ============================================================
# FILTER DATA
# ============================================================

filtered_df = df.copy()


if selected_driver != "All Drivers":

    filtered_df = filtered_df[
        filtered_df["FullName"]
        == selected_driver
    ]


if selected_team != "All Teams":

    filtered_df = filtered_df[
        filtered_df["TeamName"]
        == selected_team
    ]


if selected_venue != "All Races":

    filtered_df = filtered_df[
        filtered_df["Venue"]
        == selected_venue
    ]


# ============================================================
# KPI DATA
# ============================================================

race_count = df[
    "Round"
].nunique()


driver_count = df[
    "FullName"
].nunique()


team_count = df[
    "TeamName"
].nunique()


total_points = filtered_df[
    "Points"
].sum()


wins = (
    filtered_df["Position"] == 1
).sum()


podiums = (
    filtered_df["Position"] <= 3
).sum()


# ============================================================
# KPI CARDS
# ============================================================

st.markdown(
    '<div class="section-title">📊 Season Overview</div>',
    unsafe_allow_html=True
)


def make_kpi(
    label,
    value,
    subtitle
):

    return f"""
    <div class="kpi-card">

        <div class="kpi-label">
            {label}
        </div>

        <div class="kpi-value">
            {value}
        </div>

        <div class="kpi-subtitle">
            {subtitle}
        </div>

    </div>
    """


c1, c2, c3, c4, c5, c6 = st.columns(6)


with c1:

    st.markdown(
        make_kpi(
            "Races",
            race_count,
            "2025 Season"
        ),
        unsafe_allow_html=True
    )


with c2:

    st.markdown(
        make_kpi(
            "Drivers",
            driver_count,
            "Participants"
        ),
        unsafe_allow_html=True
    )


with c3:

    st.markdown(
        make_kpi(
            "Teams",
            team_count,
            "Constructors"
        ),
        unsafe_allow_html=True
    )


with c4:

    st.markdown(
        make_kpi(
            "Points",
            f"{total_points:.0f}",
            "Selected Filter"
        ),
        unsafe_allow_html=True
    )


with c5:

    st.markdown(
        make_kpi(
            "Wins",
            wins,
            "Race Wins"
        ),
        unsafe_allow_html=True
    )


with c6:

    st.markdown(
        make_kpi(
            "Podiums",
            podiums,
            "Top 3 Finishes"
        ),
        unsafe_allow_html=True
    )


# ============================================================
# CHAMPIONSHIP
# ============================================================

st.markdown(
    '<div class="section-title">🏆 Championship Leaderboard</div>',
    unsafe_allow_html=True
)


leaderboard = (

    df

    .groupby(
        [
            "FullName",
            "TeamName"
        ],
        as_index=False
    )

    .agg(

        Points=(
            "Points",
            "sum"
        ),

        Wins=(
            "Position",
            lambda x:
                (x == 1).sum()
        ),

        Podiums=(
            "Position",
            lambda x:
                (x <= 3).sum()
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
    height=400
)


# ============================================================
# CHARTS
# ============================================================

chart1, chart2 = st.columns(2)


# ------------------------------------------------------------
# TOP DRIVERS
# ------------------------------------------------------------

with chart1:

    st.markdown(
        '<div class="section-title">🥇 Top Drivers</div>',
        unsafe_allow_html=True
    )


    top_drivers = (

        leaderboard

        .head(10)

        .sort_values(
            "Points"
        )

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


    fig.update_layout(

        template="plotly_dark",

        height=450,

        paper_bgcolor="#080808",

        plot_bgcolor="#080808",

        xaxis_title="Points",

        yaxis_title=""

    )


    fig.update_traces(
        textposition="outside"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ------------------------------------------------------------
# CONSTRUCTORS
# ------------------------------------------------------------

with chart2:

    st.markdown(
        '<div class="section-title">🏢 Constructor Standings</div>',
        unsafe_allow_html=True
    )


    constructors = (

        df

        .groupby(
            "TeamName",
            as_index=False
        )

        ["Points"]

        .sum()

        .sort_values(
            "Points",
            ascending=False
        )

        .head(10)

        .sort_values(
            "Points"
        )

    )


    fig = px.bar(

        constructors,

        x="Points",

        y="TeamName",

        orientation="h",

        text="Points"

    )


    fig.update_layout(

        template="plotly_dark",

        height=450,

        paper_bgcolor="#080808",

        plot_bgcolor="#080808"

    )


    fig.update_traces(
        textposition="outside"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# DRIVER ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">👤 Driver Performance</div>',
    unsafe_allow_html=True
)


if selected_driver == "All Drivers":

    analysis_driver = drivers[0]

else:

    analysis_driver = selected_driver


driver_df = df[
    df["FullName"]
    == analysis_driver
].copy()


# ------------------------------------------------------------
# Driver points
# ------------------------------------------------------------

fig = px.line(

    driver_df.sort_values(
        "Round"
    ),

    x="Round",

    y="Points",

    markers=True,

    hover_data=[
        "Venue",
        "Position",
        "TeamName"
    ],

    title=(
        f"{analysis_driver}"
        " — Race Points"
    )

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
# RACE CHARTS
# ============================================================

chart3, chart4 = st.columns(2)


# ------------------------------------------------------------
# Race points
# ------------------------------------------------------------

with chart3:

    st.markdown(
        '<div class="section-title">🏁 Race Points</div>',
        unsafe_allow_html=True
    )


    race_points = (

        df

        .groupby(
            [
                "Round",
                "Venue"
            ],
            as_index=False
        )

        ["Points"]

        .sum()

        .sort_values(
            "Round"
        )

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


# ------------------------------------------------------------
# Finishing position
# ------------------------------------------------------------

with chart4:

    st.markdown(
        '<div class="section-title">📈 Finishing Position</div>',
        unsafe_allow_html=True
    )


    fig = px.line(

        driver_df.sort_values(
            "Round"
        ),

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

    race_df = df[
        df["Venue"]
        == selected_venue
    ].copy()


    race_df = race_df.sort_values(
        "Position"
    )


    info = race_df.iloc[0]


    r1, r2, r3, r4 = st.columns(4)


    with r1:

        st.metric(
            "🏁 Circuit",
            info["Venue"]
        )


    with r2:

        st.metric(
            "🌍 Country",
            info["Country"]
        )


    with r3:

        race_date = pd.to_datetime(
            info["EventDate"]
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
            race_df.iloc[0]["FullName"]
        )


    race_table = race_df[
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

        race_table,

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


comparison_drivers = st.multiselect(

    "Select drivers",

    drivers,

    default=drivers[:2]

)


if len(comparison_drivers) >= 2:

    comparison = df[
        df["FullName"].isin(
            comparison_drivers
        )
    ].copy()


    comparison = (

        comparison

        .groupby(
            [
                "Round",
                "FullName"
            ],
            as_index=False
        )

        ["Points"]

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
        "Select at least two drivers."
    )


# ============================================================
# RAW DATA
# ============================================================

with st.expander(
    "🔍 View Raw F1 Data"
):

    st.dataframe(

        filtered_df,

        use_container_width=True,

        hide_index=True

    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        🏎️ <b>FORMULA 1 RACING ANALYTICS</b>

        <br><br>

        2025 Championship Dashboard

        <br>

        Built with Streamlit • FastF1 • Pandas • Plotly

    </div>
    """,
    unsafe_allow_html=True
)
