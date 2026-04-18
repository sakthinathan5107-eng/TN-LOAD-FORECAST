# ================================================================
# TN LOAD FORECASTING — STREAMLIT WEB APP (ROLLING FORECAST)
#
# FEATURES:
# Tab 1: Rolling Forecast — 6-month rolling line chart
# Tab 2: Monthly Forecast — April, May, June, July, Aug, Sep breakdown
# Tab 3: 5-Year Comparison — 2020-2026 bar chart by year
# Tab 4: All Results — Complete data table with download
#
# Data source: GitHub (auto-refresh every 60 seconds)
# ================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests
import calendar
from datetime import datetime
from io import StringIO

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="TN Load Forecasting",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ GITHUB CONFIG ============
GITHUB_USER = "sakthinathan5107-eng"
GITHUB_REPO = "TN-LOAD-FORECAST"
GITHUB_RAW = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/results"

# ============ COLORS & STYLES ============
MONTH_COLORS = {
    4: "#2563eb",   # Blue - April
    5: "#16a34a",   # Green - May
    6: "#ea580c",   # Orange - June
    7: "#dc2626",   # Red - July
    8: "#9333ea",   # Purple - August
    9: "#0891b2",   # Cyan - September
}

MONTH_FILL = {
    4: "rgba(37,99,235,0.10)",
    5: "rgba(22,163,74,0.10)",
    6: "rgba(234,88,12,0.10)",
    7: "rgba(220,38,38,0.10)",
    8: "rgba(147,51,234,0.10)",
    9: "rgba(8,145,178,0.10)",
}

MONTH_NAMES = {
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
}

YEAR_COLORS = {
    2020: "#94a3b8",
    2021: "#64748b",
    2022: "#f59e0b",
    2023: "#8b5cf6",
    2024: "#ec4899",
    2025: "#6366f1",
    2026: "#dc2626",
}

# Plotly layout template
PLOT_LAYOUT = dict(
    template="plotly_white",
    font=dict(family="Arial, sans-serif", size=12, color="#1f2937"),
    xaxis=dict(showgrid=True, gridwidth=1, gridcolor="#e5e7eb"),
    yaxis=dict(showgrid=True, gridwidth=1, gridcolor="#e5e7eb"),
    hovermode="x unified",
    margin=dict(l=60, r=30, t=80, b=60),
)

# ============ EMBEDDED HISTORICAL DATA (2020-2025) ============
# Real historical data from TANGEDCO for comparison

HIST_MONTHLY = {
    (2020,4):{'avg':9860.2,'peak':11281.1},(2020,5):{'avg':11884.4,'peak':14378.4},(2020,6):{'avg':12377.4,'peak':14320.5},
    (2021,4):{'avg':14544.4,'peak':16913.8},(2021,5):{'avg':12517.8,'peak':15893.9},(2021,6):{'avg':12821.3,'peak':16058.2},
    (2022,4):{'avg':14751.5,'peak':17509.6},(2022,5):{'avg':13897.7,'peak':16796.5},(2022,6):{'avg':14428.5,'peak':16743.9},
    (2023,4):{'avg':15993.5,'peak':19436.0},(2023,5):{'avg':14922.9,'peak':18469.3},(2023,6):{'avg':15494.2,'peak':18308.4},
    (2024,4):{'avg':16580.4,'peak':19576.5},(2024,5):{'avg':16108.9,'peak':20393.0},(2024,6):{'avg':15040.3,'peak':18133.0},
    (2025,4):{'avg':16692.8,'peak':19975.8},(2025,5):{'avg':15673.0,'peak':19477.0},(2025,6):{'avg':16305.3,'peak':19780.2},
}

# ============ CACHE FUNCTIONS ============
@st.cache_data(ttl=60)
def fetch_from_github(filename):
    """Fetch CSV from GitHub with 60-second cache"""
    try:
        url = f"{GITHUB_RAW}/{filename}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except Exception as e:
        st.warning(f"⚠️ Error fetching {filename}: {str(e)}")
        return None

@st.cache_data(ttl=60)
def load_rolling_results():
    """Load rolling forecast results from GitHub"""
    csv_text = fetch_from_github("rolling_forecast_complete.csv")
    if csv_text:
        try:
            return pd.read_csv(StringIO(csv_text))
        except:
            return None
    return None

@st.cache_data(ttl=60)
def load_monthly_results(month_num):
    """Load monthly results from GitHub"""
    month_name = MONTH_NAMES[month_num].lower()
    csv_text = fetch_from_github(f"{month_name}_2026_forecast.csv")
    if csv_text:
        try:
            return pd.read_csv(StringIO(csv_text))
        except:
            return None
    return None

def safe_float(value):
    """Safely convert to float"""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    try:
        return float(value)
    except:
        return None

# ============ HEADER ============
def show_header():
    """Display page header"""
    st.markdown("""
    <div style='text-align:center; padding: 20px 0;'>
        <h1>⚡ Tamil Nadu Load Forecasting</h1>
        <p style='font-size:16px; color:#666;'>Rolling 3-Month Forecast with Actual Data Comparison</p>
        <p style='font-size:13px; color:#999;'>LSTM Model | 22 Features | 96-97% Accurate</p>
        <hr style='margin: 20px 0;'>
    </div>
    """, unsafe_allow_html=True)

# ============ TAB 1: ROLLING FORECAST ============
def tab_rolling_forecast():
    """6-month rolling forecast visualization"""
    st.subheader("📊 Rolling Forecast — April to September 2026")
    st.caption("Daily average load predictions with 6-month overview")
    
    df_results = load_rolling_results()
    
    if df_results is None or len(df_results) == 0:
        st.info("⏳ Data loading... Auto-refreshes every 60 seconds")
        return
    
    # Convert data types
    df_results['month'] = pd.to_numeric(df_results['month'], errors='coerce')
    df_results['day'] = pd.to_numeric(df_results['day'], errors='coerce')
    df_results['predicted_avg'] = pd.to_numeric(df_results['predicted_avg'], errors='coerce')
    df_results['predicted_peak'] = pd.to_numeric(df_results['predicted_peak'], errors='coerce')
    
    # Create rolling forecast chart
    fig_rolling = go.Figure()
    
    for month_num in [4, 5, 6, 7, 8, 9]:
        df_month = df_results[df_results['month'] == month_num].sort_values('day')
        if len(df_month) > 0:
            fig_rolling.add_trace(go.Scatter(
                x=df_month['day'].tolist(),
                y=df_month['predicted_avg'].tolist(),
                name=MONTH_NAMES[month_num],
                line=dict(color=MONTH_COLORS[month_num], width=3),
                fill='tozeroy',
                fillcolor=MONTH_FILL[month_num],
                marker=dict(size=6),
                mode='lines+markers'
            ))
    
    fig_rolling.update_layout(
        title='Rolling Forecast: Daily Average Load (All 6 Months)',
        xaxis_title='Day of Month',
        yaxis_title='Load (MW)',
        height=500,
        **PLOT_LAYOUT
    )
    st.plotly_chart(fig_rolling, use_container_width=True)
    
    # Monthly statistics
    st.subheader("📈 Monthly Summary")
    cols = st.columns(6)
    
    for idx, month_num in enumerate([4, 5, 6, 7, 8, 9]):
        df_m = df_results[df_results['month'] == month_num]
        if len(df_m) > 0:
            with cols[idx]:
                st.metric(
                    MONTH_NAMES[month_num],
                    f"{df_m['predicted_avg'].mean():.0f} MW",
                    f"Peak: {df_m['predicted_peak'].max():.0f} MW"
                )

# ============ TAB 2: MONTHLY FORECAST ============
def tab_monthly_forecast():
    """Monthly breakdown with detailed view"""
    st.subheader("🏷️ Monthly Forecast Breakdown")
    st.caption("Select a month to see detailed daily and hourly breakdown")
    
    # Month selector
    selected_month = st.selectbox(
        "Select Month:",
        ["April", "May", "June", "July", "August", "September"],
        key="month_selector"
    )
    
    month_num = [k for k, v in MONTH_NAMES.items() if v == selected_month][0]
    df_month = load_monthly_results(month_num)
    
    if df_month is None or len(df_month) == 0:
        st.info(f"⏳ {selected_month} 2026 data loading...")
        return
    
    # Day slider
    max_days = len(df_month) // 24  # Each day has 24 hours
    selected_day = st.slider(f"Select day in {selected_month}:", 1, max_days, 1)
    
    # Get day data
    df_day = df_month.iloc[(selected_day-1)*24:selected_day*24]
    
    if len(df_day) > 0:
        # Convert load to numeric
        df_day['load'] = pd.to_numeric(df_day['load'], errors='coerce')
        
        # Hourly chart
        hours = list(range(24))
        loads = df_day['load'].values
        
        fig_hourly = go.Figure()
        fig_hourly.add_trace(go.Bar(
            x=hours,
            y=loads,
            marker=dict(
                color=loads,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Load (MW)")
            ),
            text=[f"{v:.0f}" for v in loads],
            textposition='outside',
            name='Hourly Load'
        ))
        
        fig_hourly.update_layout(
            title=f"{selected_month} {selected_day}, 2026 — Hourly Load Forecast",
            xaxis_title='Hour (00:00 - 23:00)',
            yaxis_title='Load (MW)',
            height=450,
            showlegend=False,
            **PLOT_LAYOUT
        )
        st.plotly_chart(fig_hourly, use_container_width=True)
        
        # Daily metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Daily Average", f"{loads.mean():.0f} MW")
        with col2:
            st.metric("Daily Peak", f"{loads.max():.0f} MW")
        with col3:
            st.metric("Daily Min", f"{loads.min():.0f} MW")
        with col4:
            st.metric("Daily Range", f"{loads.max() - loads.min():.0f} MW")

# ============ TAB 3: 5-YEAR COMPARISON ============
def tab_5year_comparison():
    """5-year historical comparison with 2026 forecast"""
    st.subheader("📊 5-Year Comparison — 2020 to 2026")
    st.caption("Compare historical data (2020-2025) with 2026 forecast")
    
    # Month selector for comparison
    selected_month = st.selectbox(
        "Select Month for Comparison:",
        ["April", "May", "June"],
        key="comparison_month"
    )
    
    month_num = [k for k, v in MONTH_NAMES.items() if v == selected_month][0]
    
    # Load 2026 data for comparison
    df_2026 = load_monthly_results(month_num)
    
    # Create comparison chart - Bar chart with all years
    years = list(range(2020, 2027))
    averages = []
    peaks = []
    colors = []
    
    for year in years:
        if year < 2026:
            # Historical data
            data = HIST_MONTHLY.get((year, month_num))
            if data:
                averages.append(data['avg'])
                peaks.append(data['peak'])
                colors.append(YEAR_COLORS[year])
        else:
            # 2026 forecast
            if df_2026 is not None and len(df_2026) > 0:
                df_2026['predicted_avg'] = pd.to_numeric(df_2026['predicted_avg'], errors='coerce')
                df_2026['predicted_peak'] = pd.to_numeric(df_2026['predicted_peak'], errors='coerce')
                averages.append(df_2026['predicted_avg'].mean())
                peaks.append(df_2026['predicted_peak'].max())
                colors.append(YEAR_COLORS[year])
            else:
                averages.append(None)
                peaks.append(None)
                colors.append('#e5e7eb')
    
    # Create figure
    fig_comparison = go.Figure()
    
    # Add average bars
    fig_comparison.add_trace(go.Bar(
        x=[str(y) for y in years],
        y=averages,
        name='Daily Average',
        marker=dict(color=colors),
        text=[f"{v:,.0f}" if v else "—" for v in averages],
        textposition='outside',
        opacity=0.85
    ))
    
    # Add peak line
    fig_comparison.add_trace(go.Scatter(
        x=[str(y) for y in years],
        y=peaks,
        name='Monthly Peak',
        mode='lines+markers',
        line=dict(color='#dc2626', width=3, dash='dot'),
        marker=dict(size=10, symbol='diamond'),
        yaxis='y2'
    ))
    
    # Update layout with secondary y-axis
    fig_comparison.update_layout(
    title=f'{selected_month} — Load Comparison (2020-2026)',
    xaxis_title='Year',
    yaxis_title='Daily Average Load (MW)',
    yaxis2=dict(
        title='Peak Load (MW)',
        overlaying='y',
        side='right'
    ),
    height=500,
    **PLOT_LAYOUT
)
    
    st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Detailed comparison table
    st.subheader("📋 Year-over-Year Comparison")
    
    comparison_data = []
    for year in years:
        if year < 2026:
            data = HIST_MONTHLY.get((year, month_num))
            if data:
                comparison_data.append({
                    'Year': year,
                    'Avg Load (MW)': f"{data['avg']:,.0f}",
                    'Peak Load (MW)': f"{data['peak']:,.0f}",
                    'Type': 'Historical',
                })
        else:
            if df_2026 is not None and len(df_2026) > 0:
                df_2026['predicted_avg'] = pd.to_numeric(df_2026['predicted_avg'], errors='coerce')
                df_2026['predicted_peak'] = pd.to_numeric(df_2026['predicted_peak'], errors='coerce')
                comparison_data.append({
                    'Year': year,
                    'Avg Load (MW)': f"{df_2026['predicted_avg'].mean():,.0f}",
                    'Peak Load (MW)': f"{df_2026['predicted_peak'].max():,.0f}",
                    'Type': 'Forecast',
                })
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)

# ============ TAB 4: ALL RESULTS ============
def tab_all_results():
    """Complete results table with download option"""
    st.subheader("📋 All Results — Complete Forecast Data")
    st.caption("All 91 days of forecast data (April-September 2026)")
    
    df_results = load_rolling_results()
    
    if df_results is None or len(df_results) == 0:
        st.info("⏳ Data loading... Auto-refreshes every 60 seconds")
        return
    
    # Select columns to display
    display_columns = ['date', 'month_name', 'day', 'forecast_type', 
                      'predicted_avg', 'predicted_peak', 'predicted_min', 'actual_avg']
    
    available_columns = [col for col in display_columns if col in df_results.columns]
    
    # Convert to numeric
    for col in ['predicted_avg', 'predicted_peak', 'predicted_min', 'actual_avg']:
        if col in df_results.columns:
            df_results[col] = pd.to_numeric(df_results[col], errors='coerce')
    
    # Display table
    df_display = df_results[available_columns].copy()
    df_display.columns = [col.replace('_', ' ').title() for col in df_display.columns]
    
    st.dataframe(df_display, use_container_width=True, height=500)
    
    # Download options
    st.subheader("📥 Download Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Download complete CSV
        csv = df_results.to_csv(index=False)
        st.download_button(
            label="⬇️ Download All Results (CSV)",
            data=csv.encode(),
            file_name="TN_Rolling_Forecast_Complete.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Download by month
        month_select = st.selectbox("Select month to download:", ["All Months", "April", "May", "June", "July", "August", "September"])
        
        if month_select != "All Months":
            month_num = [k for k, v in MONTH_NAMES.items() if v == month_select][0]
            df_month = df_results[df_results['month'] == month_num]
            csv_month = df_month.to_csv(index=False)
            st.download_button(
                label=f"⬇️ Download {month_select} 2026",
                data=csv_month.encode(),
                file_name=f"TN_{month_select}_2026_Forecast.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col3:
        # Summary statistics
        st.metric("Total Days", len(df_results))
        st.metric("Date Range", f"Apr 1 - Sep 30, 2026")
    
    # Additional statistics
    st.subheader("📊 Summary Statistics")
    
    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    
    with stats_col1:
        st.metric(
            "Overall Avg Load",
            f"{df_results['predicted_avg'].mean():.0f} MW"
        )
    
    with stats_col2:
        st.metric(
            "Maximum Load",
            f"{df_results['predicted_peak'].max():.0f} MW"
        )
    
    with stats_col3:
        st.metric(
            "Minimum Load",
            f"{df_results['predicted_min'].min():.0f} MW"
        )
    
    with stats_col4:
        if df_results['actual_avg'].notna().sum() > 0:
            st.metric(
                "Days with Actual",
                f"{int(df_results['actual_avg'].notna().sum())} days"
            )

# ============ MAIN APP ============
def main():
    """Main app logic"""
    show_header()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Rolling Forecast",
        "🏷️ Monthly Forecast",
        "📈 5-Year Comparison",
        "📋 All Results"
    ])
    
    with tab1:
        tab_rolling_forecast()
    
    with tab2:
        tab_monthly_forecast()
    
    with tab3:
        tab_5year_comparison()
    
    with tab4:
        tab_all_results()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; padding: 20px 0; color: #666; font-size: 12px;'>
        <p>TN Load Forecasting Dashboard | LSTM Model | Data updates every 60 seconds from GitHub</p>
        <p>Accuracy: 3.1-4.2% MAPE | 96-97% Accurate</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
