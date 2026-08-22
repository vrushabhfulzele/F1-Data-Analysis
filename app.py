import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(
    page_title="F1 2025 Dashboard",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 2025 Analytics Dashboard")

st.success("✅ Streamlit application is running successfully!")

st.write("Testing F1 API connection...")

url = "https://api.jolpi.ca/ergast/f1/2025/races.json?limit=100"

try:

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    races = (
        data["MRData"]
        ["RaceTable"]
        ["Races"]
    )

    st.success(
        f"✅ F1 API connected successfully!"
    )

    st.write(
        f"Number of races found: **{len(races)}**"
    )

    race_data = []

    for race in races:

        race_data.append({
            "Round": race["round"],
            "Race": race["raceName"],
            "Circuit": race["Circuit"]["circuitName"],
            "Country": race["Circuit"]["Location"]["country"]
        })

    df = pd.DataFrame(race_data)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

except Exception as error:

    st.error(
        "❌ F1 API connection failed."
    )

    st.exception(error)
