"""
Professional Nifty 500 Dashboard - Enhanced Version
With MACD, Bollinger, ADX, Backtesting, Risk Metrics, Sector Analysis
FIXED: all 7 indicators charted, sector tab fully built
"""

import streamlit as st
import pandas as pd
import numpy as np
from html import escape
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

from config import THEMES, TOOLTIPS, FALLBACK_STOCKS, SECTOR_MAPPING
from utils import (
    load_nifty500, fetch_stock_data, calculate_technical_summary,
    fetch_fundamentals, backtest_signal, calculate_risk_metrics,
    calculate_professional_signal, calculate_bollinger_bands
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
# SIDEBAR
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

    stocks, live_data = load_nifty500()

    if not live_data:
        st.warning("⚠️ Using fallback stock list (NSE server unavailable)")

    stocks["Label"] = stocks["Company Name"] + " (" + stocks["Symbol"] + ")"

    st.markdown("### 🔍 Select Stock")
    search = st.text_input("Search", placeholder="e.g., RELIANCE")

    filtered = stocks[stocks["Label"].str.contains(search.upper(), regex=False)] if search else stocks

    if not filtered.empty:
        selected = st.selectbox("Choose stock", filtered["Label"], label_visibility="collapsed")
        symbol = filtered[filtered["Label"] == selected]["Symbol"].values[0]
        company_name = filtered[filtered["Label"] == selected]["Company Name"].values[0]
        industry = filtered[filtered["Label"] == selected]["Industry"].values[0] if "Industry" in filtered.columns else "Unknown"
    else:
        symbol, company_name, industry = "RELIANCE", "Reliance Industries Ltd.", "Oil Gas & Consumable Fuels"

# ============================================================================
# DATA FETCH — once, reused by all tabs
# ============================================================================

with st.spinner(f"Loading data for {symbol}..."):
    stock_data = fetch_stock_data(symbol)

if stock_data is None:
    st.error("Could not fetch data for this stock. Please try another.")
    st.stop()

technical      = calculate_technical_summary(stock_data)
fundamentals   = fetch_fundamentals(symbol)
risk_metrics   = calculate_risk_metrics(stock_data, symbol)
backtest       = backtest_signal(symbol, stock_data=stock_data)
signal_analysis = calculate_professional_signal(technical, [])

# Title
col_t1, col_t2, col_t3 = st.columns([1, 8, 1])
with col_t3:
    if st.button("🌓", help="Toggle theme"):
        set_theme("light" if get_theme() == "dark" else "dark")
        st.rerun()

st.markdown(f"# {escape(company_name)}")
st.markdown(f"*{symbol}.NS | {escape(str(industry))} | Nifty 500 Constituent*")

# ============================================================================
# TABS
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Analysis", "📊 Fundamentals", "🔬 Backtesting", "⚠️ Risk", "🎯 Sector"]
)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 — TECHNICAL ANALYSIS (7 indicators)
# ──────────────────────────────────────────────────────────────────────────────

with tab1:
    c1, c2 = st.columns([1.2, 2])

    with c1:
        st.markdown("### Recommendation")
        st.markdown(f"""
        <div style='text-align:center;padding:20px;background:rgba(255,255,255,0.07);border-radius:10px'>
        <h2 style='color:{signal_analysis["color"]}'>{signal_analysis["signal"]}</h2>
        <p><strong>Confidence: {signal_analysis['confidence']:.0f}%</strong></p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("### Signal Confirmations")
        for conf in signal_analysis["confirmations"]:
            st.markdown(f"- {conf}")

    st.markdown("---")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Price",      f"₹{technical['close']:.2f}",   f"{technical['change']:.2f}%")
    m2.metric("MA50",       f"₹{technical['ma50']:.2f}",    help=TOOLTIPS["MA50"])
    m3.metric("MA200",      f"₹{technical['ma200']:.2f}",   help=TOOLTIPS["MA200"])
    m4.metric("RSI(14)",    f"{technical['rsi']:.0f}",       help=TOOLTIPS["RSI"])
    m5.metric("Volatility", f"{technical['volatility']:.2f}%", help="Annualized volatility")

    st.markdown("---")
    st.markdown("### 📊 Technical Chart — 7 Indicators")
    st.caption("① Price  ② MA50  ③ MA200  ④ Bollinger Bands  ⑤ MACD  ⑥ RSI  ⑦ Volume")

    close_s = technical['close_series']
    ma50_s  = technical['ma50_series']
    ma200_s = technical['ma200_series']
    rsi_s   = technical['rsi_series']
    vol_s   = technical['volume_series']
    macd_s  = technical.get('macd_series')
    msig_s  = technical.get('macd_signal_series')

    # Bollinger Bands
    bb_upper, bb_mid, bb_lower = calculate_bollinger_bands(close_s)

    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        row_heights=[0.44, 0.20, 0.18, 0.18],
        vertical_spacing=0.03,
        subplot_titles=("Price + MA50/200 + Bollinger Bands", "MACD", "RSI (14)", "Volume"),
    )

    # ── Row 1: Price + MAs + Bollinger ──
    if bb_upper is not None:
        fig.add_trace(go.Scatter(x=bb_upper.index, y=bb_upper, name='BB Upper',
            line=dict(color='rgba(192,132,252,0.35)', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=bb_lower.index, y=bb_lower, name='BB Lower',
            line=dict(color='rgba(192,132,252,0.35)', width=1),
            fill='tonexty', fillcolor='rgba(192,132,252,0.05)'), row=1, col=1)
        fig.add_trace(go.Scatter(x=bb_mid.index, y=bb_mid, name='BB Mid',
            line=dict(color='rgba(192,132,252,0.55)', width=1, dash='dot'),
            showlegend=False), row=1, col=1)

    fig.add_trace(go.Scatter(x=close_s.index, y=close_s, name='Price',
        line=dict(color='#e2e8f0', width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=ma50_s.index, y=ma50_s, name='MA50',
        line=dict(color='#fbbf24', width=1.5, dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=ma200_s.index, y=ma200_s, name='MA200',
        line=dict(color='#f87171', width=1.5, dash='dash')), row=1, col=1)

    # ── Row 2: MACD ──
    if macd_s is not None and msig_s is not None:
        hist = macd_s - msig_s
        fig.add_trace(go.Bar(x=hist.index, y=hist, name='MACD Hist',
            marker_color=['#34d399' if v >= 0 else '#f87171' for v in hist],
            showlegend=False), row=2, col=1)
        fig.add_trace(go.Scatter(x=macd_s.index, y=macd_s, name='MACD',
            line=dict(color='#60a5fa', width=1.5)), row=2, col=1)
        fig.add_trace(go.Scatter(x=msig_s.index, y=msig_s, name='Signal',
            line=dict(color='#fb923c', width=1.5)), row=2, col=1)
        fig.add_hline(y=0, line_color='rgba(255,255,255,0.15)', line_width=1, row=2, col=1)

    # ── Row 3: RSI ──
    fig.add_trace(go.Scatter(x=rsi_s.index, y=rsi_s, name='RSI(14)',
        line=dict(color='#34d399', width=1.5)), row=3, col=1)
    fig.add_hrect(y0=70, y1=100, fillcolor='rgba(248,113,113,0.08)', line_width=0, row=3, col=1)
    fig.add_hrect(y0=0,  y1=30,  fillcolor='rgba(52,211,153,0.08)',  line_width=0, row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="rgba(248,113,113,0.5)", line_width=1, row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="rgba(52,211,153,0.5)",  line_width=1, row=3, col=1)
    fig.update_yaxes(range=[0, 100], row=3, col=1)

    # ── Row 4: Volume (green/red by day) ──
    vol_colors = ['#34d399' if i == 0 or close_s.iloc[i] >= close_s.iloc[i - 1]
                  else '#f87171' for i in range(len(close_s))]
    fig.add_trace(go.Bar(x=vol_s.index, y=vol_s, name='Volume',
        marker_color=vol_colors, showlegend=False), row=4, col=1)

    fig.update_layout(
        height=950,
        hovermode='x unified',
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15,22,41,0.8)',
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        margin=dict(l=10, r=10, t=60, b=10),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')

    st.plotly_chart(fig, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 — FUNDAMENTALS
# ──────────────────────────────────────────────────────────────────────────────

with tab2:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("P/E Ratio",    f"{fundamentals['pe_ratio']:.2f}"          if fundamentals['pe_ratio']       != "N/A" else "N/A")
        st.metric("Market Cap",   f"₹{fundamentals['market_cap']/1e12:.2f}T" if fundamentals['market_cap']     != "N/A" else "N/A")
        st.metric("EPS",          f"₹{fundamentals['eps']:.2f}"              if fundamentals['eps']            != "N/A" else "N/A")
    with c2:
        st.metric("Dividend Yield",  f"{fundamentals['dividend_yield']*100:.2f}%" if fundamentals['dividend_yield'] != "N/A" else "N/A")
        st.metric("Debt/Equity",     f"{fundamentals['debt_to_equity']:.2f}"      if fundamentals['debt_to_equity'] != "N/A" else "N/A")
        st.metric("Profit Margin",   f"{fundamentals['profit_margin']*100:.2f}%"  if fundamentals['profit_margin']  != "N/A" else "N/A")
    with c3:
        st.metric("52W High", f"₹{fundamentals['52_week_high']:.2f}" if fundamentals['52_week_high'] != "N/A" else "N/A")
        st.metric("52W Low",  f"₹{fundamentals['52_week_low']:.2f}"  if fundamentals['52_week_low']  != "N/A" else "N/A")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 — BACKTESTING
# ──────────────────────────────────────────────────────────────────────────────

with tab3:
    if backtest:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Win Rate",          f"{backtest['win_rate']:.1f}%",               help=TOOLTIPS.get("WIN_RATE", ""))
        c2.metric("Total Trades",      f"{backtest['total_trades']}")
        c3.metric("Cumulative Return", f"{backtest['cumulative_return']:.2f}%")
        c4.metric("Max Drawdown",      f"{abs(backtest['max_drawdown']):.2f}%")
        st.markdown("---")
        c1b, c2b = st.columns(2)
        c1b.metric("Sharpe Ratio",     f"{backtest['sharpe_ratio']:.2f}",    help=TOOLTIPS.get("SHARPE", ""))
        c2b.metric("Avg Daily Return", f"{backtest['avg_daily_return']:.3f}%")
        st.info("📌 Strategy: Price > MA200 · RSI 40–70 · MACD positive · Volume above 20d avg")
    else:
        st.warning("Not enough historical data for backtesting this stock.")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 4 — RISK METRICS
# ──────────────────────────────────────────────────────────────────────────────

with tab4:
    c1, c2, c3, c4 = st.columns(4)
    v = risk_metrics.get('volatility',   'N/A')
    s = risk_metrics.get('sharpe_ratio', 'N/A')
    b = risk_metrics.get('beta',         'N/A')
    d = risk_metrics.get('max_drawdown', 'N/A')
    c1.metric("Volatility",   f"{v:.2f}%" if v != "N/A" else "N/A", help="Annualized price volatility")
    c2.metric("Sharpe Ratio", f"{s:.2f}"  if s != "N/A" else "N/A", help=TOOLTIPS.get("SHARPE", ""))
    c3.metric("Beta",         f"{b:.2f}"  if b != "N/A" else "N/A", help=TOOLTIPS.get("BETA", ""))
    c4.metric("Max Drawdown", f"{d:.2f}%" if d != "N/A" else "N/A", help=TOOLTIPS.get("DRAWDOWN", ""))

# ──────────────────────────────────────────────────────────────────────────────
# TAB 5 — SECTOR ANALYSIS (fully built)
# ──────────────────────────────────────────────────────────────────────────────

with tab5:
    st.markdown("### 🎯 Sector Analysis")

    # Identify sector
    current_sector = None
    for sector, syms in SECTOR_MAPPING.items():
        if any(s in symbol for s in syms):
            current_sector = sector
            break
    if current_sector is None and industry not in ("Unknown", None, ""):
        current_sector = str(industry)

    st.markdown(
        f"**{symbol}** · Sector: **{current_sector or 'Not mapped'}** · Industry: *{industry}*"
    )
    st.markdown("---")

    # Peers
    peer_symbols = []
    if current_sector and current_sector in SECTOR_MAPPING:
        peer_symbols = [s for s in SECTOR_MAPPING[current_sector] if s != symbol][:4]

    all_symbols = [symbol] + peer_symbols
    st.markdown(f"#### 📋 Peer Comparison")
    if peer_symbols:
        st.caption(f"Stocks compared: {', '.join(all_symbols)}")
    else:
        st.caption("No peers mapped for this sector — showing standalone stats.")

    # Fetch peer data
    peer_rows = {}
    prog = st.progress(0, text="Fetching peer data…")
    for idx, sym in enumerate(all_symbols):
        try:
            d = yf.download(f"{sym}.NS", period="1y", progress=False)
            if not d.empty and len(d) > 50:
                c = d['Close']
                if isinstance(c, pd.DataFrame):
                    c = c.iloc[:, 0]
                ret_1y = (c.iloc[-1] - c.iloc[0])  / c.iloc[0]  * 100
                ret_3m = (c.iloc[-1] - c.iloc[-66]) / c.iloc[-66] * 100 if len(c) > 66 else 0.0
                ret_1m = (c.iloc[-1] - c.iloc[-22]) / c.iloc[-22] * 100 if len(c) > 22 else 0.0
                vol    = c.pct_change().std() * np.sqrt(252) * 100
                peer_rows[sym] = {
                    "Price (₹)":    round(float(c.iloc[-1]), 2),
                    "1M Return":    round(float(ret_1m), 2),
                    "3M Return":    round(float(ret_3m), 2),
                    "1Y Return":    round(float(ret_1y), 2),
                    "Volatility":   round(float(vol), 2),
                }
        except Exception:
            pass
        prog.progress((idx + 1) / len(all_symbols), text=f"Fetching {sym}…")
    prog.empty()

    if peer_rows:
        df_p = pd.DataFrame(peer_rows).T
        df_p.index.name = "Symbol"

        def _col(val):
            try:
                return f"color: {'#34d399' if float(val) >= 0 else '#f87171'}"
            except Exception:
                return ""

        styled_df = (
            df_p.style
            .applymap(_col, subset=["1M Return", "3M Return", "1Y Return"])
            .format({
                "Price (₹)":  "₹{:.2f}",
                "1M Return":  "{:+.2f}%",
                "3M Return":  "{:+.2f}%",
                "1Y Return":  "{:+.2f}%",
                "Volatility": "{:.2f}%",
            })
        )
        st.dataframe(styled_df, use_container_width=True)

        # ── Normalised 1Y performance chart ──
        st.markdown("#### 📈 1-Year Normalised Performance")
        st.caption("All stocks rebased to 100 at start of period")

        CHART_COLORS = ['#c084fc', '#fbbf24', '#34d399', '#60a5fa', '#fb923c']
        fig_norm = go.Figure()

        for i, sym in enumerate(all_symbols):
            try:
                d = yf.download(f"{sym}.NS", period="1y", progress=False)
                if not d.empty:
                    c = d['Close']
                    if isinstance(c, pd.DataFrame):
                        c = c.iloc[:, 0]
                    norm = c / c.iloc[0] * 100
                    fig_norm.add_trace(go.Scatter(
                        x=norm.index, y=norm, name=sym,
                        line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=2),
                    ))
            except Exception:
                pass

        fig_norm.add_hline(y=100, line_dash="dot", line_color="rgba(255,255,255,0.25)")
        fig_norm.update_layout(
            height=420, template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,22,41,0.8)',
            hovermode='x unified', yaxis_title="Rebased (100 = start)",
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig_norm, use_container_width=True)

        # ── Return bar chart with period selector ──
        st.markdown("#### 📊 Return Comparison")
        period_sel = st.radio("Period", ["1M Return", "3M Return", "1Y Return"],
                              horizontal=True, key="sector_period")
        bar_vals   = df_p[period_sel]
        fig_bar = go.Figure(go.Bar(
            x=bar_vals.index, y=bar_vals,
            marker_color=['#34d399' if v >= 0 else '#f87171' for v in bar_vals],
            text=[f"{v:+.1f}%" for v in bar_vals],
            textposition='outside',
        ))
        fig_bar.update_layout(
            height=350, template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,22,41,0.8)',
            yaxis_title=f"{period_sel} (%)",
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    else:
        st.warning("Could not load peer data. Check your connection or try a different stock.")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
⚠️ **Educational Use Only** | This is a technical analysis tool, not financial advice.
Always do your own research and consult a financial professional.
""")
