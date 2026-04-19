# ================================================================
#  TN INTELLIGENT LOAD FORECASTING — Streamlit Dashboard
#  Reads CSVs pushed to GitHub by the Colab training script.
#  Colab code is NOT touched — zero interference.
#
#  Deploy: streamlit run streamlit_app.py
#  Secrets: set GITHUB_TOKEN in .streamlit/secrets.toml
#           or as an environment variable (optional for public repos)
# ================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import calendar
import requests
from datetime import date, datetime

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="TN Load Forecast",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GitHub raw URL base ───────────────────────────────────────
GITHUB_USER   = "sakthinathan5107-eng"
GITHUB_REPO   = "TN-LOAD-FORECAST"
GITHUB_BRANCH = "main"
RAW_BASE      = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"

# ── Month metadata ────────────────────────────────────────────
MONTH_NAMES = {
    1:'January', 2:'February', 3:'March',    4:'April',
    5:'May',     6:'June',     7:'July',      8:'August',
    9:'September',10:'October',11:'November',12:'December',
}
MONTH_COLORS = {
    1:'#6366f1', 2:'#8b5cf6', 3:'#a855f7',
    4:'#2563eb', 5:'#16a34a', 6:'#ea580c',
    7:'#dc2626', 8:'#d97706', 9:'#0891b2',
    10:'#7c3aed',11:'#db2777',12:'#059669',
}
HISTORY_YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
YEAR_COLORS   = {
    2020:'#94a3b8', 2021:'#64748b', 2022:'#f59e0b',
    2023:'#8b5cf6', 2024:'#06b6d4', 2025:'#ec4899',
    2026:'#ef4444',
}

# ── Embedded historical monthly averages (always works) ───────
HIST_MONTHLY = {
    'April' : {2020:9860,  2021:14544, 2022:14752, 2023:15994, 2024:16580, 2025:16693},
    'May'   : {2020:11884, 2021:12518, 2022:13898, 2023:14923, 2024:16109, 2025:15673},
    'June'  : {2020:12377, 2021:12821, 2022:14429, 2023:15494, 2024:15040, 2025:16305},
    'July'  : {2020:13100, 2021:13400, 2022:14600, 2023:15200, 2024:15500, 2025:15900},
    'August': {2020:12800, 2021:13200, 2022:14300, 2023:15000, 2024:15300, 2025:15700},
    'September':{2020:12500,2021:12900,2022:14100, 2023:14800, 2024:15100, 2025:15400},
}

# ─────────────────────────────────────────────────────────────
#  DATA LOADING — cached, fetched from GitHub raw URLs
# ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load_csv_from_github(path: str) -> pd.DataFrame | None:
    """Fetch a CSV from the GitHub repo. Returns None on failure."""
    url = f"{RAW_BASE}/{path}"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            from io import StringIO
            return pd.read_csv(StringIO(r.text))
        return None
    except Exception:
        return None


@st.cache_data(ttl=300, show_spinner=False)
def load_rolling_results() -> pd.DataFrame | None:
    df = load_csv_from_github("results/rolling_results.csv")
    if df is not None and 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    return df


@st.cache_data(ttl=300, show_spinner=False)
def load_raw_history() -> pd.DataFrame | None:
    df = load_csv_from_github("results/raw_history_export.csv")
    if df is not None and 'Datetime' in df.columns:
        df['Datetime'] = pd.to_datetime(df['Datetime'])
    return df


def detect_forecast_months(df: pd.DataFrame):
    """Return list of (year, month) tuples present in rolling_results."""
    if df is None:
        return []
    return sorted(set(zip(df['year'].astype(int), df['month'].astype(int))))


# ─────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/6/6d/TANGEDCO_logo.png/120px-TANGEDCO_logo.png",
             width=80, use_container_width=False)
    st.title("⚡ TN Load Forecast")
    st.caption("Tamil Nadu Power Grid · LSTM Day-Ahead Prediction")
    st.divider()

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.markdown("**Data Source**")
    st.markdown(f"[GitHub Repo ↗](https://github.com/{GITHUB_USER}/{GITHUB_REPO})")
    st.markdown(f"[Streamlit App ↗](https://{GITHUB_USER}-{GITHUB_REPO}.streamlit.app)")
    st.caption("Data auto-refreshes every 5 min")

# ─────────────────────────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────────────────────────

with st.spinner("Loading forecast data from GitHub ..."):
    df_results = load_rolling_results()
    df_raw     = load_raw_history()

forecast_months = detect_forecast_months(df_results)
data_ok = df_results is not None and len(forecast_months) > 0

# ─────────────────────────────────────────────────────────────
#  HEADER METRICS
# ─────────────────────────────────────────────────────────────

st.markdown("## ⚡ Tamil Nadu Intelligent Load Forecasting")
if data_ok:
    quarter_label = " · ".join(
        f"{MONTH_NAMES[mo]} {yr}" for yr, mo in forecast_months
    )
    st.caption(f"Forecast window: **{quarter_label}**  |  LSTM · 168-hr lookback · 22 features · Rolling retrain")
else:
    st.caption("Waiting for Colab to push results to GitHub ...")

st.divider()

# ─────────────────────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────────────────────

tab_overview, tab_monthly, tab_daily, tab_history, tab_accuracy, tab_table = st.tabs([
    "📊 Overview",
    "📅 Monthly Forecast",
    "🕐 Daily Hourly",
    "📈 5-Year History",
    "🎯 Accuracy",
    "📋 All Results",
])


# ════════════════════════════════════════════════════════════
#  TAB 1 — OVERVIEW (3-month combined)
# ════════════════════════════════════════════════════════════

with tab_overview:
    if not data_ok:
        st.info("⏳ No forecast data yet. Run the Colab notebook and push results to GitHub.")
    else:
        # ── Summary KPI cards ──────────────────────────────
        cols = st.columns(len(forecast_months))
        for (yr, mo), col in zip(forecast_months, cols):
            mn   = MONTH_NAMES[mo]
            mask = (df_results['year'] == yr) & (df_results['month'] == mo)
            sub  = df_results[mask]
            avg_mw  = sub['predicted_avg'].mean()
            peak_mw = sub['predicted_peak'].max()
            days    = len(sub)
            col.metric(f"**{mn} {yr}**", f"{avg_mw:,.0f} MW avg",
                       f"Peak {peak_mw:,.0f} MW · {days} days")

        st.divider()

        # ── 3-month combined line chart ────────────────────
        fig = make_subplots(rows=2, cols=1,
                            subplot_titles=["Daily Average Load (MW)",
                                            "Daily Peak Load (MW)"],
                            vertical_spacing=0.12,
                            row_heights=[0.6, 0.4])

        x_offset = 0
        shapes   = []
        for yr, mo in forecast_months:
            mn   = MONTH_NAMES[mo]
            col  = MONTH_COLORS[mo]
            mask = (df_results['year'] == yr) & (df_results['month'] == mo)
            sub  = df_results[mask].sort_values('day')
            x    = [x_offset + d for d in sub['day'].tolist()]
            avgs = sub['predicted_avg'].tolist()
            pkss = sub['predicted_peak'].tolist()

            fig.add_trace(go.Scatter(
                x=x, y=avgs, name=f"{mn} {yr}",
                line=dict(color=col, width=2.5),
                mode='lines+markers', marker=dict(size=4),
                fill='tozeroy', fillcolor=hex_to_rgba(col, 0.08),
                legendgroup=f"{yr}{mo}",
            ), row=1, col=1)

            fig.add_trace(go.Bar(
                x=x, y=pkss, name=f"{mn} {yr} Peak",
                marker_color=col, opacity=0.75,
                showlegend=False, legendgroup=f"{yr}{mo}",
            ), row=2, col=1)

            if x_offset > 0:
                shapes.append(dict(
                    type='line', xref='x', yref='paper',
                    x0=x_offset+0.5, x1=x_offset+0.5, y0=0, y1=1,
                    line=dict(color='gray', width=1, dash='dash')))

            x_offset += calendar.monthrange(yr, mo)[1]

        fig.update_layout(height=600, shapes=shapes,
                          title_text="Tamil Nadu Power Grid — Rolling 3-Month Forecast",
                          hovermode='x unified', legend=dict(orientation='h', y=-0.12))
        fig.update_yaxes(tickformat=',.0f', row=1, col=1)
        fig.update_yaxes(tickformat=',.0f', row=2, col=1)
        st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════
#  TAB 2 — MONTHLY FORECAST (per-month detail)
# ════════════════════════════════════════════════════════════

with tab_monthly:
    if not data_ok:
        st.info("⏳ No forecast data yet.")
    else:
        month_labels = [f"{MONTH_NAMES[mo]} {yr}" for yr, mo in forecast_months]
        sel_label    = st.selectbox("Select month", month_labels)
        sel_idx      = month_labels.index(sel_label)
        sel_yr, sel_mo = forecast_months[sel_idx]
        sel_mn  = MONTH_NAMES[sel_mo]
        sel_col = MONTH_COLORS[sel_mo]

        mask    = (df_results['year'] == sel_yr) & (df_results['month'] == sel_mo)
        sub     = df_results[mask].sort_values('day')
        days    = sub['day'].tolist()
        avgs    = sub['predicted_avg'].tolist()
        peaks   = sub['predicted_peak'].tolist()
        roll7   = pd.Series(avgs).rolling(7, min_periods=1).mean().tolist()

        mins = []
        for _, row in sub.iterrows():
            vals = [float(row.get(f'pred_h{h:02d}', np.nan) or np.nan)
                    for h in range(24)]
            vals = [v for v in vals if not np.isnan(v)]
            mins.append(min(vals) if vals else np.nan)

        # KPI row
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Avg Load",  f"{np.mean(avgs):,.0f} MW")
        c2.metric("Peak Load", f"{max(peaks):,.0f} MW")
        c3.metric("Min Load",  f"{min(mins):,.0f} MW")
        n_wkd = len(avgs) - sum(1 for d in days
                                if date(sel_yr, sel_mo, d).weekday() >= 5)
        c4.metric("Weekdays / Weekend", f"{n_wkd} / {len(avgs)-n_wkd}")

        st.divider()

        # Daily avg/peak/min + 7-day rolling
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=days, y=peaks, name='Peak Load',
                                  line=dict(color=sel_col, width=1.5, dash='dot'),
                                  mode='lines+markers', marker=dict(size=4, symbol='triangle-up')))
        fig2.add_trace(go.Scatter(x=days, y=avgs, name='Avg Load',
                                  line=dict(color=sel_col, width=2.5),
                                  mode='lines+markers', marker=dict(size=5),
                                  fill='tonexty',
                                  fillcolor=f"rgba({int(sel_col[1:3],16)},{int(sel_col[3:5],16)},{int(sel_col[5:],16)},0.08)"))
        fig2.add_trace(go.Scatter(x=days, y=mins, name='Min Load',
                                  line=dict(color=sel_col, width=1.5, dash='dot'),
                                  mode='lines+markers', marker=dict(size=4, symbol='triangle-down')))
        fig2.add_trace(go.Scatter(x=days, y=roll7, name='7-Day Rolling Avg',
                                  line=dict(color='#dc2626', width=2, dash='dash')))
        fig2.update_layout(
            title=f"{sel_mn} {sel_yr} — Daily Load Forecast",
            xaxis_title=f"Day of {sel_mn}", yaxis_title="Load (MW)",
            yaxis_tickformat=',.0f', hovermode='x unified', height=400,
            legend=dict(orientation='h', y=-0.2))
        st.plotly_chart(fig2, use_container_width=True)

        # Average hourly profile
        hourly_avgs = []
        for h in range(24):
            vals = [float(row.get(f'pred_h{h:02d}', np.nan) or np.nan)
                    for _, row in sub.iterrows()]
            vals = [v for v in vals if not np.isnan(v)]
            hourly_avgs.append(np.mean(vals) if vals else 0)

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=list(range(24)), y=hourly_avgs,
            name=f"{sel_mn} {sel_yr} Avg Profile",
            line=dict(color=sel_col, width=2.5),
            mode='lines+markers', marker=dict(size=5),
            fill='tozeroy',
            fillcolor=f"rgba({int(sel_col[1:3],16)},{int(sel_col[3:5],16)},{int(sel_col[5:],16)},0.12)"))
        fig3.update_layout(
            title=f"Average Hourly Load Profile — {sel_mn} {sel_yr}",
            xaxis_title="Hour of Day", yaxis_title="Avg Load (MW)",
            xaxis=dict(tickmode='array', tickvals=list(range(24)),
                       ticktext=[f"{h:02d}:00" for h in range(24)]),
            yaxis_tickformat=',.0f', height=350,
            legend=dict(orientation='h', y=-0.25))
        st.plotly_chart(fig3, use_container_width=True)

        # Weekday vs Weekend
        wday, wend = [], []
        for i, d in enumerate(days):
            if date(sel_yr, sel_mo, d).weekday() >= 5:
                wend.append(avgs[i])
            else:
                wday.append(avgs[i])
        fig4 = go.Figure(go.Bar(
            x=['Weekday', 'Weekend'],
            y=[np.mean(wday) if wday else 0, np.mean(wend) if wend else 0],
            marker_color=[sel_col, '#94a3b8'],
            text=[f"{np.mean(wday):,.0f} MW" if wday else "N/A",
                  f"{np.mean(wend):,.0f} MW" if wend else "N/A"],
            textposition='outside', opacity=0.85, width=0.4))
        fig4.update_layout(
            title=f"Weekday vs Weekend Avg Load — {sel_mn} {sel_yr}",
            yaxis_title="Avg Load (MW)", yaxis_tickformat=',.0f', height=300)
        st.plotly_chart(fig4, use_container_width=True)

        # Vs previous year (from raw history if available)
        if df_raw is not None:
            prev_yr  = sel_yr - 1
            mask_prev = ((df_raw['Datetime'].dt.year  == prev_yr) &
                         (df_raw['Datetime'].dt.month == sel_mo))
            sub_prev  = df_raw[mask_prev]
            if len(sub_prev) > 0:
                prev_daily = (sub_prev.groupby(sub_prev['Datetime'].dt.day)['load']
                              .mean().sort_index())
                n      = min(len(avgs), len(prev_daily))
                growth = ((np.mean(avgs[:n]) - prev_daily.values[:n].mean()) /
                           prev_daily.values[:n].mean() * 100)
                st.divider()
                fig5 = go.Figure()
                fig5.add_trace(go.Scatter(
                    x=days, y=avgs, name=f"{sel_mn} {sel_yr} (Forecast)",
                    line=dict(color=sel_col, width=2.5), mode='lines+markers',
                    marker=dict(size=5)))
                fig5.add_trace(go.Scatter(
                    x=prev_daily.index.tolist(), y=prev_daily.values.tolist(),
                    name=f"{sel_mn} {prev_yr} (Actual)",
                    line=dict(color='#94a3b8', width=2, dash='dash'),
                    mode='lines+markers', marker=dict(size=4, symbol='square')))
                fig5.update_layout(
                    title=f"{sel_mn} {sel_yr} vs {sel_mn} {prev_yr}  |  YoY Growth: {growth:+.1f}%",
                    xaxis_title=f"Day of {sel_mn}", yaxis_title="Daily Avg Load (MW)",
                    yaxis_tickformat=',.0f', height=380,
                    legend=dict(orientation='h', y=-0.2), hovermode='x unified')
                st.plotly_chart(fig5, use_container_width=True)


# ════════════════════════════════════════════════════════════
#  TAB 3 — DAILY HOURLY (day-by-day slider)
# ════════════════════════════════════════════════════════════

with tab_daily:
    if not data_ok:
        st.info("⏳ No forecast data yet.")
    else:
        month_labels_d = [f"{MONTH_NAMES[mo]} {yr}" for yr, mo in forecast_months]
        sel_label_d    = st.selectbox("Select month ", month_labels_d, key="daily_month")
        sel_idx_d      = month_labels_d.index(sel_label_d)
        sel_yr_d, sel_mo_d = forecast_months[sel_idx_d]
        sel_mn_d  = MONTH_NAMES[sel_mo_d]
        sel_col_d = MONTH_COLORS[sel_mo_d]

        mask_d = (df_results['year'] == sel_yr_d) & (df_results['month'] == sel_mo_d)
        sub_d  = df_results[mask_d].sort_values('day').reset_index(drop=True)
        num_days_d = len(sub_d)

        day_sel = st.slider(f"Select day of {sel_mn_d}", 1, num_days_d, 1)
        row     = sub_d[sub_d['day'] == day_sel].iloc[0]
        pred    = [float(row.get(f'pred_h{h:02d}', 0) or 0) for h in range(24)]
        actual  = [row.get(f'actual_h{h:02d}') for h in range(24)]
        has_act = any(v is not None and not (isinstance(v, float) and np.isnan(v))
                      for v in actual)

        dt_str  = row['date']
        c1, c2, c3 = st.columns(3)
        c1.metric("Date",      dt_str)
        c2.metric("Avg Pred",  f"{np.mean(pred):,.0f} MW")
        c3.metric("Peak Pred", f"{max(pred):,.0f} MW @ {pred.index(max(pred)):02d}:00")

        fig_d = go.Figure()
        fig_d.add_trace(go.Bar(
            x=[f"{h:02d}:00" for h in range(24)], y=pred,
            name=f"{sel_mn_d} {day_sel}, {sel_yr_d} — Forecast",
            marker_color=sel_col_d, opacity=0.85))
        if has_act:
            fig_d.add_trace(go.Scatter(
                x=[f"{h:02d}:00" for h in range(24)],
                y=[float(v) if v is not None else None for v in actual],
                name="Actual", line=dict(color='#1e293b', width=2.5),
                mode='lines+markers', marker=dict(size=6, symbol='circle-open')))
        fig_d.update_layout(
            title=f"Hourly Load Forecast — {sel_mn_d} {day_sel}, {sel_yr_d}",
            xaxis_title="Hour of Day", yaxis_title="Load (MW)",
            yaxis_tickformat=',.0f', height=400,
            legend=dict(orientation='h', y=-0.2), hovermode='x unified')
        st.plotly_chart(fig_d, use_container_width=True)

        # Previous year same day comparison (from raw history)
        if df_raw is not None:
            prev_date = date(sel_yr_d - 1, sel_mo_d, day_sel)
            prev_mask = df_raw['Datetime'].dt.date == prev_date
            prev_day  = df_raw[prev_mask].sort_values('Datetime')
            if len(prev_day) == 24:
                fig_d.add_trace(go.Scatter(
                    x=[f"{h:02d}:00" for h in range(24)],
                    y=prev_day['load'].tolist(),
                    name=f"{sel_mn_d} {day_sel}, {sel_yr_d-1} Actual",
                    line=dict(color='#94a3b8', width=1.8, dash='dash'),
                    mode='lines+markers', marker=dict(size=4, symbol='square')))
                fig_d.update_traces()
                st.plotly_chart(fig_d, use_container_width=True, key="daily_with_prev")


# ════════════════════════════════════════════════════════════
#  TAB 4 — 5-YEAR HISTORY COMPARISON (always works)
# ════════════════════════════════════════════════════════════

with tab_history:
    st.subheader("Historical Monthly Averages (2020–2025) vs 2026 Forecast")

    hist_months_available = [MONTH_NAMES[mo] for _, mo in forecast_months
                             if MONTH_NAMES[mo] in HIST_MONTHLY]
    if not hist_months_available:
        hist_months_available = list(HIST_MONTHLY.keys())

    sel_hist_mn = st.selectbox("Month", hist_months_available, key="hist_month")

    # Build bar chart: historical years + 2026 forecast
    hist_data   = HIST_MONTHLY.get(sel_hist_mn, {})
    bar_years   = sorted(hist_data.keys())
    bar_vals    = [hist_data[y] for y in bar_years]
    bar_colors  = [YEAR_COLORS.get(y, '#64748b') for y in bar_years]

    # Add 2026 forecast if available
    fore_avg_2026 = None
    if data_ok:
        for yr, mo in forecast_months:
            if MONTH_NAMES[mo] == sel_hist_mn:
                mask_h = (df_results['year'] == yr) & (df_results['month'] == mo)
                sub_h  = df_results[mask_h]
                if len(sub_h) > 0:
                    fore_avg_2026 = sub_h['predicted_avg'].mean()
                    bar_years.append(2026)
                    bar_vals.append(fore_avg_2026)
                    bar_colors.append(YEAR_COLORS[2026])

    fig_h1 = go.Figure(go.Bar(
        x=[str(y) for y in bar_years], y=bar_vals,
        marker_color=bar_colors, opacity=0.85,
        text=[f"{v:,.0f}" for v in bar_vals], textposition='outside'))
    fig_h1.update_layout(
        title=f"{sel_hist_mn} — Monthly Avg Load by Year (2020–2026)",
        xaxis_title="Year", yaxis_title="Avg Load (MW)",
        yaxis_tickformat=',.0f', height=380)
    st.plotly_chart(fig_h1, use_container_width=True)

    # Line chart: daily trend per year from raw history
    if df_raw is not None:
        mo_num = {v: k for k, v in MONTH_NAMES.items()}.get(sel_hist_mn)
        if mo_num:
            fig_h2 = go.Figure()
            for yr in HISTORY_YEARS:
                mask_y = ((df_raw['Datetime'].dt.year  == yr) &
                          (df_raw['Datetime'].dt.month == mo_num))
                sub_y  = df_raw[mask_y].copy()
                if len(sub_y) == 0:
                    continue
                daily_y = sub_y.groupby(sub_y['Datetime'].dt.day)['load'].mean()
                is_last = (yr == max(HISTORY_YEARS))
                fig_h2.add_trace(go.Scatter(
                    x=daily_y.index.tolist(), y=daily_y.values.tolist(),
                    name=f"{yr} Actual",
                    line=dict(color=YEAR_COLORS.get(yr, '#64748b'),
                              width=2.2 if is_last else 1.2,
                              dash='solid' if is_last else 'dash'),
                    mode='lines+markers' if is_last else 'lines',
                    marker=dict(size=4) if is_last else dict(size=0)))

            if data_ok and fore_avg_2026 is not None:
                for yr, mo in forecast_months:
                    if MONTH_NAMES[mo] == sel_hist_mn:
                        mask_f2 = (df_results['year'] == yr) & (df_results['month'] == mo)
                        sub_f2  = df_results[mask_f2].sort_values('day')
                        fig_h2.add_trace(go.Scatter(
                            x=sub_f2['day'].tolist(),
                            y=sub_f2['predicted_avg'].tolist(),
                            name=f"2026 Forecast",
                            line=dict(color=YEAR_COLORS[2026], width=3),
                            mode='lines+markers', marker=dict(size=5, symbol='diamond')))

            fig_h2.update_layout(
                title=f"{sel_hist_mn} — Daily Avg Load Trend: 2020–2026",
                xaxis_title=f"Day of {sel_hist_mn}", yaxis_title="Avg Load (MW)",
                yaxis_tickformat=',.0f', height=420,
                hovermode='x unified', legend=dict(orientation='h', y=-0.2))
            st.plotly_chart(fig_h2, use_container_width=True)
    else:
        st.info("Raw history CSV not yet available from GitHub — bar chart above uses embedded historical data.")


# ════════════════════════════════════════════════════════════
#  TAB 5 — ACCURACY (MAPE / RMSE)
# ════════════════════════════════════════════════════════════

with tab_accuracy:
    if not data_ok:
        st.info("⏳ No forecast data yet.")
    else:
        has_accuracy = (
            'mape' in df_results.columns and
            df_results['mape'].notna().any()
        )

        if not has_accuracy:
            st.info("ℹ️ MAPE/RMSE will appear here once actual load data is uploaded and compared against predictions. Run the Colab notebook after uploading actuals.")
        else:
            df_acc = df_results[df_results['mape'].notna()].copy()

            # Overall metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Overall MAPE", f"{df_acc['mape'].mean():.2f}%")
            c2.metric("Overall RMSE", f"{df_acc['rmse'].mean():,.0f} MW")
            c3.metric("Days Evaluated", f"{len(df_acc)}")

            # MAPE trend
            fig_a = go.Figure()
            for yr, mo in forecast_months:
                mn_a  = MONTH_NAMES[mo]
                col_a = MONTH_COLORS[mo]
                mask_a = (df_acc['year'] == yr) & (df_acc['month'] == mo)
                sub_a  = df_acc[mask_a].sort_values('day')
                if len(sub_a) == 0:
                    continue
                fig_a.add_trace(go.Scatter(
                    x=sub_a['date'].tolist(), y=sub_a['mape'].tolist(),
                    name=f"{mn_a} {yr}", line=dict(color=col_a, width=2),
                    mode='lines+markers', marker=dict(size=5)))
            fig_a.add_hline(y=5, line_dash='dash', line_color='#dc2626',
                            annotation_text="5% target")
            fig_a.update_layout(
                title="Daily MAPE — Forecast vs Actual",
                xaxis_title="Date", yaxis_title="MAPE (%)",
                height=380, hovermode='x unified')
            st.plotly_chart(fig_a, use_container_width=True)

            # RMSE trend
            fig_b = go.Figure()
            for yr, mo in forecast_months:
                mn_b  = MONTH_NAMES[mo]
                col_b = MONTH_COLORS[mo]
                mask_b = (df_acc['year'] == yr) & (df_acc['month'] == mo)
                sub_b  = df_acc[mask_b].sort_values('day')
                if len(sub_b) == 0:
                    continue
                fig_b.add_trace(go.Bar(
                    x=sub_b['date'].tolist(), y=sub_b['rmse'].tolist(),
                    name=f"{mn_b} {yr}", marker_color=col_b, opacity=0.8))
            fig_b.update_layout(
                title="Daily RMSE — Forecast vs Actual",
                xaxis_title="Date", yaxis_title="RMSE (MW)",
                yaxis_tickformat=',.0f', height=350,
                barmode='group')
            st.plotly_chart(fig_b, use_container_width=True)

            # Per-month accuracy table
            st.subheader("Per-Month Accuracy Summary")
            rows = []
            for yr, mo in forecast_months:
                mn_t  = MONTH_NAMES[mo]
                mask_t = (df_acc['year'] == yr) & (df_acc['month'] == mo)
                sub_t  = df_acc[mask_t]
                if len(sub_t) == 0:
                    continue
                rows.append({
                    'Month'          : f"{mn_t} {yr}",
                    'Days Evaluated' : len(sub_t),
                    'Avg MAPE (%)'   : f"{sub_t['mape'].mean():.2f}",
                    'Best MAPE (%)'  : f"{sub_t['mape'].min():.2f}",
                    'Worst MAPE (%)' : f"{sub_t['mape'].max():.2f}",
                    'Avg RMSE (MW)'  : f"{sub_t['rmse'].mean():,.0f}",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════
#  TAB 6 — ALL RESULTS TABLE + DOWNLOAD
# ════════════════════════════════════════════════════════════

with tab_table:
    if not data_ok:
        st.info("⏳ No forecast data yet.")
    else:
        # Display columns only (hide hourly pred_h / actual_h cols for readability)
        display_cols = [c for c in df_results.columns
                        if not c.startswith('pred_h') and not c.startswith('actual_h')]
        df_display = df_results[display_cols].copy()

        # Filters
        col_f1, col_f2 = st.columns(2)
        month_opts = ["All"] + [f"{MONTH_NAMES[mo]} {yr}" for yr, mo in forecast_months]
        sel_filter = col_f1.selectbox("Filter by month", month_opts, key="filter_month")
        if sel_filter != "All":
            fi = month_opts.index(sel_filter) - 1
            fyr, fmo = forecast_months[fi]
            df_display = df_display[
                (df_display['year'] == fyr) & (df_display['month'] == fmo)]

        st.dataframe(
            df_display.style.format({
                'predicted_avg' : '{:,.1f}',
                'predicted_peak': '{:,.1f}',
                'actual_avg'    : lambda v: f'{v:,.1f}' if pd.notna(v) else '—',
                'actual_peak'   : lambda v: f'{v:,.1f}' if pd.notna(v) else '—',
                'mape'          : lambda v: f'{v:.2f}%' if pd.notna(v) else '—',
                'rmse'          : lambda v: f'{v:,.0f}' if pd.notna(v) else '—',
            }),
            use_container_width=True, height=500, hide_index=True)

        st.divider()

        # Download buttons
        col_d1, col_d2, col_d3 = st.columns(3)
        col_d1.download_button(
            "⬇ Download All Results (CSV)",
            data=df_results.to_csv(index=False).encode(),
            file_name="TN_rolling_forecast_all.csv",
            mime="text/csv", use_container_width=True)

        for i, (yr, mo) in enumerate(forecast_months):
            mn_dl = MONTH_NAMES[mo]
            mask_dl = (df_results['year'] == yr) & (df_results['month'] == mo)
            df_dl   = df_results[mask_dl]
            btn_col = [col_d1, col_d2, col_d3][i % 3]
            btn_col.download_button(
                f"⬇ {mn_dl} {yr} Results",
                data=df_dl.to_csv(index=False).encode(),
                file_name=f"{mn_dl.lower()}_{yr}_results.csv",
                mime="text/csv", use_container_width=True,
                key=f"dl_{yr}_{mo}")

# ── Footer ────────────────────────────────────────────────────
st.divider()
st.caption(
    "⚡ Tamil Nadu Intelligent Load Forecasting · LSTM Neural Network · "
    "Final Year EEE Project · Data: TANGEDCO 2020–2026 · "
    f"Last refresh: {datetime.now().strftime('%d %b %Y %H:%M')}"
)
