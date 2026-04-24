"""
Professional Nifty 500 Dashboard - Enhanced Version
With MACD, Bollinger, ADX, Backtesting, Risk Metrics
FIXED: backtest reuses fetched data, no duplicate downloads
"""

import streamlit as st
import pandas as pd
import numpy as np
from html import escape
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import THEMES, TOOLTIPS, FALLBACK_STOCKS
from utils import (
    load_nifty500, fetch_stock_data, calculate_technical_summary,
    fetch_fundamentals, backtest_signal, calculate_risk_metrics,
    calculate_professional_signal
)

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Nifty 500 Professional",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# THEME SETUP
# ============================================================================

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def set_theme(theme_name):
    st.session_state.theme = theme_name

def get_theme():
    return st.session_state.theme

def apply_theme():
    theme = THEMES[get_theme()]
    st.markdown(f"""
    <style>
    .stApp {{background-color: {theme['bg_primary']}}}
    .stMetric {{background-color: {theme['bg_card']}; border-radius: 10px; padding: 15px}}
    </style>
    """, unsafe_allow_html=True)

apply_theme()

# ============================================================================
# SIDEBAR - STOCK SELECTION
# ============================================================================

with st.sidebar:
    st.markdown("# 📊 Nifty 500 Professional")
    st.markdown("Advanced Analysis Dashboard")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌙 Dark", key="dark_btn"):
            set_theme("dark")
            st.rerun()
    with col2:
        if st.button("☀️ Light", key="light_btn"):
            set_theme("light")
            st.rerun()

    st.markdown("---")

    # Stock selection
    stocks, live_data = load_nifty500()

    if not live_data:
        st.warning("⚠️ Using fallback stock list (NSE server unavailable)")

    stocks["Label"] = stocks["Company Name"] + " (" + stocks["Symbol"] + ")"

    st.markdown("### 🔍 Select Stock")
    search = st.text_input("Search", placeholder="e.g., RELIANCE")

    if search:
        filtered = stocks[stocks["Label"].str.contains(search.upper(), regex=False)]
    else:
        filtered = stocks

    if not filtered.empty:
        selected = st.selectbox(
            "Choose stock",
            filtered["Label"],
            label_visibility="collapsed"
        )
        symbol = filtered[filtered["Label"] == selected]["Symbol"].values[0]
        company_name = filtered[filtered["Label"] == selected]["Company Name"].values[0]
    else:
        symbol = "RELIANCE"
        company_name = "Reliance Industries Ltd."

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Fetch data ONCE — reused by backtest and risk metrics
with st.spinner(f"Loading data for {symbol}..."):
    stock_data = fetch_stock_data(symbol)

if stock_data is not None:
    technical = calculate_technical_summary(stock_data)
    fundamentals = fetch_fundamentals(symbol)
    # Pass stock_data so backtest doesn't re-download
    risk_metrics = calculate_risk_metrics(stock_data, symbol)
    backtest = backtest_signal(symbol, stock_data=stock_data)
    signal_analysis = calculate_professional_signal(technical, [])
else:
    st.error("Could not fetch data for this stock. Please try another.")
    st.stop()

# Title
col1, col2, col3 = st.columns([1, 8, 1])
with col3:
    if st.button("🌓", help="Toggle theme"):
        set_theme("light" if get_theme() == "dark" else "dark")
        st.rerun()

st.markdown(f"# {escape(company_name)}")
st.markdown(f"*{symbol}.NS | Nifty 500 Constituent*")

# ============================================================================
# TABS
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Analysis", "📊 Fundamentals", "🔬 Backtesting", "⚠️ Risk", "🎯 Sector"]
)

# ============================================================================
# TAB 1: TECHNICAL ANALYSIS
# ============================================================================

with tab1:
    col_rec, col_conf = st.columns([1.2, 2])

    with col_rec:
        st.markdown("### Recommendation")
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: rgba(255,255,255,0.1); border-radius: 10px'>
        <h2 style='color: {signal_analysis["color"]}'>{signal_analysis["signal"]}</h2>
        <p><strong>Confidence: {signal_analysis['confidence']:.0f}%</strong></p>
        </div>
        """, unsafe_allow_html=True)

    with col_conf:
        st.markdown("### Signal Confirmations")
        for conf in signal_analysis["confirmations"]:
            st.markdown(f"- {conf}")

    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Price", f"₹{technical['close']:.2f}",
                 f"{technical['change']:.2f}%")
    with col2:
        st.metric("MA50", f"₹{technical['ma50']:.2f}",
                 help=TOOLTIPS["MA50"])
    with col3:
        st.metric("MA200", f"₹{technical['ma200']:.2f}",
                 help=TOOLTIPS["MA200"])
    with col4:
        st.metric("RSI(14)", f"{technical['rsi']:.0f}",
                 help=TOOLTIPS["RSI"])
    with col5:
        st.metric("Volatility", f"{technical['volatility']:.2f}%",
                 help="Annualized volatility")

    st.markdown("---")

    st.markdown("### Technical Chart (7 Indicators)")

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.5, 0.25, 0.25],
        vertical_spacing=0.12
    )

    fig.add_trace(go.Scatter(
        x=technical['close_series'].index, y=technical['close_series'],
        name='Price', line=dict(color='#c084fc', width=2)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=technical['ma50_series'].index, y=technical['ma50_series'],
        name='MA50', line=dict(color='#fbbf24', dash='dash')
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=technical['ma200_series'].index, y=technical['ma200_series'],
        name='MA200', line=dict(color='#f87171', dash='dash')
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=technical['rsi_series'].index, y=technical['rsi_series'],
        name='RSI(14)', line=dict(color='#34d399')
    ), row=2, col=1)

    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    fig.add_trace(go.Bar(
        x=technical['volume_series'].index, y=technical['volume_series'],
        name='Volume', marker=dict(color='#a78bfa'), showlegend=False
    ), row=3, col=1)

    fig.update_layout(height=800, hovermode='x unified', template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 2: FUNDAMENTALS
# ============================================================================

with tab2:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("P/E Ratio",
                 f"{fundamentals['pe_ratio']:.2f}" if fundamentals['pe_ratio'] != "N/A" else "N/A")
        st.metric("Market Cap",
                 f"₹{fundamentals['market_cap']/1e12:.2f}T" if fundamentals['market_cap'] != "N/A" else "N/A")
        st.metric("EPS",
                 f"₹{fundamentals['eps']:.2f}" if fundamentals['eps'] != "N/A" else "N/A")

    with col2:
        st.metric("Dividend Yield",
                 f"{fundamentals['dividend_yield']*100:.2f}%" if fundamentals['dividend_yield'] != "N/A" else "N/A")
        st.metric("Debt/Equity",
                 f"{fundamentals['debt_to_equity']:.2f}" if fundamentals['debt_to_equity'] != "N/A" else "N/A")
        st.metric("Profit Margin",
                 f"{fundamentals['profit_margin']*100:.2f}%" if fundamentals['profit_margin'] != "N/A" else "N/A")

    with col3:
        st.metric("52W High",
                 f"₹{fundamentals['52_week_high']:.2f}" if fundamentals['52_week_high'] != "N/A" else "N/A")
        st.metric("52W Low",
                 f"₹{fundamentals['52_week_low']:.2f}" if fundamentals['52_week_low'] != "N/A" else "N/A")

# ============================================================================
# TAB 3: BACKTESTING
# ============================================================================

with tab3:
    if backtest:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Win Rate", f"{backtest['win_rate']:.1f}%")
        with col2:
            st.metric("Total Trades", f"{backtest['total_trades']}")
        with col3:
            st.metric("Cumulative Return", f"{backtest['cumulative_return']:.2f}%")
        with col4:
            st.metric("Max Drawdown", f"{-backtest['max_drawdown']:.2f}%")

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Sharpe Ratio", f"{backtest['sharpe_ratio']:.2f}")
        with col2:
            st.metric("Avg Daily Return", f"{backtest['avg_daily_return']:.3f}%")
    else:
        st.warning("Not enough data for backtesting")

# ============================================================================
# TAB 4: RISK METRICS
# ============================================================================

with tab4:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        volatility = risk_metrics.get('volatility', 'N/A')
        st.metric("Volatility",
                 f"{volatility:.2f}%" if volatility != "N/A" else "N/A",
                 help=TOOLTIPS.get("VOLATILITY", "Annualized price volatility"))
    with col2:
        sharpe = risk_metrics.get('sharpe_ratio', 'N/A')
        st.metric("Sharpe Ratio",
                 f"{sharpe:.2f}" if sharpe != "N/A" else "N/A",
                 help=TOOLTIPS.get("SHARPE", ""))
    with col3:
        beta = risk_metrics.get('beta', 'N/A')
        st.metric("Beta",
                 f"{beta:.2f}" if beta != "N/A" else "N/A",
                 help=TOOLTIPS.get("BETA", ""))
    with col4:
        drawdown = risk_metrics.get('max_drawdown', 'N/A')
        st.metric("Max Drawdown",
                 f"{drawdown:.2f}%" if drawdown != "N/A" else "N/A",
                 help=TOOLTIPS.get("DRAWDOWN", ""))

# ============================================================================
# TAB 5: SECTOR ANALYSIS
# ============================================================================

with tab5:
    st.info("Sector analysis - Compare stock vs sector performance")
    st.markdown("*Coming soon: Sector rotation guide & peer comparison*")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
⚠️ **Educational Use Only** | This is a technical analysis tool, not financial advice.
Always do your own research and consult a financial professional.
""")
