# ================================================================
#  TN LOAD FORECASTING — CLEAN CONTROLLED APP
# ================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from io import StringIO
from datetime import datetime

# ================================================================
# CONFIG
# ================================================================
st.set_page_config(
    page_title="TN Load Forecasting",
    page_icon="⚡",
    layout="wide"
)

GITHUB_RAW = "https://github.com/sakthinathan5107-eng/TN-LOAD-FORECAST/edit/main/streamlit_app_rolling.py"

DATA_EXPIRY_SECONDS = 600  # 10 minutes

# ================================================================
# DATA LOADING (STRICT)
# ================================================================

@st.cache_data(ttl=60)
def fetch_file(filename):
    try:
        url = f"{GITHUB_RAW}/{filename}"
        r = requests.get(url, timeout=10)
        return r.text if r.status_code == 200 else None
    except:
        return None


def is_fresh(df):
    if 'generated_at' not in df.columns:
        return False
    try:
        t = pd.to_datetime(df['generated_at'].iloc[0])
        return (datetime.now() - t).total_seconds() <= DATA_EXPIRY_SECONDS
    except:
        return False


def load_results():
    data = fetch_file("rolling_results.csv")
    if not data:
        return None

    try:
        df = pd.read_csv(StringIO(data))

        if not is_fresh(df):
            return None

        return df
    except:
        return None


# ================================================================
# UI
# ================================================================

st.title("⚡ TN Load Forecasting Dashboard")
st.caption("Shows ONLY live Colab-generated data")

df = load_results()

# ================================================================
# NO DATA CASE
# ================================================================
if df is None:
    st.warning("⚠ No LIVE data available")
    st.info("👉 Run your Colab model to generate fresh results")
    st.stop()

st.success("✅ Live data loaded")

# ================================================================
# BASIC METRICS
# ================================================================
col1, col2, col3 = st.columns(3)

col1.metric("Total Days", len(df))
col2.metric("Avg Load", f"{df['predicted_avg'].mean():,.0f} MW")
col3.metric("Peak Load", f"{df['predicted_peak'].max():,.0f} MW")

st.divider()

# ================================================================
# TABS
# ================================================================
tab1, tab2, tab3 = st.tabs([
    "📊 Monthly",
    "📅 Daily",
    "📋 Data"
])

# ================================================================
# TAB 1 — MONTHLY
# ================================================================
with tab1:
    st.subheader("Monthly Overview")

    monthly = df.groupby('month_name').agg({
        'predicted_avg': 'mean',
        'predicted_peak': 'max'
    }).reset_index()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=monthly['month_name'],
        y=monthly['predicted_avg'],
        name="Avg Load"
    ))

    fig.add_trace(go.Scatter(
        x=monthly['month_name'],
        y=monthly['predicted_peak'],
        mode='lines+markers',
        name="Peak Load"
    ))

    st.plotly_chart(fig, use_container_width=True)

# ================================================================
# TAB 2 — DAILY
# ================================================================
with tab2:
    st.subheader("Daily Trend")

    month = st.selectbox("Select Month", df['month_name'].unique())

    df_m = df[df['month_name'] == month]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_m['day'],
        y=df_m['predicted_avg'],
        name="Avg"
    ))

    fig.add_trace(go.Scatter(
        x=df_m['day'],
        y=df_m['predicted_peak'],
        name="Peak"
    ))

    st.plotly_chart(fig, use_container_width=True)

# ================================================================
# TAB 3 — DATA TABLE
# ================================================================
with tab3:
    st.subheader("All Results")

    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False)
    st.download_button("Download CSV", csv, "results.csv")

# ================================================================
# END
# ================================================================
