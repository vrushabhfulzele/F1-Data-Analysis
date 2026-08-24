import streamlit as st
import fastf1
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="F1 2025 Race Analytics",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

    /* Main background */
    .stApp {
        background-color: #0b0b0f;
        color: white;
    }

    /* Header */
    .hero {
        background: linear-gradient(135deg, #111116, #1b0000);
        padding: 30px;
        border-radius: 18px;
        border: 1px solid #3a3a40;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 2px;
    }

    .hero-subtitle {
        font-size: 17px;
        color: #bbbbbb;
        margin-top: 5px;
    }

    .red-line {
        height: 4px;
        width: 100%;
        background: #e10600;
        margin-top: 18px;
        border-radius: 10px;
    }

    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(145deg, #15151b, #101014);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #303038;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.35);
    }

    .kpi-title {
        color: #999999;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .kpi-value {
        color: #ffffff;
        font-size: 30px;
        font-weight: 800;
        margin-top: 5px;
    }

    /* Section headings */
    .section-title {
        font-size: 24px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 10px;
        color: white;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111116;
    }

    /* Buttons */
    .stButton > button {
        background-color: #e10600;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #ff1e18;
        color: white;
    }

    /* Dataframe */
    .stDataFrame {
        border-radius: 12px;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# FASTF1 CACHE
# =========================================================

@st.cache_data(show_spinner=False)
def load_race_data():

    schedule = fastf1.get_event_schedule(2025)

    schedule = schedule[
        ['Country', 'Location', 'EventDate', 'EventName']
    ]

    all_results = []

    # Get only actual race events
    for _, event in schedule.iterrows():

        event_name = event['EventName']

        try:

            session = fastf1.get_session(
                2025,
                event_name,
                'R'
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

            required_columns = [
                'TeamName',
                'FullName',
                'Position',
                'Time',
                'Status',
                'Points',
                'Laps'
            ]

            # Check columns exist
            available_columns = [
                col for col in required_columns
                if col in results.columns
            ]

            results = results[available_columns].copy()

            results['Venue'] = event_name
            results['Country'] = event['Country']
            results['Location'] = event['Location']
            results['EventDate'] = event['EventDate']

            all_results.append(results)

        except Exception as e:
            # Ignore sessions that fail
            continue

    if not all_results:
        return pd.DataFrame()

    final = pd.concat(
        all_results,
        ignore_index=True
    )

    return final


# =========================================================
# LOAD DATA
# =========================================================

with st.spinner("🏎️ Loading 2025 Formula 1 race data..."):

    final = load_race_data()


# =========================================================
# ERROR CHECK
# =========================================================

if final.empty:

    st.error("""
    ❌ No Formula 1 data could be loaded.

    Possible reasons:

    - FastF1 could not connect to the data source
    - A session failed to load
    - Internet connection problem
    - FastF1 package compatibility issue
    """)

    st.stop()


# =========================================================
# DATA CLEANING
# =========================================================

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


# =========================================================
# HERO HEADER
# =========================================================

st.markdown("""
<div class="hero">

    <div class="hero-title">
        🏎️ FORMULA 1
    </div>

    <div class="hero-subtitle">
        2025 Race Analytics & Driver Performance Dashboard
    </div>

    <div class="red-line"></div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("## 🏎️ F1 ANALYTICS")

st.sidebar.markdown(
    "### 2025 Season"
)

st.sidebar.markdown(
    "Select a race venue to explore driver performance."
)

# Venue list
venues = sorted(
    final['Venue'].dropna().unique()
)

selected_venue = st.sidebar.selectbox(
    "🏁 Select Race",
    venues
)

st.sidebar.markdown("---")

# Driver filter
drivers = sorted(
    final['FullName'].dropna().unique()
)

selected_driver = st.sidebar.selectbox(
    "👤 Select Driver",
    ["All Drivers"] + drivers
)

st.sidebar.markdown("---")

st.sidebar.info(
    "Data powered by FastF1"
)


# =========================================================
# FILTER DATA
# =========================================================

race_data = final[
    final['Venue'] == selected_venue
].copy()


if selected_driver != "All Drivers":

    race_data = race_data[
        race_data['FullName'] == selected_driver
    ]


# =========================================================
# KPI SECTION
# =========================================================

st.markdown(
    '<div class="section-title">📊 Race Overview</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)


# Number of drivers
num_drivers = race_data['FullName'].nunique()

# Total points
total_points = race_data['Points'].sum()

# Winner
winner_data = final[
    final['Venue'] == selected_venue
].sort_values('Position')

winner = "N/A"

if not winner_data.empty:

    winner = winner_data.iloc[0]['FullName']


# Highest points
top_points = 0

if not race_data.empty:
    top_points = race_data['Points'].max()


with col1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Race</div>
            <div class="kpi-value">{selected_venue}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Drivers</div>
            <div class="kpi-value">{num_drivers}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Winner</div>
            <div class="kpi-value">{winner}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Highest Points</div>
            <div class="kpi-value">{top_points}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# DRIVER POINTS CHART
# =========================================================

st.markdown(
    '<div class="section-title">🏆 Driver Points</div>',
    unsafe_allow_html=True
)


chart_data = final[
    final['Venue'] == selected_venue
].copy()

chart_data = chart_data.sort_values(
    'Points',
    ascending=True
)


fig = px.bar(
    chart_data,
    x='Points',
    y='FullName',
    orientation='h',
    text='Points',
    hover_data=[
        'TeamName',
        'Position',
        'Status',
        'Laps'
    ],
    title=f"{selected_venue} — Driver Points"
)


fig.update_traces(
    textposition='outside'
)

fig.update_layout(

    template='plotly_dark',

    height=600,

    paper_bgcolor='#0b0b0f',

    plot_bgcolor='#0b0b0f',

    font=dict(
        color='white'
    ),

    title_font_size=22,

    xaxis=dict(
        title='Championship Points'
    ),

    yaxis=dict(
        title='Driver'
    ),

    margin=dict(
        l=20,
        r=50,
        t=70,
        b=40
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# =========================================================
# DRIVER PERFORMANCE
# =========================================================

if selected_driver != "All Drivers":

    st.markdown(
        '<div class="section-title">👤 Driver Performance</div>',
        unsafe_allow_html=True
    )

    driver_data = final[
        final['FullName'] == selected_driver
    ].copy()

    driver_data = driver_data.sort_values(
        'EventDate'
    )

    fig_driver = px.line(
        driver_data,
        x='Venue',
        y='Points',
        markers=True,
        title=f"{selected_driver} — Race Points"
    )

    fig_driver.update_layout(
        template='plotly_dark',
        paper_bgcolor='#0b0b0f',
        plot_bgcolor='#0b0b0f',
        font=dict(color='white'),
        height=400
    )

    st.plotly_chart(
        fig_driver,
        use_container_width=True
    )


# =========================================================
# TEAM PERFORMANCE
# =========================================================

st.markdown(
    '<div class="section-title">🏢 Team Performance</div>',
    unsafe_allow_html=True
)

team_points = (
    chart_data
    .groupby('TeamName')['Points']
    .sum()
    .reset_index()
    .sort_values(
        'Points',
        ascending=False
    )
)


fig_team = px.bar(
    team_points,
    x='TeamName',
    y='Points',
    text='Points',
    title=f"Team Points — {selected_venue}"
)

fig_team.update_traces(
    textposition='outside'
)

fig_team.update_layout(
    template='plotly_dark',
    paper_bgcolor='#0b0b0f',
    plot_bgcolor='#0b0b0f',
    font=dict(color='white'),
    height=450
)

st.plotly_chart(
    fig_team,
    use_container_width=True
)


# =========================================================
# RACE RESULTS TABLE
# =========================================================

st.markdown(
    '<div class="section-title">📋 Race Results</div>',
    unsafe_allow_html=True
)


display_columns = [
    'Position',
    'FullName',
    'TeamName',
    'Points',
    'Laps',
    'Status'
]

display_columns = [
    col for col in display_columns
    if col in race_data.columns
]

results_display = race_data[
    display_columns
].sort_values(
    'Position'
)


st.dataframe(
    results_display,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# DOWNLOAD DATA
# =========================================================

st.markdown(
    '<div class="section-title">📥 Export Data</div>',
    unsafe_allow_html=True
)


csv = race_data.to_csv(
    index=False
).encode('utf-8')


st.download_button(
    label="⬇️ Download Race Data CSV",
    data=csv,
    file_name=f"{selected_venue}_2025.csv",
    mime="text/csv"
)


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:#777;">
        🏎️ Formula 1 2025 Analytics Dashboard
        <br>
        Built with Streamlit + FastF1 + Plotly
    </div>
    """,
    unsafe_allow_html=True
)
