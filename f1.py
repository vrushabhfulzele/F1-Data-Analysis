import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="2025 F1 GP",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS - LIGHT F1 THEME
# ============================================================

st.markdown("""
<style>

    /* Main page */
    .stApp {
        background-color: #f4f5f7;
        color: #171717;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #dddddd;
    }

    /* Sidebar text */
    [data-testid="stSidebar"] * {
        color: #222222;
    }

    /* Main title */
    .main-title {
        font-size: 46px;
        font-weight: 800;
        color: #e10600;
        margin-bottom: 0;
        letter-spacing: -1px;
    }

    .subtitle {
        color: #666666;
        font-size: 17px;
        margin-bottom: 25px;
    }

    /* Section headings */
    .section-title {
        color: #222222;
        font-size: 25px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #dddddd;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    div[data-testid="stMetricLabel"] {
        color: #666666;
    }

    div[data-testid="stMetricValue"] {
        color: #222222;
    }

    /* Select boxes */
    div[data-baseweb="select"] > div {
        background-color: #ffffff;
        border-color: #cccccc;
    }

    /* Radio buttons */
    div[role="radiogroup"] {
        gap: 8px;
    }

    /* Dataframes */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
    }

    /* Horizontal separator */
    hr {
        border-color: #dddddd;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# PLOTLY LIGHT THEME
# ============================================================

PLOTLY_LAYOUT = dict(
    template="plotly_white",
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(
        color="#222222",
        family="Arial"
    ),
    title_font=dict(
        color="#222222",
        size=20
    ),
    xaxis=dict(
        title_font=dict(color="#444444"),
        tickfont=dict(color="#444444"),
        gridcolor="#eeeeee"
    ),
    yaxis=dict(
        title_font=dict(color="#444444"),
        tickfont=dict(color="#444444"),
        gridcolor="#eeeeee"
    ),
    margin=dict(
        l=50,
        r=30,
        t=70,
        b=80
    )
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv("F1_2025_GP.csv")

    df.columns = df.columns.str.strip()

    # Fix driver name
    df["FullName"] = df["FullName"].replace(
        "Andrea Kimi Antonelli",
        "Kimi Antonelli"
    )

    # Convert numeric columns
    df["Points"] = pd.to_numeric(
        df["Points"],
        errors="coerce"
    ).fillna(0)

    df["Laps"] = pd.to_numeric(
        df["Laps"],
        errors="coerce"
    ).fillna(0)

    df["PositionNumeric"] = pd.to_numeric(
        df["Position"],
        errors="coerce"
    )

    return df


df = load_data()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "## 🏎️ F1 2025"
)

st.sidebar.markdown(
    "**Analytics Dashboard**"
)

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Overview",
        "👤 Driver Analysis",
        "⚔️ Driver Comparison",
        "🏁 Team Analysis",
        "📍 Race Analysis",
        "📊 Championship"
    ],
    label_visibility="visible"
)

st.sidebar.markdown("---")

st.sidebar.info(
    "Explore driver, team and race performance "
    "throughout the 2025 F1 season."
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">FORMULA 1 2025</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Driver • Team • Race Performance Dashboard'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# OVERVIEW
# ============================================================

if page == "🏠 Overview":

    # KPI calculations
    total_drivers = df["FullName"].nunique()
    total_teams = df["TeamName"].nunique()
    total_races = df["Venue"].nunique()
    total_points = df["Points"].sum()

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🏎️ Drivers",
        total_drivers
    )

    c2.metric(
        "🏁 Teams",
        total_teams
    )

    c3.metric(
        "🌍 Grands Prix",
        total_races
    )

    c4.metric(
        "🏆 Total Points",
        int(total_points)
    )

    st.markdown("---")

    # --------------------------------------------------------
    # DRIVER STANDINGS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '🏆 Driver Championship'
        '</div>',
        unsafe_allow_html=True
    )

    driver_standings = (
        df.groupby("FullName")["Points"]
        .sum()
        .sort_values(ascending=True)
        .reset_index()
    )

    fig = px.bar(
        driver_standings,
        x="Points",
        y="FullName",
        orientation="h",
        text="Points",
        color="Points",
        color_continuous_scale=[
            "#ffcccc",
            "#ff4d4d",
            "#e10600"
        ]
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=650,
        coloraxis_showscale=False
    )

    fig.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # TEAM STANDINGS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '🏁 Constructor Championship'
        '</div>',
        unsafe_allow_html=True
    )

    team_standings = (
        df.groupby("TeamName")["Points"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig = px.bar(
        team_standings,
        x="TeamName",
        y="Points",
        text="Points",
        color="Points",
        color_continuous_scale=[
            "#ffcccc",
            "#ff4d4d",
            "#e10600"
        ]
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        coloraxis_showscale=False
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

elif page == "👤 Driver Analysis":

    drivers = sorted(
        df["FullName"].unique()
    )

    driver = st.selectbox(
        "Select Driver",
        drivers
    )

    d = df[
        df["FullName"] == driver
    ].copy()

    total_points = d["Points"].sum()

    avg_points = d["Points"].mean()

    best_points = d["Points"].max()

    valid_positions = (
        d["PositionNumeric"]
        .dropna()
    )

    best_finish = (
        int(valid_positions.min())
        if not valid_positions.empty
        else 0
    )

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🏆 Points",
        int(total_points)
    )

    c2.metric(
        "📊 Avg Points",
        round(avg_points, 2)
    )

    c3.metric(
        "🥇 Best Finish",
        best_finish
    )

    c4.metric(
        "🔥 Best Race",
        int(best_points)
    )

    st.markdown("---")

    # --------------------------------------------------------
    # POINTS BY RACE
    # --------------------------------------------------------

    fig = px.line(
        d,
        x="Venue",
        y="Points",
        markers=True,
        title=f"{driver} — Points by Race"
    )

    fig.update_traces(
        line=dict(
            color="#e10600",
            width=3
        ),
        marker=dict(
            size=9,
            color="#e10600"
        )
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # FINISHING POSITION
    # --------------------------------------------------------

    fig = px.line(
        d,
        x="Venue",
        y="PositionNumeric",
        markers=True,
        title=f"{driver} — Finishing Position"
    )

    fig.update_traces(
        line=dict(
            color="#1976d2",
            width=3
        ),
        marker=dict(
            size=9,
            color="#1976d2"
        )
    )

    fig.update_yaxes(
        autorange="reversed"
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # RACE POINTS
    # --------------------------------------------------------

    fig = px.bar(
        d,
        x="Venue",
        y="Points",
        color="Points",
        color_continuous_scale=[
            "#ffcccc",
            "#ff4d4d",
            "#e10600"
        ],
        title=f"{driver} — Race Points"
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        coloraxis_showscale=False,
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # DATA TABLE
    # --------------------------------------------------------

    st.subheader("Race Results")

    st.dataframe(
        d[
            [
                "Venue",
                "Position",
                "Time",
                "Status",
                "Points",
                "Laps",
                "TeamName"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# DRIVER COMPARISON
# ============================================================

elif page == "⚔️ Driver Comparison":

    drivers = sorted(
        df["FullName"].unique()
    )

    c1, c2 = st.columns(2)

    with c1:

        d1 = st.selectbox(
            "Driver 1",
            drivers,
            index=0
        )

    with c2:

        d2 = st.selectbox(
            "Driver 2",
            drivers,
            index=min(1, len(drivers)-1)
        )

    s1 = df[
        df["FullName"] == d1
    ].copy()

    s2 = df[
        df["FullName"] == d2
    ].copy()

    p1 = s1["Points"].sum()
    p2 = s2["Points"].sum()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        d1,
        int(p1)
    )

    c2.metric(
        d2,
        int(p2)
    )

    c3.metric(
        "Points Difference",
        int(abs(p1 - p2))
    )

    st.markdown("---")

    # --------------------------------------------------------
    # POINTS COMPARISON
    # --------------------------------------------------------

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=s1["Venue"],
            y=s1["Points"],
            mode="lines+markers",
            name=d1,
            line=dict(
                color="#e10600",
                width=3
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=s2["Venue"],
            y=s2["Points"],
            mode="lines+markers",
            name=d2,
            line=dict(
                color="#1976d2",
                width=3
            )
        )
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        title="Race-by-Race Points Comparison",
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # CUMULATIVE POINTS
    # --------------------------------------------------------

    s1["CumulativePoints"] = (
        s1["Points"].cumsum()
    )

    s2["CumulativePoints"] = (
        s2["Points"].cumsum()
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=s1["Venue"],
            y=s1["CumulativePoints"],
            mode="lines+markers",
            name=d1,
            line=dict(
                color="#e10600",
                width=3
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=s2["Venue"],
            y=s2["CumulativePoints"],
            mode="lines+markers",
            name=d2,
            line=dict(
                color="#1976d2",
                width=3
            )
        )
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        title="Cumulative Championship Points",
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # POSITION COMPARISON
    # --------------------------------------------------------

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=s1["Venue"],
            y=s1["PositionNumeric"],
            mode="lines+markers",
            name=d1
        )
    )

    fig.add_trace(
        go.Scatter(
            x=s2["Venue"],
            y=s2["PositionNumeric"],
            mode="lines+markers",
            name=d2
        )
    )

    fig.update_yaxes(
        autorange="reversed"
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        title="Finishing Position Comparison",
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# TEAM ANALYSIS
# ============================================================

elif page == "🏁 Team Analysis":

    teams = sorted(
        df["TeamName"].unique()
    )

    team = st.selectbox(
        "Select Team",
        teams
    )

    q = df[
        df["TeamName"] == team
    ]

    total = q["Points"].sum()

    driver_count = q["FullName"].nunique()

    race_count = q["Venue"].nunique()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "🏆 Team Points",
        int(total)
    )

    c2.metric(
        "👤 Drivers",
        driver_count
    )

    c3.metric(
        "🏁 Races",
        race_count
    )

    st.markdown("---")

    # --------------------------------------------------------
    # DRIVER CONTRIBUTION
    # --------------------------------------------------------

    r = (
        q.groupby("FullName")["Points"]
        .sum()
        .reset_index()
        .sort_values(
            "Points",
            ascending=False
        )
    )

    fig = px.bar(
        r,
        x="FullName",
        y="Points",
        color="FullName",
        text="Points",
        title=f"{team} — Driver Contribution"
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        showlegend=False
    )

    fig.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # TEAM POINTS BY RACE
    # --------------------------------------------------------

    race_points = (
        q.groupby("Venue")["Points"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        race_points,
        x="Venue",
        y="Points",
        color="Points",
        color_continuous_scale=[
            "#ffcccc",
            "#ff4d4d",
            "#e10600"
        ],
        title=f"{team} — Points by Race"
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        coloraxis_showscale=False,
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # PIE CHART
    # --------------------------------------------------------

    fig = px.pie(
        r,
        names="FullName",
        values="Points",
        hole=0.5,
        title=f"{team} — Driver Points Distribution"
    )

    fig.update_layout(
        **PLOTLY_LAYOUT
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# RACE ANALYSIS
# ============================================================

elif page == "📍 Race Analysis":

    venues = list(
        df["Venue"].unique()
    )

    venue = st.selectbox(
        "Select Grand Prix",
        venues
    )

    race = df[
        df["Venue"] == venue
    ].copy()

    winner = race[
        race["PositionNumeric"] == 1
    ]

    if not winner.empty:

        winner_name = winner.iloc[0]["FullName"]

        winner_team = winner.iloc[0]["TeamName"]

    else:

        winner_name = "N/A"
        winner_team = "N/A"

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "🥇 Winner",
        winner_name
    )

    c2.metric(
        "🏎️ Team",
        winner_team
    )

    c3.metric(
        "👥 Drivers",
        race["FullName"].nunique()
    )

    st.markdown("---")

    # --------------------------------------------------------
    # DRIVER POINTS
    # --------------------------------------------------------

    result = race.sort_values(
        "PositionNumeric"
    )

    fig = px.bar(
        result,
        x="FullName",
        y="Points",
        color="TeamName",
        title=f"{venue} — Driver Points"
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_tickangle=-60
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # POSITION VS POINTS
    # --------------------------------------------------------

    fig = px.scatter(
        race,
        x="PositionNumeric",
        y="Points",
        color="TeamName",
        hover_name="FullName",
        size="Laps",
        title=f"{venue} — Position vs Points"
    )

    fig.update_layout(
        **PLOTLY_LAYOUT
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # RACE CLASSIFICATION
    # --------------------------------------------------------

    st.subheader("Race Classification")

    st.dataframe(
        race[
            [
                "FullName",
                "TeamName",
                "Position",
                "Status",
                "Points",
                "Laps"
            ]
        ].sort_values(
            "PositionNumeric"
        ),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# CHAMPIONSHIP
# ============================================================

elif page == "📊 Championship":

    standings = (
        df.groupby(
            ["FullName", "TeamName"]
        )["Points"]
        .sum()
        .reset_index()
        .sort_values(
            "Points",
            ascending=False
        )
    )

    standings["Rank"] = range(
        1,
        len(standings) + 1
    )

    st.subheader(
        "🏆 2025 Driver Championship"
    )

    st.dataframe(
        standings[
            [
                "Rank",
                "FullName",
                "TeamName",
                "Points"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # --------------------------------------------------------
    # CHAMPIONSHIP BATTLE
    # --------------------------------------------------------

    st.subheader(
        "📈 Championship Battle"
    )

    selected_drivers = st.multiselect(
        "Select drivers",
        sorted(
            df["FullName"].unique()
        ),
        default=list(
            standings.head(5)["FullName"]
        )
    )

    fig = go.Figure()

    for driver in selected_drivers:

        temp = df[
            df["FullName"] == driver
        ].copy()

        temp["CumulativePoints"] = (
            temp["Points"].cumsum()
        )

        fig.add_trace(
            go.Scatter(
                x=temp["Venue"],
                y=temp["CumulativePoints"],
                mode="lines+markers",
                name=driver
            )
        )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        title="Cumulative Championship Points",
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # POINT DISTRIBUTION
    # --------------------------------------------------------

    fig = px.histogram(
        df,
        x="Points",
        color="TeamName",
        nbins=15,
        title="Race Points Distribution"
    )

    fig.update_layout(
        **PLOTLY_LAYOUT
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status_count = (
        df["Status"]
        .value_counts()
        .reset_index()
    )

    status_count.columns = [
        "Status",
        "Count"
    ]

    fig = px.pie(
        status_count,
        names="Status",
        values="Count",
        hole=0.45,
        title="Race Status Distribution"
    )

    fig.update_layout(
        **PLOTLY_LAYOUT
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Formula 1 2025 Analytics Dashboard • "
    "Built with Streamlit, Pandas & Plotly"
)
