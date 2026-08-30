# 🚚 Food Delivery Analytics & Operational Dashboard

An end-to-end analytics application built to analyze food delivery performance, evaluate logistics bottlenecks, and generate executive business recommendations.

---

## 📊 Executive Summary & Key Findings

### 1. Traffic Impact Analysis (Q1 Answer)
- High traffic density causes maximum delays in delivery times.
- **Key Insight:** Peak traffic hours significantly increase turnaround times, requiring dynamic fleet re-allocation.

### 2. Distance vs. Time Correlation (Q2 Answer)
- **Pearson Correlation Coefficient:** Shows a positive correlation between delivery distance (`distance_km`) and total delivery time (`Time_taken (min)`).
- **Key Insight:** Distance is a primary driver of delay, but route congestion adds non-linear delay overhead.

### 3. Environmental & Traffic Combination (Q3 Answer)
- The worst delivery conditions occur when adverse weather conditions combine with high road traffic density, resulting in maximum average delivery duration.

---

## 🛠️ Tech Stack & Setup

### Requirements
- Python 3.9+
- Streamlit
- Pandas & NumPy
- Matplotlib & Seaborn

### How to Run Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt