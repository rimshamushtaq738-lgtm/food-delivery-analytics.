import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
from google import genai

# Warnings Suppress
warnings.filterwarnings('ignore')

# Page Configuration
st.set_page_config(
    page_title="Food Delivery Analytics Challenge",
    page_icon="🚚",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stAlert { border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("🚚 Food Delivery Performance & Operational Dashboard")
st.caption("Hackathon Task A: Python Data Analysis, Insights & Gemini LLM Integration")

# Load and Clean Data
@st.cache_data
def load_and_clean_data():
    if not os.path.exists("food_delivery_dataset.csv"):
        return None, None
    
    df_raw = pd.read_csv("food_delivery_dataset.csv")
    raw_stats = {
        "rows": df_raw.shape[0],
        "cols": df_raw.shape[1],
        "missing": df_raw.isna().sum().sum(),
        "duplicates": df_raw.duplicated().sum()
    }
    
    df = df_raw.copy()
    df.columns = df.columns.str.strip()
    df = df.drop_duplicates()
    
    df['Delivery_person_Age'] = pd.to_numeric(df['Delivery_person_Age'], errors='coerce')
    df['Delivery_person_Ratings'] = pd.to_numeric(df['Delivery_person_Ratings'], errors='coerce')
    df['Time_taken (min)'] = pd.to_numeric(df['Time_taken (min)'], errors='coerce')
    df['distance_km'] = pd.to_numeric(df['distance_km'], errors='coerce')
    
    df['Delivery_person_Age'] = df['Delivery_person_Age'].fillna(df['Delivery_person_Age'].median())
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].fillna(df['Delivery_person_Ratings'].median())
    
    if 'Time_Orderd' in df.columns:
        df['Time_Orderd'] = df['Time_Orderd'].fillna(df['Time_Orderd'].mode()[0])
        
    df['delivery_speed_kmh'] = df['distance_km'] / (df['Time_taken (min)'] / 60)
    df['delivery_speed_kmh'] = df['delivery_speed_kmh'].replace([np.inf, -np.inf], np.nan).fillna(df['delivery_speed_kmh'].median())
    
    return df, raw_stats

df, raw_stats = load_and_clean_data()

if df is None:
    st.error("⚠️ 'food_delivery_dataset.csv' file nahi mili!")
    st.stop()

# Sidebar
st.sidebar.header("🔍 Global Filters")
api_key = st.sidebar.text_input("Gemini API Key (Optional)", type="password")

selected_city = st.sidebar.multiselect("Select City", options=df['City'].unique(), default=df['City'].unique())
selected_traffic = st.sidebar.multiselect("Select Traffic Density", options=df['Road_traffic_density'].unique(), default=df['Road_traffic_density'].unique())

fdf = df[(df['City'].isin(selected_city)) & (df['Road_traffic_density'].isin(selected_traffic))]

# Section A & B: Dataset Audit
with st.expander("📋 Section A & B: Dataset Loading & Cleaning Audit", expanded=False):
    c_a, c_b, c_c, c_d = st.columns(4)
    c_a.metric("Total Records", f"{raw_stats['rows']:,}")
    c_b.metric("Total Columns", raw_stats['cols'])
    c_c.metric("Missing Values Cleaned", f"{raw_stats['missing']:,}")
    c_d.metric("Duplicates Dropped", raw_stats['duplicates'])
    st.dataframe(fdf.head(5), width=None)

# Section C: Basic Statistics
st.header("📊 Section C: Operational Basic Statistics")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Deliveries", f"{len(fdf):,}")
k2.metric("Avg Delivery Time", f"{fdf['Time_taken (min)'].mean():.1f} min", f"Min: {fdf['Time_taken (min)'].min()} | Max: {fdf['Time_taken (min)'].max()}")
k3.metric("Avg Distance", f"{fdf['distance_km'].mean():.2f} km")
k4.metric("Avg Speed", f"{fdf['delivery_speed_kmh'].mean():.1f} km/h")
k5.metric("Avg Rider Rating", f"{fdf['Delivery_person_Ratings'].mean():.2f} ⭐", f"Avg Age: {fdf['Delivery_person_Age'].mean():.1f} yrs")

st.divider()

# Section D & E: Programmatic Answers & Charts
st.header("🎯 Section D & E: Competition Answers & Visualizations")

traffic_impact = fdf.groupby('Road_traffic_density')['Time_taken (min)'].mean().sort_values(ascending=False)
distance_corr = fdf['distance_km'].corr(fdf['Time_taken (min)'])
combo_impact = fdf.groupby(['Weather_conditions', 'Road_traffic_density'])['Time_taken (min)'].mean().sort_values(ascending=False)

q1_answer = traffic_impact.index[0] if len(traffic_impact) > 0 else "N/A"
q1_val = traffic_impact.iloc[0] if len(traffic_impact) > 0 else 0

q3_weather = combo_impact.index[0][0] if len(combo_impact) > 0 else "N/A"
q3_traffic = combo_impact.index[0][1] if len(combo_impact) > 0 else "N/A"
q3_val = combo_impact.iloc[0] if len(combo_impact) > 0 else 0

a1, a2, a3 = st.columns(3)
with a1:
    st.info(f"**Q1 – Traffic Impact:**\n\nHighest Avg Time: **{q1_answer}**\nAverage Latency: **{q1_val:.2f} mins**")
with a2:
    st.info(f"**Q2 – Distance Impact:**\n\nPearson Correlation: **{distance_corr:.4f}**\nIndicates positive linear relationship.")
with a3:
    st.info(f"**Q3 – Combined Conditions:**\n\nWorst Combo: **{q3_weather} + {q3_traffic}**\nAverage Latency: **{q3_val:.2f} mins**")

v_col1, v_col2 = st.columns(2)

with v_col1:
    st.markdown("### Chart 1: Average Delivery Time by Traffic Density")
    fig1, ax1 = plt.subplots(figsize=(7, 4.5))
    sns.barplot(x=traffic_impact.index, y=traffic_impact.values, hue=traffic_impact.index, palette="rocket", legend=False, ax=ax1)
    ax1.set_title("Traffic Density vs Delivery Duration", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Traffic Condition", fontsize=10)
    ax1.set_ylabel("Average Time Taken (minutes)", fontsize=10)
    for p in ax1.patches:
        ax1.annotate(f'{p.get_height():.1f}m', (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                    ha='center', va='center', color='white', fontweight='bold')
    st.pyplot(fig1)

with v_col2:
    st.markdown("### Chart 2: Delivery Distance vs. Delivery Time")
    fig2, ax2 = plt.subplots(figsize=(7, 4.5))
    sns.regplot(data=fdf.sample(min(2000, len(fdf))), x='distance_km', y='Time_taken (min)',
                scatter_kws={'alpha':0.2, 'color':'teal'}, line_kws={'color':'red'}, ax=ax2)
    ax2.set_title(f"Distance vs Duration (Correlation: {distance_corr:.4f})", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Delivery Distance (km)", fontsize=10)
    ax2.set_ylabel("Time Taken (minutes)", fontsize=10)
    st.pyplot(fig2)

st.divider()

# Section F: Business Insights
st.header("💡 Section F: Strategic Business Insights")
b1, b2, b3 = st.columns(3)

with b1:
    st.success("""
    **1. Traffic Bottleneck Management**
    - **Finding:** Traffic density (Jam) causes the largest delivery delays.
    - **Business Impact:** Implement dynamic ETA padding and assign riders on 2-wheelers during peak hours.
    """)

with b2:
    st.success(f"""
    **2. Distance Sensitivity & Dynamic Radius**
    - **Finding:** Correlation of **{distance_corr:.2f}** proves long distance increases duration.
    - **Business Impact:** Introduce delivery surcharges or cap order radius during peak rush hours.
    """)

with b3:
    st.success("""
    **3. Weather Contingency Planning**
    - **Finding:** Bad weather combined with heavy traffic yields maximum delivery delays.
    - **Business Impact:** Offer rider surge incentives and update consumer app promise times during rain.
    """)

st.divider()

# Section G: AI Explanation
st.header("🤖 Section G: AI-Powered Executive Summary (Gemini LLM)")

if not api_key and "GEMINI_API_KEY" in os.environ:
    api_key = os.environ["GEMINI_API_KEY"]

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
        Summarize these food delivery analytics results for management:
        - Total Deliveries: {len(fdf)}
        - Q1 Traffic Impact: Worst traffic is '{q1_answer}' ({q1_val:.2f} mins avg).
        - Q2 Distance Impact: Correlation between distance and time is {distance_corr:.4f}.
        - Q3 Combined Impact: Worst combination is '{q3_weather}' weather and '{q3_traffic}' traffic ({q3_val:.2f} mins avg).
        - Avg Speed: {fdf['delivery_speed_kmh'].mean():.1f} km/h.

        Provide 3 clear actionable bullet points for management.
        """
        with st.spinner("Connecting to Gemini LLM Engine..."):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            st.info("🤖 **Gemini AI Generated Explanation:**")
            st.markdown(response.text)
    except Exception as e:
        st.warning(f"Could not connect to Gemini API: {e}")
else:
    st.info(f"""
    **Executive Summary (Automated Rules Engine):**
    - **Primary Bottleneck:** Traffic condition **'{q1_answer}'** creates maximum delay (**{q1_val:.2f} mins** avg).
    - **Distance Scaling:** Distance correlates positively with delivery duration (**r = {distance_corr:.4f}**).
    - **Peak Friction Window:** **'{q3_weather}'** weather + **'{q3_traffic}'** traffic leads to maximum latency (**{q3_val:.2f} mins**).
    """)s