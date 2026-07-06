"""
NIFTY 50 Stock Market Analytics Dashboard
------------------------------------------
A professional analytics dashboard for NIFTY 50 stocks featuring:
- Market overview with index trend, gainers/losers, and breadth
- Per-stock deep dive with EMA/VWAP overlays and RSI
- Cross-stock correlation heatmap
- Sector-wise performance comparison
- Rolling volatility analysis

Author: Sahej
Tech stack: Python, Streamlit, yfinance, Plotly, Pandas
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from config import NIFTY50_STOCKS, NIFTY_INDEX_TICKER, MARKET_ASSETS, DEFAULT_PERIOD, THEME
from data_utils import (
    fetch_history,
    fetch_multiple,
    fetch_market_assets,
    compute_ema,
    compute_vwap,
    compute_rsi,
    compute_macd,
    compute_bollinger_bands,
    compute_atr,
    compute_fibonacci_levels,
    compute_rolling_volatility,
    compute_period_return,
    compute_daily_change,
    build_returns_matrix,
    build_market_summary,
)

# ----------------------------------------------------------------------------
# Page configuration
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="NIFTY 50 Analytics Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# Global styling
# ----------------------------------------------------------------------------
st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
        .stApp {{ background-color: {THEME["background"]}; color: {THEME["text"]}; }}
        .main {{ background-color: {THEME["background"]}; }}
        .block-container {{ padding-top: 1.5rem; max-width: 1400px; }}

        section[data-testid="stSidebar"] {{
            background-color: {THEME["card_bg"]};
            border-right: 1px solid {THEME["border"]};
        }}
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stSlider label {{
            color: {THEME["text"]} !important; font-weight: 600; font-size: 13px;
        }}

        [data-testid="stMetric"] {{
            background: linear-gradient(155deg, {THEME["card_bg"]} 0%, #0F172A 100%);
            border-radius: 14px; padding: 16px 18px;
            border: 1px solid {THEME["border"]};
            transition: border-color 0.2s ease, transform 0.15s ease;
        }}
        [data-testid="stMetric"]:hover {{ border-color: {THEME["primary"]}; transform: translateY(-2px); }}
        [data-testid="stMetricLabel"] {{ color: {THEME["neutral"]} !important; font-size: 12.5px !important; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }}
        [data-testid="stMetricValue"] {{ color: {THEME["text"]} !important; font-weight: 700 !important; font-family: 'JetBrains Mono', monospace; }}
        [data-testid="stMetricDelta"] {{ font-weight: 600 !important; }}

        h1, h2, h3, h4 {{ font-family: 'Inter', sans-serif; color: {THEME["text"]}; font-weight: 700; }}
        h3 {{ border-left: 3px solid {THEME["primary"]}; padding-left: 10px; margin-top: 4px; }}
        p, span, label, .stMarkdown, .stCaption {{ color: {THEME["text"]}; }}

        .stTabs [data-baseweb="tab-list"] {{ gap: 8px; border-bottom: 1px solid {THEME["border"]}; }}
        .stTabs [data-baseweb="tab"] {{
            font-size: 14.5px; font-weight: 600; color: {THEME["neutral"]};
            padding: 10px 18px; border-radius: 8px 8px 0 0;
        }}
        .stTabs [aria-selected="true"] {{
            color: {THEME["primary"]} !important;
            background-color: rgba(59,130,246,0.08);
            border-bottom: 2px solid {THEME["primary"]};
        }}

        .stDataFrame {{ border: 1px solid {THEME["border"]}; border-radius: 10px; overflow: hidden; }}
        [data-testid="stExpander"] {{ border: 1px solid {THEME["border"]}; border-radius: 10px; background-color: {THEME["card_bg"]}; }}

        footer {{visibility: hidden;}}
        #MainMenu {{visibility: hidden;}}

        /* Hero header */
        .hero-banner {{
            background: linear-gradient(120deg, #0F172A 0%, #111E3A 55%, #0B1120 100%);
            border: 1px solid {THEME["border"]};
            border-radius: 18px; padding: 28px 32px; margin-bottom: 22px;
            display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;
        }}
        .hero-title {{
            font-size: 34px; font-weight: 800; color: {THEME["text"]}; letter-spacing: 0.01em;
            background: linear-gradient(90deg, #FFFFFF 0%, #93C5FD 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin: 0; text-transform: uppercase;
        }}
        .hero-sub {{ color: {THEME["neutral"]}; font-size: 13.5px; margin-top: 6px; }}
        .hero-badge {{
            background-color: rgba(34,197,94,0.12); color: {THEME["positive"]};
            border: 1px solid rgba(34,197,94,0.3); border-radius: 20px;
            padding: 6px 14px; font-size: 12px; font-weight: 700; letter-spacing: 0.03em;
        }}
        .hero-badge-dot {{
            height: 8px; width: 8px; background-color: {THEME["positive"]}; border-radius: 50%;
            display: inline-block; margin-right: 6px; animation: pulse 1.6s infinite;
        }}
        @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.35; }} 100% {{ opacity: 1; }} }}

        /* Multi-asset cards */
        .asset-card {{
            background-color: {THEME["card_bg"]}; border: 1px solid {THEME["border"]};
            border-radius: 14px; padding: 16px 10px; text-align: center;
            transition: border-color 0.2s ease, transform 0.15s ease;
        }}
        .asset-card:hover {{ border-color: {THEME["primary"]}; transform: translateY(-2px); }}
        .asset-label {{ color: {THEME["neutral"]}; font-size: 11.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; }}
        .asset-value {{ color: {THEME["text"]}; font-size: 19px; font-weight: 700; margin-top: 6px; font-family: 'JetBrains Mono', monospace; }}
        .asset-change-pos {{ color: {THEME["positive"]}; font-size: 12.5px; font-weight: 700; margin-top: 2px; }}
        .asset-change-neg {{ color: {THEME["negative"]}; font-size: 12.5px; font-weight: 700; margin-top: 2px; }}

        /* Big KPI strip (Power-BI style) */
        .kpi-card {{
            background-color: {THEME["card_bg"]};
            border-top: 4px solid var(--accent, {THEME["primary"]});
            border-radius: 10px; padding: 16px 18px 14px 18px;
            transition: transform 0.15s ease;
        }}
        .kpi-card:hover {{ transform: translateY(-3px); }}
        .kpi-label {{
            color: var(--accent, {THEME["primary"]}); font-size: 13px; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 6px;
        }}
        .kpi-value {{
            color: #FFFFFF; font-size: 36px; font-weight: 800; line-height: 1.1;
            font-family: 'JetBrains Mono', monospace;
        }}
        .kpi-subrow {{ display: flex; justify-content: space-between; margin-top: 10px; }}
        .kpi-sub {{ text-align: left; }}
        .kpi-sub-label {{ color: {THEME["accent"]}; font-size: 11px; font-weight: 700; text-transform: uppercase; }}
        .kpi-sub-value {{ color: {THEME["text"]}; font-size: 14px; font-weight: 700; }}

        /* Donut panel (Good Loan / Bad Loan style) */
        .donut-panel {{
            background-color: {THEME["card_bg"]}; border-radius: 14px; padding: 18px 20px;
            border: 1px solid {THEME["border"]};
        }}
        .donut-panel-title {{
            color: {THEME["text"]}; font-size: 15px; font-weight: 800; letter-spacing: 0.03em;
            margin-bottom: 6px; text-transform: uppercase;
        }}
        .donut-stat-label {{ color: {THEME["accent2"]}; font-size: 13px; font-weight: 500; margin-top: 10px; }}
        .donut-stat-value {{ color: #FFFFFF; font-size: 22px; font-weight: 800; font-family: 'JetBrains Mono', monospace; }}

        /* Insight cards */
        .insight-card {{
            background-color: {THEME["card_bg"]}; border-left: 3px solid {THEME["primary"]};
            border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; font-size: 14px; color: {THEME["text"]};
        }}
        .insight-card b {{ color: {THEME["primary"]}; }}

        .footer-note {{ color: {THEME["neutral"]}; font-size: 12px; text-align: center; padding-top: 30px; }}
    </style>
""", unsafe_allow_html=True)

PLOTLY_TEMPLATE = "plotly_dark"
PLOTLY_FONT = dict(family="Inter, sans-serif", color=THEME["text"], size=12)
PLOTLY_LAYOUT = dict(
    template=PLOTLY_TEMPLATE,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=PLOTLY_FONT,
    title_font=dict(family="Inter, sans-serif", size=16, color=THEME["text"]),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    margin=dict(l=10, r=10, t=50, b=10),
    xaxis=dict(gridcolor=THEME["grid"], zerolinecolor=THEME["grid"]),
    yaxis=dict(gridcolor=THEME["grid"], zerolinecolor=THEME["grid"]),
)

# ----------------------------------------------------------------------------
# Sidebar controls
# ----------------------------------------------------------------------------
st.sidebar.markdown(f"""
    <div style="text-align:center; padding: 6px 0 18px 0;">
        <div style="font-size:34px;">📈</div>
        <div style="font-size:17px; font-weight:800; color:{THEME['text']};">NIFTY TERMINAL</div>
        <div style="font-size:11px; color:{THEME['neutral']}; letter-spacing:0.05em;">ANALYTICS · v2.0</div>
    </div>
""", unsafe_allow_html=True)
st.sidebar.markdown("##### ⚙️ Controls")
period_map = {"1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y", "2 Years": "2y"}
period_label = st.sidebar.selectbox("Lookback Period", list(period_map.keys()), index=2)
period = period_map[period_label]

watchlist_size = st.sidebar.slider(
    "Number of stocks to analyze (Market Overview / Correlation)",
    min_value=10, max_value=50, value=20, step=5,
    help="Fewer stocks load faster. Increase for a fuller market picture."
)

all_tickers = list(NIFTY50_STOCKS.keys())[:watchlist_size]

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**About**\n\n"
    "This dashboard pulls live/historical NSE data via Yahoo Finance and "
    "computes technical + statistical indicators — EMA/VWAP crossovers, RSI, "
    "rolling volatility, and cross-stock correlation — used to evaluate "
    "NIFTY 50 constituents.\n\n"
    "Built with Python, Streamlit, and Plotly."
)

st.sidebar.markdown("---")
st.sidebar.caption("Data may be delayed by ~15 minutes. For informational use only — not investment advice.")

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
import datetime
now_str = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

st.markdown(f"""
    <div class="hero-banner">
        <div>
            <div class="hero-title">NIFTY 50 Analytics Terminal</div>
            <div class="hero-sub">Tracking {len(all_tickers)} constituents · {period_label} lookback · Last refreshed {now_str}</div>
        </div>
        <div class="hero-badge"><span class="hero-badge-dot"></span>LIVE DATA FEED</div>
    </div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Tabs
# ----------------------------------------------------------------------------
tab_overview, tab_deepdive, tab_corr, tab_sector, tab_vol = st.tabs(
    ["🏠 Market Overview", "🔍 Stock Deep Dive", "🔗 Correlation", "🏭 Sector Performance", "📉 Volatility"]
)

# ============================================================================
# TAB 1: MARKET OVERVIEW
# ============================================================================
with tab_overview:
    with st.spinner("Fetching Nifty 50 index data..."):
        index_df = fetch_history(NIFTY_INDEX_TICKER, period=period)

    # ---- Big KPI strip (Power-BI style) ----
    if not index_df.empty:
        latest_k, change_k, change_pct_k = compute_daily_change(index_df)
        period_return_k = compute_period_return(index_df)
        vol_series_k = compute_rolling_volatility(index_df)
        latest_vol_k = vol_series_k.iloc[-1] if not vol_series_k.empty else np.nan
        trend_word = "Bullish" if change_pct_k >= 0 else "Bearish"
        trend_color = THEME["positive"] if change_pct_k >= 0 else THEME["negative"]

        kpi_specs = [
            ("#F59E0B", "NIFTY 50 LEVEL", f"{latest_k:,.0f}", "TODAY", f"{change_pct_k:+.2f}%", "TREND", trend_word),
            ("#3B82F6", f"{period_label.upper()} RETURN", f"{period_return_k:+.2f}%", "HIGH", f"{index_df['Close'].max():,.0f}", "LOW", f"{index_df['Close'].min():,.0f}"),
            ("#22C55E", "ANN. VOLATILITY", f"{latest_vol_k:.1f}%" if pd.notna(latest_vol_k) else "N/A", "WINDOW", "21D", "REGIME", "Elevated" if pd.notna(latest_vol_k) and latest_vol_k > 15 else "Normal"),
            ("#A78BFA", "STOCKS TRACKED", f"{len(all_tickers)}", "UNIVERSE", "NIFTY 50", "SECTORS", f"{len(set(v['sector'] for v in NIFTY50_STOCKS.values()))}"),
            ("#EF4444", "TRADING DAYS", f"{len(index_df)}", "PERIOD", period_label.upper(), "SOURCE", "NSE"),
        ]
        kpi_cols = st.columns(5)
        for col, (accent, label, value, sub1_l, sub1_v, sub2_l, sub2_v) in zip(kpi_cols, kpi_specs):
            with col:
                st.markdown(f"""
                    <div class="kpi-card" style="--accent:{accent}">
                        <div class="kpi-label">{label}</div>
                        <div class="kpi-value">{value}</div>
                        <div class="kpi-subrow">
                            <div class="kpi-sub"><div class="kpi-sub-label">{sub1_l}</div><div class="kpi-sub-value">{sub1_v}</div></div>
                            <div class="kpi-sub"><div class="kpi-sub-label">{sub2_l}</div><div class="kpi-sub-value">{sub2_v}</div></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    st.markdown("#### Market Snapshot — Multi-Asset")
    with st.spinner("Fetching indices, forex, and commodities..."):
        market_assets_data = fetch_market_assets(period="1mo")

    if market_assets_data:
        asset_cols = st.columns(len(MARKET_ASSETS))
        for i, (ticker, meta) in enumerate(MARKET_ASSETS.items()):
            df_a = market_assets_data.get(ticker)
            with asset_cols[i]:
                if df_a is not None and not df_a.empty:
                    latest_a, change_a, change_pct_a = compute_daily_change(df_a)
                    css_class = "asset-change-pos" if change_a >= 0 else "asset-change-neg"
                    arrow = "▲" if change_a >= 0 else "▼"
                    st.markdown(f"""
                        <div class="asset-card">
                            <div class="asset-label">{meta['label']}</div>
                            <div class="asset-value">{latest_a:,.2f}</div>
                            <div class="{css_class}">{arrow} {change_pct_a:+.2f}%</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="asset-card">
                            <div class="asset-label">{meta['label']}</div>
                            <div class="asset-value">—</div>
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.warning("Could not fetch multi-asset market data.")

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    if not index_df.empty:
        latest, change, change_pct = compute_daily_change(index_df)
        period_return = compute_period_return(index_df)
        col1.metric("NIFTY 50 Index", f"{latest:,.2f}", f"{change:+.2f} ({change_pct:+.2f}%)")
        col2.metric(f"{period_label} Return", f"{period_return:+.2f}%")
        vol_series = compute_rolling_volatility(index_df)
        latest_vol = vol_series.iloc[-1] if not vol_series.empty else np.nan
        col3.metric("Annualized Volatility", f"{latest_vol:.2f}%" if pd.notna(latest_vol) else "N/A")
        col4.metric("Trading Days Analyzed", f"{len(index_df)}")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=index_df.index, y=index_df["Close"],
            mode="lines", name="NIFTY 50",
            line=dict(color=THEME["primary"], width=2),
            fill="tozeroy", fillcolor="rgba(37, 99, 235, 0.08)"
        ))
        fig.update_layout(
            title="NIFTY 50 Index Trend",
            xaxis_title="Date", yaxis_title="Index Value",
            **PLOTLY_LAYOUT, height=420, hovermode="x unified"
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.warning("Could not fetch NIFTY 50 index data. Check your internet connection.")

    st.markdown("### Market Snapshot")
    with st.spinner(f"Fetching data for {len(all_tickers)} stocks..."):
        stock_data = fetch_multiple(all_tickers, period=period)

    summary_df = build_market_summary(stock_data)

    if not summary_df.empty:
        advances = int((summary_df["Change %"] > 0).sum())
        declines = int((summary_df["Change %"] < 0).sum())
        unchanged = int((summary_df["Change %"] == 0).sum())
        total_n = max(advances + declines + unchanged, 1)
        adv_pct = advances / total_n * 100

        gainers_mask = summary_df["Change %"] > 0
        gainers_df = summary_df[gainers_mask]
        losers_df = summary_df[~gainers_mask]

        donut_left, donut_right = st.columns(2)

        with donut_left:
            fig_breadth = go.Figure(go.Pie(
                values=[advances, declines + unchanged], hole=0.72,
                marker=dict(colors=[THEME["accent"], "#374151"]),
                textinfo="none", sort=False, direction="clockwise"
            ))
            fig_breadth.update_layout(
                **{**PLOTLY_LAYOUT, "margin": dict(l=0, r=0, t=10, b=0)}, height=230, showlegend=False,
                annotations=[dict(text=f"<b>{adv_pct:.1f}%</b>", x=0.5, y=0.5, font=dict(size=26, color="#FFFFFF"), showarrow=False)]
            )
            c1, c2 = st.columns([1, 1.1])
            with c1:
                st.markdown('<div class="donut-panel-title" style="margin-bottom:0;">MARKET BREADTH</div>', unsafe_allow_html=True)
                st.plotly_chart(fig_breadth, width='stretch', config={"displayModeBar": False})
            with c2:
                st.markdown(f"""
                    <div style="padding-top:28px;">
                        <div class="donut-stat-label">Advancers</div><div class="donut-stat-value">{advances}</div>
                        <div class="donut-stat-label">Decliners</div><div class="donut-stat-value">{declines}</div>
                        <div class="donut-stat-label">Unchanged</div><div class="donut-stat-value">{unchanged}</div>
                    </div>
                """, unsafe_allow_html=True)

        with donut_right:
            avg_gain = gainers_df["Change %"].mean() if not gainers_df.empty else 0
            avg_loss = losers_df["Change %"].mean() if not losers_df.empty else 0
            fig_momentum = go.Figure(go.Pie(
                values=[max(avg_gain, 0.01), abs(min(avg_loss, -0.01))], hole=0.72,
                marker=dict(colors=[THEME["positive"], THEME["negative"]]),
                textinfo="none", sort=False, direction="clockwise"
            ))
            fig_momentum.update_layout(
                **{**PLOTLY_LAYOUT, "margin": dict(l=0, r=0, t=10, b=0)}, height=230, showlegend=False,
                annotations=[dict(text=f"<b>{avg_gain:.2f}%</b>", x=0.5, y=0.5, font=dict(size=24, color="#FFFFFF"), showarrow=False)]
            )
            d1, d2 = st.columns([1, 1.1])
            with d1:
                st.markdown('<div class="donut-panel-title" style="margin-bottom:0;">AVG MOVE SIZE</div>', unsafe_allow_html=True)
                st.plotly_chart(fig_momentum, width='stretch', config={"displayModeBar": False})
            with d2:
                st.markdown(f"""
                    <div style="padding-top:28px;">
                        <div class="donut-stat-label">Avg Gainer Move</div><div class="donut-stat-value" style="color:{THEME['positive']}">+{avg_gain:.2f}%</div>
                        <div class="donut-stat-label">Avg Loser Move</div><div class="donut-stat-value" style="color:{THEME['negative']}">{avg_loss:.2f}%</div>
                        <div class="donut-stat-label">Net Watchlist Tilt</div><div class="donut-stat-value">{"Bullish" if advances >= declines else "Bearish"}</div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        # ---- Auto-generated insights ----
        st.markdown("##### 🧠 Auto-Generated Insights")
        best_row = summary_df.loc[summary_df["Change %"].idxmax()]
        worst_row = summary_df.loc[summary_df["Change %"].idxmin()]
        most_volatile = summary_df.loc[summary_df["Volatility %"].idxmax()]
        breadth_tone = "broad-based buying" if advances > declines else "broad-based selling" if declines > advances else "a mixed, indecisive session"

        st.markdown(f"""
            <div class="insight-card">📈 <b>{best_row['Company']}</b> led gainers today, up <b>{best_row['Change %']:+.2f}%</b> to ₹{best_row['Price']:,.2f}.</div>
            <div class="insight-card">📉 <b>{worst_row['Company']}</b> led losers, down <b>{worst_row['Change %']:+.2f}%</b> to ₹{worst_row['Price']:,.2f}.</div>
            <div class="insight-card">⚡ <b>{most_volatile['Company']}</b> is the most volatile stock in this watchlist at <b>{most_volatile['Volatility %']:.1f}%</b> annualized volatility.</div>
            <div class="insight-card">🧭 Market breadth ({advances} advances vs {declines} declines) suggests <b>{breadth_tone}</b> across the watchlist.</div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("**Top 5 Gainers**")
            top_gainers = summary_df.sort_values("Change %", ascending=False).head(5)
            st.dataframe(
                top_gainers[["Company", "Price", "Change %"]].set_index("Company")
                .style.background_gradient(subset=["Change %"], cmap="Greens"),
                width='stretch'
            )
        with col_right:
            st.markdown("**Top 5 Losers**")
            top_losers = summary_df.sort_values("Change %", ascending=True).head(5)
            st.dataframe(
                top_losers[["Company", "Price", "Change %"]].set_index("Company")
                .style.background_gradient(subset=["Change %"], cmap="Reds_r"),
                width='stretch'
            )

        st.markdown("**Full Market Summary**")
        st.dataframe(
            summary_df.set_index("Ticker")
            .style.background_gradient(subset=["Change %", "Period Return %"], cmap="RdYlGn")
            .background_gradient(subset=["Volatility %"], cmap="Oranges"),
            width='stretch', height=350
        )
        st.download_button(
            "⬇ Download Market Summary (CSV)",
            data=summary_df.to_csv(index=False).encode("utf-8"),
            file_name=f"nifty_market_summary_{period}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No stock data available. Check your internet connection.")

# ============================================================================
# TAB 2: STOCK DEEP DIVE
# ============================================================================
with tab_deepdive:
    ticker_names = {t: NIFTY50_STOCKS[t]["name"] for t in NIFTY50_STOCKS}
    selected_ticker = st.selectbox(
        "Select a stock",
        options=list(ticker_names.keys()),
        format_func=lambda x: f"{ticker_names[x]} ({x.replace('.NS','')})"
    )

    with st.spinner("Fetching stock data..."):
        df = fetch_history(selected_ticker, period=period)

    if df.empty:
        st.warning("Could not fetch data for this stock.")
    else:
        df = compute_ema(df)
        df = compute_vwap(df)
        df = compute_macd(df)
        df = compute_bollinger_bands(df)
        df["RSI"] = compute_rsi(df)
        df["ATR"] = compute_atr(df)
        fib_levels = compute_fibonacci_levels(df)

        latest, change, change_pct = compute_daily_change(df)
        period_return = compute_period_return(df)
        high_52 = df["Close"].max()
        low_52 = df["Close"].min()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Last Close", f"₹{latest:,.2f}", f"{change:+.2f} ({change_pct:+.2f}%)")
        c2.metric(f"{period_label} Return", f"{period_return:+.2f}%")
        c3.metric("Period High", f"₹{high_52:,.2f}")
        c4.metric("Period Low", f"₹{low_52:,.2f}")

        # Indicator toggles
        overlay_cols = st.columns(4)
        show_ema = overlay_cols[0].checkbox("EMA (9/21)", value=True)
        show_vwap = overlay_cols[1].checkbox("VWAP", value=True)
        show_bb = overlay_cols[2].checkbox("Bollinger Bands", value=False)
        show_fib = overlay_cols[3].checkbox("Fibonacci Levels", value=False)

        # Price chart with selectable overlays
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
            name="Price", increasing_line_color=THEME["positive"], decreasing_line_color=THEME["negative"]
        ))
        if show_ema:
            fig.add_trace(go.Scatter(x=df.index, y=df["EMA_9"], name="EMA 9", line=dict(color=THEME["accent"], width=1.5)))
            fig.add_trace(go.Scatter(x=df.index, y=df["EMA_21"], name="EMA 21", line=dict(color=THEME["accent2"], width=1.5)))
        if show_vwap:
            fig.add_trace(go.Scatter(x=df.index, y=df["VWAP"], name="VWAP", line=dict(color="#0EA5E9", width=1.5, dash="dot")))
        if show_bb:
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_Upper"], name="BB Upper", line=dict(color=THEME["neutral"], width=1, dash="dash")))
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lower"], name="BB Lower", line=dict(color=THEME["neutral"], width=1, dash="dash"), fill="tonexty", fillcolor="rgba(148,163,184,0.08)"))
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_Middle"], name="BB Middle (SMA 20)", line=dict(color=THEME["neutral"], width=1)))
        if show_fib:
            for label, level in fib_levels.items():
                fig.add_hline(y=level, line_dash="dot", line_color=THEME["accent2"], opacity=0.5,
                               annotation_text=label, annotation_position="right")

        fig.update_layout(
            title=f"{ticker_names[selected_ticker]} — Price Chart",
            xaxis_title="Date", yaxis_title="Price (₹)",
            **PLOTLY_LAYOUT, height=520, xaxis_rangeslider_visible=False,
            hovermode="x unified"
        )
        st.plotly_chart(fig, width='stretch')

        col_vol, col_rsi = st.columns(2)
        with col_vol:
            vol_fig = go.Figure()
            vol_fig.add_trace(go.Bar(x=df.index, y=df["Volume"], marker_color=THEME["neutral"]))
            vol_fig.update_layout(title="Trading Volume", **PLOTLY_LAYOUT, height=320)
            st.plotly_chart(vol_fig, width='stretch')

        with col_rsi:
            rsi_fig = go.Figure()
            rsi_fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI", line=dict(color=THEME["primary"])))
            rsi_fig.add_hline(y=70, line_dash="dash", line_color=THEME["negative"], annotation_text="Overbought")
            rsi_fig.add_hline(y=30, line_dash="dash", line_color=THEME["positive"], annotation_text="Oversold")
            rsi_fig.update_layout(title="RSI (14-day)", **PLOTLY_LAYOUT, height=320, yaxis_range=[0, 100])
            st.plotly_chart(rsi_fig, width='stretch')

        col_macd, col_atr = st.columns(2)
        with col_macd:
            macd_fig = go.Figure()
            hist_colors = [THEME["positive"] if v >= 0 else THEME["negative"] for v in df["MACD_Hist"].fillna(0)]
            macd_fig.add_trace(go.Bar(x=df.index, y=df["MACD_Hist"], name="Histogram", marker_color=hist_colors))
            macd_fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD", line=dict(color=THEME["primary"], width=1.5)))
            macd_fig.add_trace(go.Scatter(x=df.index, y=df["MACD_Signal"], name="Signal", line=dict(color=THEME["accent"], width=1.5)))
            macd_fig.update_layout(title="MACD (12, 26, 9)", **PLOTLY_LAYOUT, height=320)
            st.plotly_chart(macd_fig, width='stretch')

        with col_atr:
            atr_fig = go.Figure()
            atr_fig.add_trace(go.Scatter(x=df.index, y=df["ATR"], name="ATR", line=dict(color=THEME["accent2"], width=1.5), fill="tozeroy", fillcolor="rgba(167,139,250,0.1)"))
            atr_fig.update_layout(title="ATR — Average True Range (14-day)", **PLOTLY_LAYOUT, height=320)
            st.plotly_chart(atr_fig, width='stretch')

        with st.expander("Indicator Interpretation Guide"):
            st.write(
                "- **EMA 9 crossing above EMA 21** → short-term bullish momentum; crossing below → bearish momentum.\n"
                "- **Price above VWAP** → buyers in control for the period; **below VWAP** → sellers in control.\n"
                "- **RSI > 70** → potentially overbought; **RSI < 30** → potentially oversold.\n"
                "- **MACD line crossing above Signal line** → bullish crossover; below → bearish crossover. Histogram shows the gap between them.\n"
                "- **Bollinger Bands** — price near the upper band suggests overbought conditions relative to recent volatility; near the lower band suggests oversold. A narrowing band (squeeze) often precedes a big move.\n"
                "- **ATR** — higher values mean bigger price swings (higher volatility); used to size stop-losses.\n"
                "- **Fibonacci levels** — horizontal lines at key retracement percentages (23.6%, 38.2%, 50%, 61.8%) where price often finds support/resistance."
            )

# ============================================================================
# TAB 3: CORRELATION
# ============================================================================
with tab_corr:
    st.markdown("### Cross-Stock Return Correlation")
    st.caption("Shows how closely stocks move together based on daily returns. Values near +1 = move together, near -1 = move oppositely.")

    with st.spinner("Computing correlation matrix..."):
        stock_data_corr = fetch_multiple(all_tickers, period=period)
        returns_matrix = build_returns_matrix(stock_data_corr)

    if not returns_matrix.empty and returns_matrix.shape[1] > 1:
        corr = returns_matrix.corr()
        corr.columns = [c.replace(".NS", "") for c in corr.columns]
        corr.index = [c.replace(".NS", "") for c in corr.index]

        fig = px.imshow(
            corr, text_auto=".2f", aspect="auto",
            color_continuous_scale="RdBu", zmin=-1, zmax=1,
            title="Daily Returns Correlation Heatmap"
        )
        fig.update_layout(height=650, **PLOTLY_LAYOUT)
        st.plotly_chart(fig, width='stretch')

        st.markdown("**Most Correlated Pairs**")
        pairs = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool)).stack().reset_index()
        pairs.columns = ["Stock A", "Stock B", "Correlation"]
        top_pairs = pairs.reindex(pairs["Correlation"].abs().sort_values(ascending=False).index).head(10)
        st.dataframe(top_pairs, width='stretch', hide_index=True)
    else:
        st.warning("Not enough data to compute correlation. Try increasing the watchlist size.")

# ============================================================================
# TAB 4: SECTOR PERFORMANCE
# ============================================================================
with tab_sector:
    st.markdown("### Sector-Wise Performance")

    with st.spinner("Aggregating sector performance..."):
        stock_data_sector = fetch_multiple(all_tickers, period=period)
        summary_df2 = build_market_summary(stock_data_sector)

    if not summary_df2.empty:
        sector_perf = summary_df2.groupby("Sector")["Period Return %"].mean().sort_values(ascending=False).reset_index()

        fig = px.bar(
            sector_perf, x="Period Return %", y="Sector", orientation="h",
            color="Period Return %", color_continuous_scale=["#DC2626", "#F3F4F6", "#16A34A"],
            title=f"Average Sector Return — {period_label}"
        )
        fig.update_layout(**PLOTLY_LAYOUT, height=500)
        fig.update_yaxes(categoryorder='total ascending', gridcolor=THEME["grid"])
        st.plotly_chart(fig, width='stretch')

        st.markdown("**Sector Breakdown**")
        for sector in sector_perf["Sector"]:
            with st.expander(f"{sector}"):
                sector_stocks = summary_df2[summary_df2["Sector"] == sector][
                    ["Company", "Price", "Change %", "Period Return %"]
                ]
                st.dataframe(sector_stocks.set_index("Company"), width='stretch')
    else:
        st.warning("No data available for sector analysis.")

# ============================================================================
# TAB 5: VOLATILITY
# ============================================================================
with tab_vol:
    st.markdown("### Rolling Volatility Comparison")
    st.caption("Annualized volatility computed from a 21-day rolling standard deviation of daily returns.")

    compare_tickers = st.multiselect(
        "Select stocks to compare (max 6 for readability)",
        options=all_tickers,
        default=all_tickers[:3],
        format_func=lambda x: NIFTY50_STOCKS[x]["name"],
        max_selections=6
    )

    if compare_tickers:
        fig = go.Figure()
        for t in compare_tickers:
            df_t = fetch_history(t, period=period)
            if df_t.empty:
                continue
            vol_series = compute_rolling_volatility(df_t)
            fig.add_trace(go.Scatter(x=df_t.index, y=vol_series, mode="lines", name=NIFTY50_STOCKS[t]["name"]))

        fig.update_layout(
            title="Annualized Rolling Volatility (21-day window)",
            xaxis_title="Date", yaxis_title="Volatility (%)",
            **PLOTLY_LAYOUT, height=500, hovermode="x unified"
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("Select at least one stock to view volatility trends.")

# ----------------------------------------------------------------------------
# Footer
# ----------------------------------------------------------------------------
st.markdown(
    "<div class='footer-note'>Data sourced from Yahoo Finance via yfinance · "
    "Built with Streamlit & Plotly · For educational/informational purposes only, not financial advice.</div>",
    unsafe_allow_html=True
)