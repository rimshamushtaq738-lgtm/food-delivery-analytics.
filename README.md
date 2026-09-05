# 🚚 Food Delivery Analytics & Operational Dashboard

An end-to-end **Data Analytics and Business Intelligence project** built to analyze food delivery performance, identify operational bottlenecks, and generate actionable business recommendations.

This project transforms raw food delivery data into meaningful insights using **Python, Pandas, NumPy, Matplotlib, Seaborn, and Streamlit**.

---

## 📊 Project Overview

The objective of this project is to understand the major factors affecting food delivery performance, including:

- 🚦 Road traffic density
- 📍 Delivery distance
- 🌦️ Weather conditions
- 🚗 Vehicle condition
- 🏙️ City-level performance
- ⏱️ Delivery time

The project follows an end-to-end analytics workflow:

**Raw Data → Data Cleaning → Feature Engineering → Exploratory Data Analysis → Visualization → Business Insights → Interactive Dashboard → AI Explanation**

---

## 🏆 Competition Questions & Key Findings

### 1. 🚦 Traffic Impact Analysis

**Question:** Which traffic level has the highest average delivery time?

The analysis compares average delivery time across different road traffic density levels.

**Key Business Insight:**  
Higher traffic density is associated with increased delivery times, highlighting traffic congestion as an important operational bottleneck.

**Business Recommendation:**  
Food delivery companies can consider dynamic rider allocation and route optimization during high-traffic periods.

---

### 2. 📍 Distance vs. Delivery Time

**Question:** Does delivery distance affect delivery time?

The relationship between `distance_km` and `Time_taken (min)` was analyzed using correlation analysis and a regression visualization.

**Key Finding:**  
The dataset shows a positive relationship between delivery distance and delivery time.

**Business Insight:**  
Longer delivery routes generally require more delivery time, while traffic and other operational conditions can further increase delays.

---

### 3. 🌦️ Weather + Traffic Combination

**Question:** Which combination of weather and traffic conditions produces the highest average delivery time?

The dataset was grouped by:

- Weather conditions
- Road traffic density
- Average delivery time

The combination with the highest average delivery time was identified programmatically.

**Key Business Insight:**  
Adverse operating conditions combined with high traffic can create significant delivery delays.

**Business Recommendation:**  
Delivery operations can prepare additional rider capacity and prioritize route optimization during high-risk conditions.

---

## 🧹 Data Cleaning & Preprocessing

The dataset was cleaned and prepared before analysis.

Key preprocessing steps included:

- Removed duplicate records
- Cleaned column names
- Converted relevant columns to numeric data types
- Handled missing driver age and rating values
- Handled missing order-time values
- Removed records with missing essential analytical fields
- Removed invalid/non-positive delivery times
- Created a new delivery speed feature

### Feature Engineering

A new feature was calculated:

**Delivery Speed (km/h)**

```text
Delivery Speed = Distance (km) / Delivery Time (hours)
