# ================================================================
# TN LOAD FORECASTING — STREAMLIT WEB APP (ROLLING FORECAST)
#
# GATE LOGIC:
#   → If rolling_forecast_complete.csv NOT found on GitHub:
#       Show "Run Colab first" instructions page. No graphs, no data.
#   → If CSV found on GitHub:
#       Show full dashboard with all 4 tabs.
# ================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
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
GITHUB_USER   = "sakthinathan5107-eng"
GITHUB_REPO   = "TN-LOAD-FORECAST"
GITHUB_BRANCH = "main"
GITHUB_RAW    = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/results"

# ============ COLORS ============
MONTH_COLORS = {4:"#2563eb", 5:"#16a34a", 6:"#ea580c", 7:"#dc2626", 8:"#9333ea", 9:"#0891b2"}
MONTH_FILL   = {4:"rgba(37,99,235,0.10)", 5:"rgba(22,163,74,0.10)", 6:"rgba(234,88,12,0.10)",
                7:"rgba(220,38,38,0.10)", 8:"rgba(147,51,234,0.10)", 9:"rgba(8,145,178,0.10)"}
MONTH_NAMES  = {4:"April", 5:"May", 6:"June", 7:"July", 8:"August", 9:"September"}
YEAR_COLORS  = {2020:"#94a3b8",2021:"#64748b",2022:"#f59e0b",2023:"#8b5cf6",
                2024:"#ec4899",2025:"#6366f1",2026:"#dc2626"}

# ============ HISTORICAL DATA (2020-2025) ============
HIST_MONTHLY = {
    (2020,4):{'avg':9860.2,'peak':11281.1},(2020,5):{'avg':11884.4,'peak':14378.4},(2020,6):{'avg':12377.4,'peak':14320.5},
    (2021,4):{'avg':14544.4,'peak':16913.8},(2021,5):{'avg':12517.8,'peak':15893.9},(2021,6):{'avg':12821.3,'peak':16058.2},
    (2022,4):{'avg':14751.5,'peak':17509.6},(2022,5):{'avg':13897.7,'peak':16796.5},(2022,6):{'avg':14428.5,'peak':16743.9},
    (2023,4):{'avg':15993.5,'peak':19436.0},(2023,5):{'avg':14922.9,'peak':18469.3},(2023,6):{'avg':15494.2,'peak':18308.4},
    (2024,4):{'avg':16580.4,'peak':19576.5},(2024,5):{'avg':16108.9,'peak':20393.0},(2024,6):{'avg':15040.3,'peak':18133.0},
    (2025,4):{'avg':16692.8,'peak':19975.8},(2025,5):{'avg':15673.0,'peak':19477.0},(2025,6):{'avg':16305.3,'peak':19780.2},
}

# ============ DATA FETCH ============
@st.cache_data(ttl=60)
def fetch_csv(filename):
    """Fetch a CSV from GitHub. Returns (DataFrame or None, error_msg or None)."""
    url = f"{GITHUB_RAW}/{filename}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return pd.read_csv(StringIO(resp.text)), None
        else:
            return None, f"HTTP {resp.status_code} — URL tried: `{url}`"
    except Exception as e:
        return None, str(e)

def check_data_ready():
    """Returns (is_ready, df_rolling or None, error_msg or None)."""
    df, err = fetch_csv("rolling_forecast_complete.csv")
    if df is not None and len(df) > 0:
        return True, df, None
    return False, None, err

# ============ NOT-READY PAGE ============
def show_not_ready_page(error_msg):
    st.markdown("""
    <div style='text-align:center; padding:30px 0 10px 0;'>
        <h1>⚡ Tamil Nadu Load Forecasting</h1>
        <p style='font-size:16px; color:#888;'>LSTM Model | 22 Features | 96-97% Accurate</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # Warning banner
    st.markdown("""
    <div style='background:#fef9c3; border:2px solid #f59e0b; border-radius:12px;
                padding:28px 32px; margin:10px 0 28px 0; text-align:center;'>
        <h2 style='color:#b45309; margin:0 0 10px 0;'>⚠️ No Forecast Data Found</h2>
        <p style='font-size:17px; color:#78350f; margin:0;'>
            The dashboard is waiting for you to <strong>run the Colab notebook first</strong>.<br>
            Once you run Colab and push the CSV files to GitHub, all charts and results
            will appear here automatically.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("### 📋 How to Activate the Dashboard")
        st.markdown("""
**Step 1 — Open Google Colab**
Open your notebook:
`TN_ROLLING_FORECAST_COMPLETE.ipynb`

---

**Step 2 — Run All Cells (Cell 1 → Cell 19)**
The notebook will:
- Install libraries & import data
- Train the LSTM model on 2020–2026 data
- Generate daily forecasts for April–September 2026
- Save all results as CSV files

---

**Step 3 — Download the ZIP at Cell 19**
Uncomment and run:
```python
files.download('TN_Rolling_Forecast_Results.zip')
```

---

**Step 4 — Push CSV Files to GitHub**
Extract the ZIP and upload all CSVs into the `results/` folder of your repo:
```
TN-LOAD-FORECAST/
└── results/
    ├── rolling_forecast_complete.csv  ← unlocks dashboard
    ├── april_2026_forecast.csv
    ├── may_2026_forecast.csv
    ├── june_2026_forecast.csv
    ├── july_2026_forecast.csv
    ├── august_2026_forecast.csv
    └── september_2026_forecast.csv
```

---

**Step 5 — Refresh This Page**
Click **🔄 Refresh** in the sidebar, or wait 60 seconds.
The full dashboard will unlock automatically!
        """)

    with col_right:
        st.markdown("### 📁 CSV File Status")

        files_to_check = [
            ("rolling_forecast_complete.csv", "Master file — unlocks dashboard", True),
            ("april_2026_forecast.csv",       "April 2026 hourly data",          False),
            ("may_2026_forecast.csv",          "May 2026 hourly data",            False),
            ("june_2026_forecast.csv",         "June 2026 hourly data",           False),
            ("july_2026_forecast.csv",         "July 2026 hourly data",           False),
            ("august_2026_forecast.csv",       "August 2026 hourly data",         False),
            ("september_2026_forecast.csv",    "September 2026 hourly data",      False),
        ]

        for fname, desc, required in files_to_check:
            df_check, _ = fetch_csv(fname)
            if df_check is not None:
                icon   = "✅"
                color  = "#16a34a"
                status = f"Found ({len(df_check)} rows)"
                bg     = "#f0fdf4"
            else:
                icon   = "❌" if required else "⬜"
                color  = "#dc2626" if required else "#6b7280"
                status = "Not found yet"
                bg     = "#fff1f2" if required else "#f9fafb"

            st.markdown(f"""
            <div style='border:1px solid #e5e7eb; border-radius:8px; padding:10px 14px;
                        margin-bottom:8px; background:{bg};'>
                <span style='font-size:18px;'>{icon}</span>
                <strong style='color:{color};'> {fname}</strong><br>
                <span style='font-size:12px; color:#666;'>{desc} — <em>{status}</em></span>
            </div>
            """, unsafe_allow_html=True)

        if error_msg:
            st.markdown("---")
            st.markdown("### 🔍 Debug Info")
            st.error(f"{error_msg}")
            st.markdown(f"**Expected URL:**\n```\n{GITHUB_RAW}/rolling_forecast_complete.csv\n```")

        st.markdown("---")
        st.markdown("### ⚙️ Current GitHub Settings")
        st.code(
            f"User:   {GITHUB_USER}\n"
            f"Repo:   {GITHUB_REPO}\n"
            f"Branch: {GITHUB_BRANCH}\n"
            f"Folder: results/",
            language="text"
        )

# ============ SIDEBAR ============
def show_sidebar():
    with st.sidebar:
        st.markdown("### ⚡ TN Load Forecasting")
        st.markdown(f"**Repo:** `{GITHUB_USER}/{GITHUB_REPO}`")
        st.markdown(f"**Branch:** `{GITHUB_BRANCH}`  |  **Folder:** `results/`")
        st.caption("Data auto-refreshes every 60 seconds")
        if st.button("🔄 Clear Cache & Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.markdown("---")
        st.caption(f"Checked at: {datetime.now().strftime('%H:%M:%S')}")

# ============ HEADER ============
def show_header():
    st.markdown("""
    <div style='text-align:center; padding:20px 0 0 0;'>
        <h1>⚡ Tamil Nadu Load Forecasting</h1>
        <p style='font-size:16px; color:#666;'>Rolling 3-Month Forecast | LSTM Model | 96-97% Accurate</p>
        <hr style='margin:16px 0;'>
    </div>
    """, unsafe_allow_html=True)

# ============ TAB 1: ROLLING FORECAST ============
def tab_rolling_forecast(df_results):
    st.subheader("📊 Rolling Forecast — April to September 2026")
    st.caption("Daily average load predictions for all 6 months")

    df = df_results.copy()
    for col in ['month','day','predicted_avg','predicted_peak']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    fig = go.Figure()
    for m in [4,5,6,7,8,9]:
        dm = df[df['month']==m].sort_values('day')
        if len(dm) > 0:
            fig.add_trace(go.Scatter(
                x=dm['day'].tolist(), y=dm['predicted_avg'].tolist(),
                name=MONTH_NAMES[m],
                line=dict(color=MONTH_COLORS[m], width=3),
                fill='tozeroy', fillcolor=MONTH_FILL[m],
                marker=dict(size=6), mode='lines+markers'
            ))
    fig.update_layout(
        title='Rolling Forecast: Daily Average Load (April–September 2026)',
        xaxis_title='Day of Month', yaxis_title='Load (MW)',
        height=500, template='plotly_white',
        font=dict(family='Arial', size=12),
        hovermode='x unified',
        margin=dict(l=60, r=30, t=80, b=60)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Monthly Summary")
    cols = st.columns(6)
    for idx, m in enumerate([4,5,6,7,8,9]):
        dm = df[df['month']==m]
        if len(dm) > 0:
            with cols[idx]:
                st.metric(MONTH_NAMES[m],
                          f"{dm['predicted_avg'].mean():.0f} MW",
                          f"Peak: {dm['predicted_peak'].max():.0f} MW")

# ============ TAB 2: MONTHLY FORECAST ============
def tab_monthly_forecast():
    st.subheader("🏷️ Monthly Forecast Breakdown")
    st.caption("Hourly load breakdown per day")

    selected_month = st.selectbox("Select Month:",
        ["April","May","June","July","August","September"], key="month_selector")
    month_num = [k for k,v in MONTH_NAMES.items() if v==selected_month][0]

    df_month, err = fetch_csv(f"{selected_month.lower()}_2026_forecast.csv")
    if df_month is None or len(df_month) == 0:
        st.warning(f"⚠️ `{selected_month.lower()}_2026_forecast.csv` not found.\n\n{err or ''}")
        return

    # Detect load column
    load_col = None
    for candidate in ['load','predicted_load','Load','load_mw','value']:
        if candidate in df_month.columns:
            load_col = candidate
            break
    if load_col is None:
        st.error(f"❌ No load column found. Columns: {list(df_month.columns)}")
        return

    df_month[load_col] = pd.to_numeric(df_month[load_col], errors='coerce')
    max_days = max(1, len(df_month) // 24)
    selected_day = st.slider(f"Select day in {selected_month}:", 1, max_days, 1)
    df_day = df_month.iloc[(selected_day-1)*24 : selected_day*24].copy()

    if len(df_day) > 0:
        loads = df_day[load_col].values
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(range(len(loads))), y=loads,
            marker=dict(color=loads, colorscale='Viridis', showscale=True,
                        colorbar=dict(title="Load (MW)")),
            text=[f"{v:.0f}" if not np.isnan(v) else "" for v in loads],
            textposition='outside'
        ))
        fig.update_layout(
            title=f"{selected_month} {selected_day}, 2026 — Hourly Load Forecast",
            xaxis_title='Hour', yaxis_title='Load (MW)',
            height=450, showlegend=False, template='plotly_white',
            margin=dict(l=60,r=30,t=80,b=60)
        )
        st.plotly_chart(fig, use_container_width=True)

        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Daily Average", f"{np.nanmean(loads):.0f} MW")
        with c2: st.metric("Daily Peak",    f"{np.nanmax(loads):.0f} MW")
        with c3: st.metric("Daily Min",     f"{np.nanmin(loads):.0f} MW")
        with c4: st.metric("Daily Range",   f"{np.nanmax(loads)-np.nanmin(loads):.0f} MW")

# ============ TAB 3: 5-YEAR COMPARISON ============
def tab_5year_comparison():
    st.subheader("📊 5-Year Comparison — 2020 to 2026")
    st.caption("Historical (2020-2025) vs 2026 forecast")

    selected_month = st.selectbox("Select Month:",
        ["April","May","June","July","August","September"], key="comparison_month")
    month_num = [k for k,v in MONTH_NAMES.items() if v==selected_month][0]

    df_2026, _ = fetch_csv(f"{selected_month.lower()}_2026_forecast.csv")

    years = list(range(2020, 2027))
    averages, peaks, colors = [], [], []

    for year in years:
        if year < 2026:
            data = HIST_MONTHLY.get((year, month_num))
            if data:
                averages.append(data['avg']); peaks.append(data['peak']); colors.append(YEAR_COLORS[year])
            else:
                averages.append(None); peaks.append(None); colors.append('#e5e7eb')
        else:
            if df_2026 is not None and len(df_2026) > 0:
                avg_col  = 'predicted_avg'  if 'predicted_avg'  in df_2026.columns else (
                           'load'           if 'load'           in df_2026.columns else None)
                peak_col = 'predicted_peak' if 'predicted_peak' in df_2026.columns else avg_col
                if avg_col:
                    df_2026[avg_col]  = pd.to_numeric(df_2026[avg_col],  errors='coerce')
                    df_2026[peak_col] = pd.to_numeric(df_2026[peak_col], errors='coerce')
                    averages.append(df_2026[avg_col].mean())
                    peaks.append(df_2026[peak_col].max())
                else:
                    averages.append(None); peaks.append(None)
                colors.append(YEAR_COLORS[year])
            else:
                averages.append(None); peaks.append(None); colors.append('#e5e7eb')

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[str(y) for y in years], y=averages, name='Daily Average',
        marker=dict(color=colors),
        text=[f"{v:,.0f}" if v else "—" for v in averages],
        textposition='outside', opacity=0.85
    ))
    fig.add_trace(go.Scatter(
        x=[str(y) for y in years], y=peaks, name='Monthly Peak',
        mode='lines+markers',
        line=dict(color='#dc2626', width=3, dash='dot'),
        marker=dict(size=10, symbol='diamond'), yaxis='y2'
    ))
    # ✅ All layout params written explicitly — no **PLOT_LAYOUT unpacking (avoids TypeError)
    fig.update_layout(
        title=f'{selected_month} — Load Comparison (2020-2026)',
        xaxis_title='Year',
        yaxis_title='Daily Average Load (MW)',
        yaxis2=dict(title='Peak Load (MW)', overlaying='y', side='right', showgrid=False),
        height=500,
        hovermode='x unified',
        template='plotly_white',
        font=dict(family='Arial', size=12, color='#1f2937'),
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#e5e7eb'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#e5e7eb'),
        margin=dict(l=60, r=60, t=80, b=60),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Year-over-Year Comparison Table")
    rows = []
    for i, year in enumerate(years):
        if averages[i] is not None:
            rows.append({
                'Year': year,
                'Avg Load (MW)': f"{averages[i]:,.0f}",
                'Peak Load (MW)': f"{peaks[i]:,.0f}" if peaks[i] else "—",
                'Type': 'Historical' if year < 2026 else 'Forecast'
            })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ============ TAB 4: ALL RESULTS ============
def tab_all_results(df_results):
    st.subheader("📋 All Results — Complete Forecast Data")
    st.caption("All 91 days of forecast data (April–September 2026)")

    df = df_results.copy()
    for col in ['predicted_avg','predicted_peak','predicted_min','actual_avg']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    display_cols = [c for c in ['date','month_name','day','forecast_type',
                                'predicted_avg','predicted_peak','predicted_min','actual_avg']
                    if c in df.columns]
    df_show = df[display_cols].copy()
    df_show.columns = [c.replace('_',' ').title() for c in df_show.columns]
    st.dataframe(df_show, use_container_width=True, height=500)

    st.subheader("📥 Download")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("⬇️ Download All (CSV)",
                           df.to_csv(index=False).encode(),
                           "TN_Rolling_Forecast_Complete.csv", "text/csv",
                           use_container_width=True)
    with c2:
        ms = st.selectbox("Month to download:",
            ["All Months","April","May","June","July","August","September"])
        if ms != "All Months":
            mn = [k for k,v in MONTH_NAMES.items() if v==ms][0]
            st.download_button(f"⬇️ Download {ms}",
                               df[df['month']==mn].to_csv(index=False).encode(),
                               f"TN_{ms}_2026_Forecast.csv", "text/csv",
                               use_container_width=True)
    with c3:
        st.metric("Total Days", len(df))
        st.metric("Date Range", "Apr 1 – Sep 30, 2026")

    st.subheader("📊 Summary Statistics")
    s1,s2,s3,s4 = st.columns(4)
    with s1: st.metric("Overall Avg", f"{df['predicted_avg'].mean():.0f} MW")
    with s2: st.metric("Max Peak",    f"{df['predicted_peak'].max():.0f} MW")
    with s3:
        if 'predicted_min' in df.columns:
            st.metric("Min Load", f"{df['predicted_min'].min():.0f} MW")
    with s4:
        if 'actual_avg' in df.columns and df['actual_avg'].notna().sum() > 0:
            st.metric("Days with Actual", f"{int(df['actual_avg'].notna().sum())} days")

# ============ MAIN ============
def main():
    show_sidebar()

    # ── DATA GATE ──────────────────────────────────────────────────────────────
    # IMPORTANT: App checks GitHub for rolling_forecast_complete.csv FIRST.
    # If NOT found → show "Run Colab first" page with NO graphs or data.
    # If FOUND → show full dashboard with all 4 tabs.
    # ──────────────────────────────────────────────────────────────────────────
    data_ready, df_rolling, error_msg = check_data_ready()

    if not data_ready:
        show_not_ready_page(error_msg)
        return  # ← STOP HERE. Nothing else renders.

    # ── DATA IS READY: show full dashboard ────────────────────────────────────
    show_header()
    st.success(
        f"✅ Data loaded successfully — {len(df_rolling)} days of forecast ready!  "
        f"Last refreshed: {datetime.now().strftime('%H:%M:%S')}"
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Rolling Forecast",
        "🏷️ Monthly Forecast",
        "📈 5-Year Comparison",
        "📋 All Results"
    ])
    with tab1: tab_rolling_forecast(df_rolling)
    with tab2: tab_monthly_forecast()
    with tab3: tab_5year_comparison()
    with tab4: tab_all_results(df_rolling)

    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; color:#999; font-size:12px; padding:10px 0;'>
        TN Load Forecasting Dashboard | LSTM Model | Data refreshes every 60 seconds from GitHub
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
