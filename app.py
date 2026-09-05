import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
from google import genai

warnings.filterwarnings("ignore")

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Food Delivery Analytics",
    page_icon="🚚",
    layout="wide"
)

# =========================================================
# PROFESSIONAL CSS
# =========================================================
st.markdown("""
<style>

.main {
    background-color: #f7f7f8;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.hero {
    background: linear-gradient(135deg, #172554, #1e3a8a);
    padding: 28px;
    border-radius: 18px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.10);
}

.hero h1 {
    font-size: 38px;
    margin-bottom: 5px;
}

.hero p {
    font-size: 17px;
    opacity: 0.9;
}

.kpi-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 15px rgba(0,0,0,0.06);
    text-align: center;
}

.kpi-title {
    color: #64748b;
    font-size: 14px;
    margin-bottom: 8px;
}

.kpi-value {
    color: #172554;
    font-size: 27px;
    font-weight: 700;
}

.question-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    border-left: 6px solid #991b1b;
    box-shadow: 0 4px 15px rgba(0,0,0,0.06);
    margin-bottom: 15px;
}

.question-title {
    color: #7f1d1d;
    font-size: 18px;
    font-weight: 700;
}

.insight-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    border-top: 5px solid #d97706;
    box-shadow: 0 4px 15px rgba(0,0,0,0.06);
    min-height: 150px;
}

.section-title {
    color: #172554;
    font-size: 25px;
    font-weight: 700;
    margin-top: 20px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="hero">
    <h1>🚚 Food Delivery Analytics</h1>
    <p>
        Data-driven analysis of delivery performance, traffic,
        distance, weather and operational factors.
    </p>
</div>
""", unsafe_allow_html=True)


# =========================================================
# LOAD & CLEAN DATA
# =========================================================
@st.cache_data
def load_data():

    file_path = "food_delivery_dataset.csv"

    df = pd.read_csv(file_path)

    original_rows = len(df)
    original_columns = len(df.columns)

    original_missing = int(df.isnull().sum().sum())
    original_duplicates = int(df.duplicated().sum())

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert numeric columns
    numeric_columns = [
        "Delivery_person_Age",
        "Delivery_person_Ratings",
        "Time_taken (min)",
        "distance_km"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove duplicates
    df = df.drop_duplicates()

    duplicates_removed = original_duplicates

    # Fill missing numerical values
    if "Delivery_person_Age" in df.columns:
        df["Delivery_person_Age"] = df["Delivery_person_Age"].fillna(
            df["Delivery_person_Age"].median()
        )

    if "Delivery_person_Ratings" in df.columns:
        df["Delivery_person_Ratings"] = df["Delivery_person_Ratings"].fillna(
            df["Delivery_person_Ratings"].median()
        )

    # Fill order time
    if "Time_Orderd" in df.columns:
        df["Time_Orderd"] = df["Time_Orderd"].fillna(
            df["Time_Orderd"].mode()[0]
        )

    # Essential columns
    essential_columns = [
        "Time_taken (min)",
        "distance_km",
        "Road_traffic_density",
        "Weather_conditions"
    ]

    existing_essential = [
        col for col in essential_columns
        if col in df.columns
    ]

    df = df.dropna(subset=existing_essential)

    # Remove invalid delivery times
    if "Time_taken (min)" in df.columns:
        df = df[df["Time_taken (min)"] > 0]

    # Calculate delivery speed
    if "distance_km" in df.columns and "Time_taken (min)" in df.columns:

        df["delivery_speed_kmh"] = (
            df["distance_km"] /
            (df["Time_taken (min)"] / 60)
        )

    remaining_missing = int(df.isnull().sum().sum())

    stats = {
        "original_rows": original_rows,
        "original_columns": original_columns,
        "original_missing": original_missing,
        "duplicates_removed": duplicates_removed,
        "remaining_missing": remaining_missing,
        "final_rows": len(df)
    }

    return df, stats


# =========================================================
# LOAD DATA
# =========================================================
try:

    df, stats = load_data()

except FileNotFoundError:

    st.error(
        "❌ food_delivery_dataset.csv not found. "
        "Please place the CSV file in the same folder as app.py."
    )

    st.stop()


# =========================================================
# SIDEBAR FILTERS
# =========================================================
st.sidebar.header("🎛️ Dashboard Filters")

filtered_df = df.copy()

# City
if "City" in df.columns:

    city_options = sorted(
        df["City"].dropna().unique().tolist()
    )

    selected_city = st.sidebar.multiselect(
        "City",
        city_options,
        default=city_options
    )

    if selected_city:
        filtered_df = filtered_df[
            filtered_df["City"].isin(selected_city)
        ]


# Traffic
if "Road_traffic_density" in df.columns:

    traffic_options = sorted(
        df["Road_traffic_density"].dropna().unique().tolist()
    )

    selected_traffic = st.sidebar.multiselect(
        "Road Traffic Density",
        traffic_options,
        default=traffic_options
    )

    if selected_traffic:
        filtered_df = filtered_df[
            filtered_df["Road_traffic_density"].isin(selected_traffic)
        ]


# Weather
if "Weather_conditions" in df.columns:

    weather_options = sorted(
        df["Weather_conditions"].dropna().unique().tolist()
    )

    selected_weather = st.sidebar.multiselect(
        "Weather Conditions",
        weather_options,
        default=weather_options
    )

    if selected_weather:
        filtered_df = filtered_df[
            filtered_df["Weather_conditions"].isin(selected_weather)
        ]


# Vehicle condition
if "Vehicle_condition" in df.columns:

    vehicle_options = sorted(
        df["Vehicle_condition"].dropna().unique().tolist()
    )

    selected_vehicle = st.sidebar.multiselect(
        "Vehicle Condition",
        vehicle_options,
        default=vehicle_options
    )

    if selected_vehicle:
        filtered_df = filtered_df[
            filtered_df["Vehicle_condition"].isin(selected_vehicle)
        ]


# =========================================================
# GEMINI API KEY
# =========================================================
st.sidebar.markdown("---")

api_key = st.sidebar.text_input(
    "Gemini API Key",
    type="password",
    help="Optional: Add your Gemini API key for AI-generated business explanation."
)


# =========================================================
# KPI SECTION
# =========================================================
st.markdown(
    '<div class="section-title">📊 Executive Performance Overview</div>',
    unsafe_allow_html=True
)

if len(filtered_df) > 0:

    total_deliveries = len(filtered_df)

    avg_delivery_time = filtered_df["Time_taken (min)"].mean()

    avg_distance = filtered_df["distance_km"].mean()

    avg_speed = filtered_df["delivery_speed_kmh"].mean()

    avg_rating = (
        filtered_df["Delivery_person_Ratings"].mean()
        if "Delivery_person_Ratings" in filtered_df.columns
        else np.nan
    )

    avg_age = (
        filtered_df["Delivery_person_Age"].mean()
        if "Delivery_person_Age" in filtered_df.columns
        else np.nan
    )

    max_delivery_time = filtered_df["Time_taken (min)"].max()

else:

    total_deliveries = 0
    avg_delivery_time = 0
    avg_distance = 0
    avg_speed = 0
    avg_rating = 0
    avg_age = 0
    max_delivery_time = 0


kpi_cols = st.columns(7)

kpis = [
    ("Total Deliveries", f"{total_deliveries:,}"),
    ("Avg Delivery Time", f"{avg_delivery_time:.1f} min"),
    ("Avg Distance", f"{avg_distance:.2f} km"),
    ("Avg Speed", f"{avg_speed:.2f} km/h"),
    ("Avg Rating", f"{avg_rating:.2f}"),
    ("Avg Driver Age", f"{avg_age:.1f}"),
    ("Max Delivery Time", f"{max_delivery_time:.0f} min")
]

for col, (title, value) in zip(kpi_cols, kpis):

    col.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# DATA QUALITY AUDIT
# =========================================================
st.markdown(
    '<div class="section-title">🧹 Data Quality & Cleaning Audit</div>',
    unsafe_allow_html=True
)

audit_cols = st.columns(5)

audit_values = [
    ("Original Records", stats["original_rows"]),
    ("Columns", stats["original_columns"]),
    ("Original Missing", stats["original_missing"]),
    ("Duplicates Removed", stats["duplicates_removed"]),
    ("Final Records", stats["final_rows"])
]

for col, (title, value) in zip(audit_cols, audit_values):

    col.metric(title, value)


with st.expander("🔎 View Cleaned Dataset"):

    st.dataframe(
        filtered_df.head(100),
        use_container_width=True
    )

with st.expander("📋 Data Types"):

    st.dataframe(
        filtered_df.dtypes.astype(str).to_frame("Data Type"),
        use_container_width=True
    )


# =========================================================
# COMPETITION QUESTIONS
# =========================================================
st.markdown(
    '<div class="section-title">🏆 Competition Questions</div>',
    unsafe_allow_html=True
)


# =========================================================
# Q1 TRAFFIC
# =========================================================
traffic_summary = (
    filtered_df
    .groupby("Road_traffic_density")["Time_taken (min)"]
    .mean()
    .sort_values(ascending=False)
)

q1_traffic = traffic_summary.index[0]
q1_time = traffic_summary.iloc[0]

st.markdown(
    f"""
    <div class="question-card">
        <div class="question-title">
            Q1. Which traffic level has the highest average delivery time?
        </div>
        <p>
            <b>{q1_traffic}</b> traffic has the highest average delivery time
            of <b>{q1_time:.2f} minutes</b>.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# Q2 DISTANCE
# =========================================================
distance_corr = filtered_df[
    ["distance_km", "Time_taken (min)"]
].corr().iloc[0, 1]

if distance_corr > 0.3:

    distance_statement = (
        f"Yes. Distance has a positive relationship with delivery time "
        f"(correlation = {distance_corr:.2f})."
    )

elif distance_corr > 0:

    distance_statement = (
        f"Yes, but the relationship is weak "
        f"(correlation = {distance_corr:.2f})."
    )

else:

    distance_statement = (
        f"The dataset does not show a positive relationship "
        f"(correlation = {distance_corr:.2f})."
    )


st.markdown(
    f"""
    <div class="question-card">
        <div class="question-title">
            Q2. Does distance affect delivery time?
        </div>
        <p>{distance_statement}</p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# Q3 WEATHER + TRAFFIC
# =========================================================
combo_summary = (
    filtered_df
    .groupby(
        ["Weather_conditions", "Road_traffic_density"]
    )["Time_taken (min)"]
    .mean()
    .sort_values(ascending=False)
)

if len(combo_summary) > 0:

    q3_combo = combo_summary.index[0]
    q3_time = combo_summary.iloc[0]

    q3_weather = q3_combo[0]
    q3_traffic = q3_combo[1]

else:

    q3_weather = "N/A"
    q3_traffic = "N/A"
    q3_time = 0


st.markdown(
    f"""
    <div class="question-card">
        <div class="question-title">
            Q3. Which weather + traffic combination causes the highest delay?
        </div>
        <p>
            <b>{q3_weather}</b> weather with
            <b>{q3_traffic}</b> traffic produces the highest
            average delivery time of <b>{q3_time:.2f} minutes</b>.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# CHART STYLE FUNCTION
# =========================================================
def style_chart(ax):

    ax.set_axisbelow(True)

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.20
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["left"].set_alpha(0.25)
    ax.spines["bottom"].set_alpha(0.25)


# =========================================================
# CHART 1 — TRAFFIC
# MAROON / RED / BURGUNDY
# =========================================================
st.markdown(
    '<div class="section-title">📈 Traffic Impact on Delivery Time</div>',
    unsafe_allow_html=True
)

fig, ax = plt.subplots(figsize=(10, 5))

traffic_plot = traffic_summary.sort_values(ascending=False)

traffic_colors = [
    "#4C0519",
    "#7F1D1D",
    "#991B1B",
    "#B91C1C",
    "#DC2626",
    "#EF4444"
]

bars = ax.bar(
    traffic_plot.index.astype(str),
    traffic_plot.values,
    color=traffic_colors[:len(traffic_plot)],
    edgecolor="#3F0712",
    linewidth=0.8
)

ax.set_title(
    "Average Delivery Time by Traffic Density",
    fontsize=16,
    fontweight="bold"
)

ax.set_xlabel("Road Traffic Density")
ax.set_ylabel("Average Delivery Time (minutes)")

for bar in bars:

    height = bar.get_height()

    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.3,
        f"{height:.1f}",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold"
    )

style_chart(ax)

plt.tight_layout()

st.pyplot(fig)

plt.close(fig)


# =========================================================
# CHART 2 — DISTANCE
# MAROON POINTS + GOLDEN REGRESSION
# =========================================================
st.markdown(
    '<div class="section-title">📍 Distance vs Delivery Time</div>',
    unsafe_allow_html=True
)

fig, ax = plt.subplots(figsize=(10, 5))

sns.regplot(
    data=filtered_df,
    x="distance_km",
    y="Time_taken (min)",
    scatter_kws={
        "alpha": 0.30,
        "s": 25,
        "color": "#7F1D1D"
    },
    line_kws={
        "color": "#D97706",
        "linewidth": 3
    },
    ax=ax
)

ax.set_title(
    "Relationship Between Distance and Delivery Time",
    fontsize=16,
    fontweight="bold"
)

ax.set_xlabel("Distance (km)")
ax.set_ylabel("Delivery Time (minutes)")

style_chart(ax)

plt.tight_layout()

st.pyplot(fig)

plt.close(fig)


# =========================================================
# CHART 3 — WEATHER
# GOLD / AMBER / MUSTARD
# =========================================================
st.markdown(
    '<div class="section-title">🌦️ Weather Impact on Delivery Time</div>',
    unsafe_allow_html=True
)

weather_summary = (
    filtered_df
    .groupby("Weather_conditions")["Time_taken (min)"]
    .mean()
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(10, 5))

weather_colors = [
    "#78350F",
    "#92400E",
    "#B45309",
    "#D97706",
    "#F59E0B",
    "#FBBF24",
    "#FCD34D"
]

bars = ax.bar(
    weather_summary.index.astype(str),
    weather_summary.values,
    color=weather_colors[:len(weather_summary)],
    edgecolor="#713F12",
    linewidth=0.8
)

ax.set_title(
    "Average Delivery Time by Weather Condition",
    fontsize=16,
    fontweight="bold"
)

ax.set_xlabel("Weather Condition")
ax.set_ylabel("Average Delivery Time (minutes)")

for bar in bars:

    height = bar.get_height()

    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.3,
        f"{height:.1f}",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold"
    )

style_chart(ax)

plt.tight_layout()

st.pyplot(fig)

plt.close(fig)


# =========================================================
# CHART 4 — VEHICLE CONDITION
# BURGUNDY / TERRACOTTA / ORANGE
# =========================================================
st.markdown(
    '<div class="section-title">🚗 Vehicle Condition Analysis</div>',
    unsafe_allow_html=True
)

vehicle_summary = (
    filtered_df
    .groupby("Vehicle_condition")["Time_taken (min)"]
    .mean()
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(10, 5))

vehicle_colors = [
    "#4C0519",
    "#7F1D1D",
    "#991B1B",
    "#C2410C",
    "#EA580C",
    "#F97316"
]

bars = ax.bar(
    vehicle_summary.index.astype(str),
    vehicle_summary.values,
    color=vehicle_colors[:len(vehicle_summary)],
    edgecolor="#431407",
    linewidth=0.8
)

ax.set_title(
    "Average Delivery Time by Vehicle Condition",
    fontsize=16,
    fontweight="bold"
)

ax.set_xlabel("Vehicle Condition")
ax.set_ylabel("Average Delivery Time (minutes)")

for bar in bars:

    height = bar.get_height()

    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.3,
        f"{height:.1f}",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold"
    )

style_chart(ax)

plt.tight_layout()

st.pyplot(fig)

plt.close(fig)


# =========================================================
# CHART 5 — CITY PERFORMANCE
# MAROON + GOLD ALTERNATING
# =========================================================
st.markdown(
    '<div class="section-title">🏙️ City Performance</div>',
    unsafe_allow_html=True
)

city_summary = (
    filtered_df
    .groupby("City")["Time_taken (min)"]
    .mean()
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(10, 5))

city_palette = [
    "#4C0519",
    "#991B1B",
    "#D97706",
    "#7F1D1D",
    "#F59E0B",
    "#B91C1C",
    "#C2410C",
    "#FBBF24"
]

bars = ax.bar(
    city_summary.index.astype(str),
    city_summary.values,
    color=[
        city_palette[i % len(city_palette)]
        for i in range(len(city_summary))
    ],
    edgecolor="#451A03",
    linewidth=0.8
)

ax.set_title(
    "Average Delivery Time by City",
    fontsize=16,
    fontweight="bold"
)

ax.set_xlabel("City")
ax.set_ylabel("Average Delivery Time (minutes)")

ax.tick_params(axis="x", rotation=15)

for bar in bars:

    height = bar.get_height()

    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.3,
        f"{height:.1f}",
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="bold"
    )

style_chart(ax)

plt.tight_layout()

st.pyplot(fig)

plt.close(fig)


# =========================================================
# BUSINESS INSIGHTS
# =========================================================
st.markdown(
    '<div class="section-title">💡 Business Insights</div>',
    unsafe_allow_html=True
)

insight_cols = st.columns(3)


# Insight 1
with insight_cols[0]:

    st.markdown(
        f"""
        <div class="insight-card">
            <h3>🚦 Traffic Bottleneck</h3>
            <p>
                <b>{q1_traffic}</b> traffic has the highest average
                delivery time at <b>{q1_time:.1f} minutes</b>.
                Traffic management should be a major operational priority.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# Insight 2
with insight_cols[1]:

    st.markdown(
        f"""
        <div class="insight-card">
            <h3>📍 Distance Effect</h3>
            <p>
                Distance shows a correlation of
                <b>{distance_corr:.2f}</b> with delivery time.
                Longer delivery routes can contribute to increased delays.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# Insight 3
with insight_cols[2]:

    st.markdown(
        f"""
        <div class="insight-card">
            <h3>🌦️ Weather + Traffic Risk</h3>
            <p>
                The combination of <b>{q3_weather}</b> weather and
                <b>{q3_traffic}</b> traffic creates the highest
                average delivery time of <b>{q3_time:.1f} minutes</b>.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# GEMINI AI EXPLANATION
# =========================================================
st.markdown(
    '<div class="section-title">🤖 AI-Powered Business Explanation</div>',
    unsafe_allow_html=True
)

if api_key:

    try:

        client = genai.Client(api_key=api_key)

        prompt = f"""
You are a senior business analyst.

Analyze these calculated findings from a food delivery dataset:

Highest traffic delay:
{q1_traffic} traffic = {q1_time:.2f} minutes

Distance correlation:
{distance_corr:.2f}

Worst weather + traffic combination:
Weather = {q3_weather}
Traffic = {q3_traffic}
Average delivery time = {q3_time:.2f} minutes

Write a concise executive explanation covering:

1. What the findings mean
2. Why these operational factors may matter
3. Three practical recommendations for a food delivery company

Do not invent numerical results.
Only interpret the provided findings.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        st.success("AI analysis generated successfully.")

        st.write(response.text)

    except Exception as e:

        st.error(
            f"AI analysis could not be generated: {e}"
        )

else:

    st.info(
        "🔑 Add your Gemini API key in the sidebar "
        "to generate an AI-powered executive explanation."
    )


# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:#64748b; padding:15px;">
        🚚 Food Delivery Analytics Dashboard |
        Built with Python, Pandas, Matplotlib, Seaborn & Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
