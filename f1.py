```python
import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="F1 Driver Comparison",
    page_icon="🏎️",
    layout="wide"
)

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }

    .title {
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        color: #e10600;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #b8b8b8;
        font-size: 18px;
        margin-bottom: 30px;
    }

    .metric-card {
        background-color: #1a1d24;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #333;
    }

    .metric-title {
        color: #aaa;
        font-size: 14px;
    }

    .metric-value {
        color: white;
        font-size: 28px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.markdown(
    '<div class="title">🏎️ F1 DRIVER COMPARISON</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Compare Formula 1 drivers across the 2025 season</div>',
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():

    df = pd.read_csv("../datasets/F1_2025_GP.csv")

    # Fix driver name
    df["FullName"] = df["FullName"].replace(
        "Andrea Kimi Antonelli",
        "Kimi Antonelli"
    )

    return df


try:
    df = load_data()

except FileNotFoundError:
    st.error(
        "❌ Dataset not found. Make sure F1_2025_GP.csv is inside the datasets folder."
    )
    st.stop()


# ---------------------------------------------------------
# CLEAN DATA
# ---------------------------------------------------------
df["Points"] = pd.to_numeric(df["Points"], errors="coerce").fillna(0)

drivers = sorted(df["FullName"].dropna().unique())


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.header("🏁 Driver Selection")

d1 = st.sidebar.selectbox(
    "Select Driver 1",
    drivers,
    index=0
)

d2_options = [driver for driver in drivers if driver != d1]

d2 = st.sidebar.selectbox(
    "Select Driver 2",
    d2_options,
    index=0
)


# ---------------------------------------------------------
# DRIVER DATA
# ---------------------------------------------------------
s1 = df[df["FullName"] == d1].copy()
s2 = df[df["FullName"] == d2].copy()


# ---------------------------------------------------------
# CALCULATE TOTAL POINTS
# ---------------------------------------------------------
points1 = s1["Points"].sum()
points2 = s2["Points"].sum()

races1 = s1["Venue"].nunique()
races2 = s2["Venue"].nunique()

avg1 = s1["Points"].mean()
avg2 = s2["Points"].mean()


# ---------------------------------------------------------
# KPI SECTION
# ---------------------------------------------------------
st.subheader("📊 Driver Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        f"{d1} Points",
        f"{points1:.0f}"
    )

with col2:
    st.metric(
        f"{d2} Points",
        f"{points2:.0f}",
        delta=f"{points2 - points1:.0f}"
    )

with col3:
    st.metric(
        f"{d1} Avg Points",
        f"{avg1:.2f}"
    )

with col4:
    st.metric(
        f"{d2} Avg Points",
        f"{avg2:.2f}",
        delta=f"{avg2 - avg1:.2f}"
    )


# ---------------------------------------------------------
# CREATE COMPARISON DATA
# ---------------------------------------------------------
s1["Driver"] = d1
s2["Driver"] = d2

comparison = pd.concat([s1, s2])


# ---------------------------------------------------------
# POINTS BY RACE
# ---------------------------------------------------------
st.subheader("📈 Points by Grand Prix")

fig = px.line(
    comparison,
    x="Venue",
    y="Points",
    color="Driver",
    markers=True,
    title=f"{d1} vs {d2} — Points per Race",
    labels={
        "Venue": "Grand Prix",
        "Points": "Points"
    }
)

fig.update_layout(
    template="plotly_dark",
    height=550,
    xaxis=dict(
        tickangle=-45
    ),
    legend_title="Driver",
    hovermode="x unified"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ---------------------------------------------------------
# CUMULATIVE POINTS
# ---------------------------------------------------------
st.subheader("🏆 Cumulative Championship Points")

comparison["Cumulative Points"] = (
    comparison
    .groupby("Driver")["Points"]
    .cumsum()
)

fig2 = px.line(
    comparison,
    x="Venue",
    y="Cumulative Points",
    color="Driver",
    markers=True,
    title="Championship Progression",
    labels={
        "Venue": "Grand Prix",
        "Cumulative Points": "Total Points"
    }
)

fig2.update_layout(
    template="plotly_dark",
    height=550,
    xaxis=dict(
        tickangle=-45
    ),
    hovermode="x unified"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# ---------------------------------------------------------
# BAR CHART
# ---------------------------------------------------------
st.subheader("🏁 Total Championship Points")

total_points = pd.DataFrame({
    "Driver": [d1, d2],
    "Points": [points1, points2]
})

fig3 = px.bar(
    total_points,
    x="Driver",
    y="Points",
    text="Points",
    title="Total Points Comparison"
)

fig3.update_traces(
    textposition="outside"
)

fig3.update_layout(
    template="plotly_dark",
    height=450
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# ---------------------------------------------------------
# RACE-BY-RACE TABLE
# ---------------------------------------------------------
st.subheader("📋 Race-by-Race Comparison")

table = comparison[
    ["Venue", "Driver", "Points"]
].copy()

pivot_table = table.pivot(
    index="Venue",
    columns="Driver",
    values="Points"
).reset_index()

pivot_table = pivot_table.fillna(0)

st.dataframe(
    pivot_table,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# DRIVER SUMMARY
# ---------------------------------------------------------
st.subheader("🏆 Comparison Summary")

if points1 > points2:
    winner = d1
    difference = points1 - points2
elif points2 > points1:
    winner = d2
    difference = points2 - points1
else:
    winner = "Tie"
    difference = 0


if winner != "Tie":
    st.success(
        f"🏆 **{winner}** is ahead by **{difference:.0f} points**."
    )
else:
    st.info("🤝 Both drivers have the same number of points.")


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("---")

st.markdown(
    "<center>🏎️ F1 2025 Driver Analytics Dashboard</center>",
    unsafe_allow_html=True
)
```
