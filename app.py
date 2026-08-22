import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# FastF1 import
# ---------------------------------------------------------

try:
    import fastf1
except Exception as e:
    st.error("❌ FastF1 could not be loaded.")
    st.code(str(e))
    st.info(
        "Please check that requirements.txt contains a current "
        "FastF1 version and redeploy the application."
    )
    st.stop()


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="F1 Racing Analytics",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------------------------------------------------
# FastF1 cache
# ---------------------------------------------------------

fastf1.Cache.enable_cache("fastf1_cache")


# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------

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

    html, body, [class*="css"] {
        font-family: 'Orbitron', sans-serif;
    }

    section[data-testid="stSidebar"] {
        background: #0d0d0d;
        border-right: 1px solid #292929;
    }

    .hero {
        padding: 35px;
        border-radius: 20px;
        margin-bottom: 25px;

        background:
            linear-gradient(
                135deg,
                rgba(225,6,0,0.95),
                rgba(15,15,15,0.97)
            );

        border: 1px solid #3a3a3a;

        box-shadow:
            0 15px 40px rgba(0,0,0,0.55);
    }

    .hero-title {
        font-size: 44px;
        font-weight: 800;
        letter-spacing: 4px;
    }

    .hero-subtitle {
        margin-top: 8px;
        color: #dddddd;
        font-size: 14px;
        letter-spacing: 1px;
    }

    .badge {
        display: inline-block;
        margin-top: 18px;
        padding: 8px 16px;
        border-radius: 20px;
        background: #111111;
        border: 1px solid #444444;
        font-size: 11px;
    }

    .section-title {
        margin-top: 28px;
        margin-bottom: 18px;
        padding-left: 12px;

        border-left: 4px solid #e10600;

        font-size: 21px;
        font-weight: 700;
    }

    .kpi {
        padding: 20px;
        min-height: 115px;

        border-radius: 14px;

        background:
            linear-gradient(
                145deg,
                #181818,
                #0b0b0b
            );

        border: 1px solid #2d2d2d;
        border-left: 4px solid #e10600;

        box-shadow:
            0 8px 25px rgba(0,0,0,0.35);
    }

    .kpi-label {
        color: #888888;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .kpi-value {
        margin-top: 8px;
        font-size: 28px;
        font-weight: 800;
    }

    .kpi-description {
        margin-top: 5px;
        color: #666666;
        font-size: 10px;
    }

    .footer {
        margin-top: 40px;
        padding: 25px;

        text-align: center;

        color: #666666;

        border-top: 1px solid #222222;

        font-size: 11px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.markdown(
    """
    <div class="hero">

        <div class="hero-title">
            🏎️ FORMULA 1
        </div>

        <div class="hero-subtitle">
            2025 RACING ANALYTICS & CHAMPIONSHIP INTELLIGENCE
        </div>

        <div class="badge">
            🔴 FASTF1 • STREAMLIT • PLOTLY
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# Load race data
# ---------------------------------------------------------

@st.cache_data(
    ttl=86400,
    show_spinner=False
)
def load_f1_data():

    schedule = fastf1.get_event_schedule(2025)

    # Only actual race rounds
    schedule = schedule[
        schedule["RoundNumber"] > 0
    ].copy()

    all_results = []

    progress = st.progress(
        0,
        text="Loading F1 race data..."
    )

    total = len(schedule)

    for counter, (_, race) in enumerate(
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

            if results is None or results.empty:
                continue

            wanted_columns = [
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
                for column in wanted_columns
                if column in results.columns
            ]

            results = results[
                available_columns
            ].copy()

            results["Round"] = round_number

            results["Venue"] = race[
                "Location"
            ]

            results["Country"] = race[
                "Country"
            ]

            results["EventName"] = race[
                "EventName"
            ]

            results["EventDate"] = race[
                "EventDate"
            ]

            all_results.append(results)

        except Exception:
            # Continue if one race fails
            continue

        progress.progress(
            counter / total,
            text=f"Loading race {counter} of {total}"
        )

    progress.empty()

    if not all_results:
        return pd.DataFrame()

    data = pd.concat(
        all_results,
        ignore_index=True
    )

    # -----------------------------------------------------
    # Clean columns
    # -----------------------------------------------------

    data["Position"] = pd.to_numeric(
        data["Position"],
        errors="coerce"
    )

    data["Points"] = pd.to_numeric(
        data["Points"],
        errors="coerce"
    ).fillna(0)

    data["Laps"] = pd.to_numeric(
        data["Laps"],
        errors="coerce"
    ).fillna(0)

    data["Round"] = pd.to_numeric(
        data["Round"],
        errors="coerce"
    )

    data["EventDate"] = pd.to_datetime(
        data["EventDate"],
        errors="coerce"
    )

    return data.sort_values(
        ["Round", "Position"]
    )


# ---------------------------------------------------------
# Get data
# ---------------------------------------------------------

with st.spinner(
    "🏁 Preparing the 2025 championship..."
):

    df = load_f1_data()


if df.empty:

    st.error(
        "❌ No F1 race data was returned."
    )

    st.stop()


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.title(
    "🏎️ F1 CONTROL CENTER"
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
        ["Round", "Venue"]
    ]
    .drop_duplicates()
    .sort_values("Round")["Venue"]
    .tolist()
)


selected_driver = st.sidebar.selectbox(
    "👤 Driver",
    ["All Drivers"] + drivers
)

selected_team = st.sidebar.selectbox(
    "🏢 Team",
    ["All Teams"] + teams
)

selected_venue = st.sidebar.selectbox(
    "🏁 Race",
    ["All Races"] + venues
)


# ---------------------------------------------------------
# Filters
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# KPI calculations
# ---------------------------------------------------------

race_count = df["Round"].nunique()

driver_count = df["FullName"].nunique()

team_count = df["TeamName"].nunique()

points = filtered_df["Points"].sum()

wins = (
    filtered_df["Position"] == 1
).sum()

podiums = (
    filtered_df["Position"] <= 3
).sum()


# ---------------------------------------------------------
# KPI cards
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">📊 Championship Overview</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4, c5, c6 = st.columns(6)


def create_kpi(
    label,
    value,
    description
):

    return f"""
    <div class="kpi">

        <div class="kpi-label">
            {label}
        </div>

        <div class="kpi-value">
            {value}
        </div>

        <div class="kpi-description">
            {description}
        </div>

    </div>
    """


with c1:

    st.markdown(
        create_kpi(
            "Races",
            race_count,
            "2025 Season"
        ),
        unsafe_allow_html=True
    )


with c2:

    st.markdown(
        create_kpi(
            "Drivers",
            driver_count,
            "Participants"
        ),
        unsafe_allow_html=True
    )


with c3:

    st.markdown(
        create_kpi(
            "Teams",
            team_count,
            "Constructors"
        ),
        unsafe_allow_html=True
    )


with c4:

    st.markdown(
        create_kpi(
            "Points",
            f"{points:.0f}",
            "Current Filter"
        ),
        unsafe_allow_html=True
    )


with c5:

    st.markdown(
        create_kpi(
            "Wins",
            wins,
            "Victories"
        ),
        unsafe_allow_html=True
    )


with c6:

    st.markdown(
        create_kpi(
            "Podiums",
            podiums,
            "Top 3"
        ),
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# Championship leaderboard
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">🏆 Driver Championship</div>',
    unsafe_allow_html=True
)

leaderboard = (
    df
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
    leaderboard["Points"].round(0)
)

st.dataframe(
    leaderboard,
    use_container_width=True,
    hide_index=True,
    height=400
)


# ---------------------------------------------------------
# Top drivers and teams
# ---------------------------------------------------------

col1, col2 = st.columns(2)


with col1:

    st.markdown(
        '<div class="section-title">🥇 Top 10 Drivers</div>',
        unsafe_allow_html=True
    )

    top = (
        leaderboard
        .head(10)
        .sort_values("Points")
    )

    fig = px.bar(
        top,
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
        plot_bgcolor="#080808"
    )

    fig.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with col2:

    st.markdown(
        '<div class="section-title">🏢 Constructor Standings</div>',
        unsafe_allow_html=True
    )

    constructor = (
        df
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
        .sort_values("Points")
    )

    fig = px.bar(
        constructor,
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


# ---------------------------------------------------------
# Driver analysis
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">👤 Driver Performance</div>',
    unsafe_allow_html=True
)

if selected_driver == "All Drivers":

    driver_for_analysis = drivers[0]

else:

    driver_for_analysis = selected_driver


driver_df = df[
    df["FullName"]
    == driver_for_analysis
].copy()


# ---------------------------------------------------------
# Driver points progression
# ---------------------------------------------------------

fig = px.line(
    driver_df.sort_values("Round"),
    x="Round",
    y="Points",
    markers=True,
    hover_data=[
        "Venue",
        "Position",
        "TeamName"
    ],
    title=f"{driver_for_analysis} — Race Points"
)

fig.update_layout(
    template="plotly_dark",
    height=450,
    paper_bgcolor="#080808",
    plot_bgcolor="#080808"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ---------------------------------------------------------
# Race performance
# ---------------------------------------------------------

col1, col2 = st.columns(2)


with col1:

    st.markdown(
        '<div class="section-title">🏁 Race Points</div>',
        unsafe_allow_html=True
    )

    race_points = (
        df
        .groupby(
            ["Round", "Venue"],
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
        driver_df.sort_values("Round"),
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
        plot_bgcolor="#080808"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ---------------------------------------------------------
# Selected race
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">🏁 Race Results</div>',
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

        date = pd.to_datetime(
            info["EventDate"]
        )

        st.metric(
            "📅 Date",
            date.strftime("%d %b %Y")
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
    ].copy()

    st.dataframe(
        race_table,
        use_container_width=True,
        hide_index=True,
        height=450
    )

else:

    st.info(
        "👈 Select a specific race from the sidebar "
        "to view its results."
    )


# ---------------------------------------------------------
# Driver comparison
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">⚔️ Driver Comparison</div>',
    unsafe_allow_html=True
)

comparison_drivers = st.multiselect(
    "Select drivers to compare",
    drivers,
    default=drivers[:2]
)

if len(comparison_drivers) >= 2:

    comparison = df[
        df["FullName"].isin(
            comparison_drivers
        )
    ]

    comparison = (
        comparison
        .groupby(
            ["Round", "FullName"],
            as_index=False
        )["Points"]
        .sum()
    )

    fig = px.line(
        comparison,
        x="Round",
        y="Points",
        color="FullName",
        markers=True
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


# ---------------------------------------------------------
# Raw data
# ---------------------------------------------------------

with st.expander("🔍 View Raw F1 Data"):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

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
