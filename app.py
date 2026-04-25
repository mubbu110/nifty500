"""
StockSense India — Intelligent Stock Analysis for the Indian Market
Nifty 500 coverage · 7 technical indicators · News sentiment · Fundamentals · Backtesting · Risk · Sector comparison
"""

import time
import feedparser
import re
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
    page_title="StockSense India",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================================
# SESSION STATE
# ============================================================================

for key, default in [
    ("theme", "dark"),
    ("active_tab", 0),
    ("symbol", None),
    ("company_name", None),
    ("industry", None),
    ("selected_news", []),
    ("news_fetched_for", None),
    ("news_items", []),
    ("sector_period", "1Y Return"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ============================================================================
# THEME
# ============================================================================

def apply_theme():
    theme = THEMES["dark"]

    text_primary   = theme["text_primary"]    # #f0f4ff
    text_secondary = theme["text_secondary"]  # #c7d2fe
    bg_primary     = theme["bg_primary"]      # #0a0e27
    bg_card        = theme["bg_card"]
    bg_secondary   = theme["bg_secondary"]    # #0f1629
    accent         = theme["accent"]          # #c084fc
    border         = theme["border_color"]

    signal_bg      = "rgba(0,0,0,0.12)"
    signal_border  = "rgba(255,255,255,0.08)"
    caption_color  = "rgba(255,255,255,0.45)"
    metric_bg      = bg_card
    metric_border  = border
    plot_bg_css    = "rgba(15,22,41,0.8)"

    st.markdown(f"""
    <style>
    /* ── Sidebar hide ── */
    [data-testid="collapsedControl"] {{display:none}}
    section[data-testid="stSidebar"]  {{display:none}}

    /* ── App base ── */
    .stApp {{
        background-color: {bg_primary} !important;
        color: {text_primary} !important;
    }}

    /* ── All text elements ── */
    .stApp p, .stApp li, .stApp span,
    .stApp label, .stApp div {{
        color: {text_primary};
    }}
    .stApp h1, .stApp h2, .stApp h3,
    .stApp h4, .stApp h5, .stApp h6 {{
        color: {text_primary} !important;
    }}

    /* ── Markdown text ── */
    .stMarkdown p, .stMarkdown li {{
        color: {text_primary} !important;
    }}

    /* ── Caption / small text ── */
    .stCaption, .stCaption p {{
        color: {text_secondary} !important;
        opacity: 0.8;
    }}

    /* ── Metrics ── */
    [data-testid="stMetric"] {{
        background-color: {metric_bg};
        border-radius: 12px;
        padding: 16px;
        border: 1px solid {metric_border};
    }}
    [data-testid="stMetricLabel"] p {{
        color: {text_secondary} !important;
        font-size: 13px !important;
    }}
    [data-testid="stMetricValue"] {{
        color: {text_primary} !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background: {bg_secondary};
        border-radius: 10px 10px 0 0;
        padding: 4px 4px 0 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        padding: 8px 20px;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
        color: {text_secondary} !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: {accent} !important;
        background: {bg_primary} !important;
    }}

    /* ── Selectbox / inputs ── */
    .stSelectbox div[data-baseweb="select"] {{
        background-color: {bg_secondary} !important;
        border-color: {border} !important;
    }}
    .stSelectbox div[data-baseweb="select"] span {{
        color: {text_primary} !important;
    }}
    .stTextInput input {{
        background-color: {bg_secondary} !important;
        color: {text_primary} !important;
        border-color: {border} !important;
    }}

    /* ── Checkboxes ── */
    .stCheckbox label span {{
        color: {text_primary} !important;
    }}

    /* ── Radio buttons ── */
    .stRadio label span {{
        color: {text_primary} !important;
    }}

    /* ── Multiselect ── */
    .stMultiSelect div[data-baseweb="select"] {{
        background-color: {bg_secondary} !important;
    }}
    .stMultiSelect span {{
        color: {text_primary} !important;
    }}

    /* ── Info / warning / error boxes ── */
    .stAlert {{
        background-color: {bg_secondary} !important;
        color: {text_primary} !important;
        border-radius: 8px;
    }}

    /* ── Dataframe ── */
    .stDataFrame {{
        border: 1px solid {border};
        border-radius: 8px;
    }}

    /* ── Progress bar ── */
    .stProgress > div > div {{
        background-color: {accent} !important;
    }}

    /* ── Signal / card boxes (HTML) ── */
    .signal-box {{
        background: {signal_bg} !important;
        border: 1px solid {signal_border} !important;
        border-radius: 12px;
    }}

    /* ── Caption override for HTML spans ── */
    span.caption {{
        color: {caption_color} !important;
    }}

    /* ── Divider ── */
    hr {{
        border-color: {border} !important;
        opacity: 0.5;
    }}

    /* ── Buttons ── */
    .stButton button {{
        background-color: {bg_secondary} !important;
        color: {text_primary} !important;
        border: 1px solid {border} !important;
        border-radius: 8px !important;
    }}
    .stButton button:hover {{
        border-color: {accent} !important;
        color: {accent} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Store for use in HTML blocks
    st.session_state["_text_primary"]   = text_primary
    st.session_state["_text_secondary"] = text_secondary
    st.session_state["_caption_color"]  = caption_color
    st.session_state["_signal_bg"]      = signal_bg
    st.session_state["_signal_border"]  = signal_border

apply_theme()

# Shorthand helpers for inline HTML — dark mode hardcoded
_tp  = "#f0f4ff"
_ts  = "#c7d2fe"
_cap = "rgba(255,255,255,0.45)"
_sbg = "rgba(0,0,0,0.12)"
_sbd = "rgba(255,255,255,0.08)"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@st.cache_data(ttl=300, show_spinner=False)
def fetch_peer_close(sym: str):
    time.sleep(0.4)
    for suffix in [".NS", ".BO"]:
        try:
            d = yf.download(f"{sym}{suffix}", period="1y", progress=False, auto_adjust=True)
            if d.empty or len(d) < 30:
                continue
            c = d["Close"]
            if isinstance(c, pd.DataFrame):
                c = c.iloc[:, 0]
            return c.dropna()
        except Exception:
            pass
    return None

def find_sector(symbol, industry):
    sym_upper = symbol.upper()
    for sector, syms in SECTOR_MAPPING.items():
        if sym_upper in [s.upper() for s in syms]:
            return sector
    if industry and industry not in ("Unknown", ""):
        ind_lower = industry.lower()
        for sector in SECTOR_MAPPING:
            if sector.lower() in ind_lower or ind_lower in sector.lower():
                return sector
    return None

def get_peers(symbol, sector, max_peers=4):
    if not sector or sector not in SECTOR_MAPPING:
        return []
    return [s for s in SECTOR_MAPPING[sector] if s.upper() != symbol.upper()][:max_peers]

# ── News & Sentiment ─────────────────────────────────────────────────────────

BULLISH_WORDS = {
    "beats": 2.0, "profit": 1.8, "growth": 1.5, "surge": 2.0, "rally": 1.8,
    "upgrade": 2.0, "record": 1.8, "launches": 1.2, "wins": 1.5, "raises": 1.5,
    "buyback": 1.8, "strong": 1.5, "order": 1.2, "expansion": 1.5, "acquisition": 1.2,
    "dividend": 1.5, "outperform": 2.0, "buy": 1.5, "positive": 1.2, "recovery": 1.5,
}
BEARISH_WORDS = {
    "misses": -2.0, "loss": -1.8, "fraud": -3.0, "probe": -2.0, "downgrade": -2.0,
    "penalty": -2.0, "resigns": -1.5, "crash": -2.5, "weak": -1.5, "falls": -1.2,
    "default": -3.0, "debt": -1.2, "selloff": -2.0, "drop": -1.2, "cuts": -1.5,
    "lawsuit": -2.0, "investigation": -2.0, "miss": -1.8, "negative": -1.2, "concern": -1.2,
}

def score_headline(text: str) -> float:
    text_lower = text.lower()
    score = 0.0
    for word, weight in BULLISH_WORDS.items():
        if word in text_lower:
            score += weight
    for word, weight in BEARISH_WORDS.items():
        if word in text_lower:
            score += weight  # already negative
    return max(-10.0, min(10.0, score))

@st.cache_data(ttl=300, show_spinner=False)
def fetch_news(symbol: str) -> list:
    """
    Fetch news using Anthropic API with web_search tool.
    This works on Streamlit Cloud since api.anthropic.com is an allowed domain.
    Falls back to yfinance .news if API call fails.
    """
    import json as _json

    news = []

    # ── Method 1: Anthropic API with web_search ───────────────────────────
    try:
        import requests as _req

        prompt = (
            f"Search for the latest 10 news headlines about {symbol} NSE India stock. "
            f"Return ONLY a JSON array, no markdown, no explanation. "
            f"Each item must have: title (string), url (string), published (string, date only). "
            f"Example: [{{'title':'...','url':'...','published':'2026-04-25'}}]"
        )

        response = _req.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "tools": [{"type": "web_search_20250305", "name": "web_search"}],
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=20,
        )

        if response.status_code == 200:
            data = response.json()
            # Extract text from response
            full_text = " ".join(
                block.get("text", "")
                for block in data.get("content", [])
                if block.get("type") == "text"
            )
            # Parse JSON array from response
            start = full_text.find("[")
            end   = full_text.rfind("]") + 1
            if start != -1 and end > start:
                items = _json.loads(full_text[start:end])
                for item in items[:15]:
                    title = str(item.get("title", "")).strip()
                    if title:
                        news.append({
                            "title": title,
                            "link": item.get("url", "#"),
                            "published": str(item.get("published", ""))[:16],
                            "sentiment": score_headline(title),
                            "source": "Web Search",
                        })
    except Exception:
        pass

    if len(news) >= 3:
        return news[:15]

    # ── Method 2: yfinance .news (backup) ────────────────────────────────
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        yf_news = ticker.news or []
        for item in yf_news[:15]:
            content = item.get("content", item)
            title = (content.get("title") or item.get("title", "")).strip()
            link  = (
                content.get("canonicalUrl", {}).get("url")
                or content.get("clickThroughUrl", {}).get("url")
                or item.get("link", "#")
            )
            pub = str(content.get("pubDate") or item.get("providerPublishTime", ""))[:16]
            if title:
                news.append({
                    "title": title,
                    "link": link,
                    "published": pub,
                    "sentiment": score_headline(title),
                    "source": "Yahoo Finance",
                })
    except Exception:
        pass

    return news[:15]

# ============================================================================
# TOP BAR — logo + stock search + theme toggle (NO sidebar)
# ============================================================================

stocks, live_data = load_nifty500()
# Build label list — "Reliance Industries Ltd. (RELIANCE)"
stocks["Label"] = stocks["Company Name"] + " (" + stocks["Symbol"] + ")"
all_labels = stocks["Label"].tolist()

top_l, top_m, top_r = st.columns([2, 6, 1])

with top_l:
    st.markdown("### 🔍 StockSense India")

with top_m:
    # Single selectbox — Streamlit's built-in search works exactly like the index dropdown
    current_label = None
    if st.session_state.symbol:
        # Pre-select current stock so the box shows it after rerun
        matches = stocks[stocks["Symbol"] == st.session_state.symbol]["Label"]
        current_label = matches.values[0] if not matches.empty else None

    chosen = st.selectbox(
        "🔍 Search stock",
        options=[""] + all_labels,          # blank first = "no selection" state
        index=0 if current_label is None else ([""] + all_labels).index(current_label),
        placeholder="Type symbol or company name (e.g. INFY, Reliance, TCS…)",
        label_visibility="collapsed",
        key="stock_select_main",
    )

    if chosen and chosen != "":
        row = stocks[stocks["Label"] == chosen]
        if not row.empty:
            new_symbol   = row["Symbol"].values[0]
            new_company  = row["Company Name"].values[0]
            new_industry = row["Industry"].values[0] if "Industry" in row.columns else "Unknown"

            if new_symbol != st.session_state.symbol:
                st.session_state.symbol            = new_symbol
                st.session_state.company_name      = new_company
                st.session_state.industry          = new_industry
                st.session_state.selected_news     = []
                st.session_state.news_items        = []
                st.session_state.news_fetched_for  = None
                st.rerun()

with top_r:
    st.markdown("&nbsp;", unsafe_allow_html=True)

# ── If no stock selected yet, show landing prompt ────────────────────────────
if st.session_state.symbol is None:
    st.markdown("---")
    st.markdown("""
    ## Welcome to StockSense India 🔍
    **Intelligent stock analysis for the Indian market. Search any Nifty 500 stock above to get started.**

    ✅ Technical Analysis (7 indicators — Price, MA50/200, Bollinger, MACD, RSI, Volume)
    ✅ News Sentiment → BUY / SELL / HOLD signal
    ✅ Sector & Peer Comparison with index overlays
    ✅ Fundamentals calculated from raw financial statements
    ✅ Backtesting with Win Rate, Sharpe Ratio & Drawdown
    ✅ Risk Metrics — Beta, Volatility, Max Drawdown
    """)
    st.stop()

# ============================================================================
# DATA FETCH (only runs when symbol is set)
# ============================================================================

symbol       = st.session_state.symbol
company_name = st.session_state.company_name
industry     = st.session_state.industry

with st.spinner(f"Loading {symbol}…"):
    stock_data = fetch_stock_data(symbol)

if stock_data is None:
    st.error("Could not fetch data. Please try another stock.")
    st.stop()

technical       = calculate_technical_summary(stock_data)
fundamentals    = fetch_fundamentals(symbol)
risk_metrics    = calculate_risk_metrics(stock_data, symbol)
backtest        = backtest_signal(symbol, stock_data=stock_data)

# Auto-fetch news once per symbol
if st.session_state.news_fetched_for != symbol:
    st.session_state.news_items = fetch_news(symbol)
    st.session_state.news_fetched_for = symbol
    st.session_state.selected_news = []

news_items = st.session_state.news_items

# Signal uses currently selected news
signal_analysis = calculate_professional_signal(
    technical, st.session_state.selected_news
)

# ── Stock header ──────────────────────────────────────────────────────────────
st.markdown(f"# {escape(company_name)}")
st.markdown(f"*{symbol}.NS | {escape(str(industry))} | NSE Listed*")

# ============================================================================
# HORIZONTAL TABS — with JS tab-persistence across reruns
# ============================================================================

TAB_NAMES = [
    "📈 Analysis", "📰 News & Sentiment", "🎯 Sector",
    "📊 Fundamentals", "🔬 Backtesting", "⚠️ Risk",
]

# Inject JS that:
#  1. On load: clicks the tab matching session state (restores position after rerun)
#  2. On tab click: posts the tab index back to Streamlit via a hidden input
st.markdown("""
<script>
(function() {
    // Read desired tab from sessionStorage (survives Streamlit rerun)
    const desired = parseInt(sessionStorage.getItem('active_tab') || '0');

    function clickTab(idx) {
        const tabs = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
        if (tabs && tabs[idx]) {
            tabs[idx].click();
        }
    }

    // Click desired tab shortly after DOM is ready
    setTimeout(() => clickTab(desired), 120);

    // Listen for tab clicks and save to sessionStorage
    setTimeout(() => {
        const tabs = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
        tabs.forEach((tab, idx) => {
            tab.addEventListener('click', () => {
                sessionStorage.setItem('active_tab', String(idx));
            });
        });
    }, 300);
})();
</script>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(TAB_NAMES)

# tab1 = Analysis, tab2 = News & Sentiment, tab3 = Sector
# tab4 = Fundamentals, tab5 = Backtesting, tab6 = Risk

# ── Chart theme vars (dark mode only) ─────────────────────────────────────────
chart_template = "plotly_dark"
plot_bg        = "rgba(15,22,41,0.8)"
price_col      = "#e2e8f0"
grid_col       = "rgba(255,255,255,0.05)"
zero_line      = "rgba(255,255,255,0.15)"

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 — TECHNICAL ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────

with tab1:
    c1, c2 = st.columns([1.2, 2])
    with c1:
        st.markdown(f"""
        <div style='text-align:center;padding:30px 20px;background:{_sbg};
                    border:1px solid {_sbd};border-radius:12px'>
          <p style='margin:0 0 4px 0;font-size:22px;font-weight:700;
                    text-align:left;color:{_tp}'>Recommendation</p>
          <p style='margin:0 0 16px 0;font-size:13px;text-align:left;color:{_cap}'>
            Technical + News Signal</p>
          <h2 style='margin:0;font-size:36px;font-weight:800;
                     color:{signal_analysis["color"]}'>{signal_analysis["signal"]}</h2>
          <p style='margin:14px 0 0 0;font-size:16px;color:{_tp}'>
            <strong>Confidence: {signal_analysis['confidence']:.0f}%</strong></p>
          <p style='margin:6px 0 0 0;font-size:12px;color:{_cap}'>
            Based on technical + {len(st.session_state.selected_news)} news article(s)</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <p style='margin:0 0 16px 0;font-size:22px;font-weight:700;color:{_tp}'>
          Signal Confirmations</p>
        {"".join(f"<p style='margin:0 0 14px 0;font-size:16px;color:{_tp}'>{conf}</p>"
                 for conf in signal_analysis["confirmations"])}
        """, unsafe_allow_html=True)

    st.markdown("---")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Price",      f"₹{technical['close']:.2f}",      f"{technical['change']:.2f}%")
    m2.metric("MA50",       f"₹{technical['ma50']:.2f}",       help=TOOLTIPS["MA50"])
    m3.metric("MA200",      f"₹{technical['ma200']:.2f}",      help=TOOLTIPS["MA200"])
    m4.metric("RSI(14)",    f"{technical['rsi']:.0f}",          help=TOOLTIPS["RSI"])
    m5.metric("Volatility", f"{technical['volatility']:.2f}%",  help="Annualized volatility")

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
    bb_upper, bb_mid, bb_lower = calculate_bollinger_bands(close_s)

    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True,
        row_heights=[0.46, 0.20, 0.17, 0.17],
        vertical_spacing=0.06,   # increased from 0.03 to give titles room
        subplot_titles=(" ", "MACD", "RSI (14)", "Volume"),  # Row 1 title handled via annotation
    )
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
        line=dict(color=price_col, width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=ma50_s.index, y=ma50_s, name='MA50',
        line=dict(color='#f59e0b', width=1.5, dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=ma200_s.index, y=ma200_s, name='MA200',
        line=dict(color='#ef4444', width=1.5, dash='dash')), row=1, col=1)
    if macd_s is not None and msig_s is not None:
        hist = macd_s - msig_s
        fig.add_trace(go.Bar(x=hist.index, y=hist, name='MACD Hist',
            marker_color=['#34d399' if v >= 0 else '#f87171' for v in hist],
            showlegend=False), row=2, col=1)
        fig.add_trace(go.Scatter(x=macd_s.index, y=macd_s, name='MACD',
            line=dict(color='#3b82f6', width=1.5)), row=2, col=1)
        fig.add_trace(go.Scatter(x=msig_s.index, y=msig_s, name='Signal',
            line=dict(color='#f97316', width=1.5)), row=2, col=1)
        fig.add_hline(y=0, line_color=zero_line, line_width=1, row=2, col=1)
    fig.add_trace(go.Scatter(x=rsi_s.index, y=rsi_s, name='RSI(14)',
        line=dict(color='#10b981', width=1.5)), row=3, col=1)
    fig.add_hrect(y0=70, y1=100, fillcolor='rgba(239,68,68,0.08)',  line_width=0, row=3, col=1)
    fig.add_hrect(y0=0,  y1=30,  fillcolor='rgba(16,185,129,0.08)', line_width=0, row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="rgba(239,68,68,0.5)",   line_width=1, row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="rgba(16,185,129,0.5)",  line_width=1, row=3, col=1)
    fig.update_yaxes(range=[0, 100], row=3, col=1)
    vol_colors = ['#10b981' if i == 0 or close_s.iloc[i] >= close_s.iloc[i-1]
                  else '#ef4444' for i in range(len(close_s))]
    fig.add_trace(go.Bar(x=vol_s.index, y=vol_s, name='Volume',
        marker_color=vol_colors, showlegend=False), row=4, col=1)
    fig.update_layout(
        height=1020,
        hovermode='x unified',
        template=chart_template,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor=plot_bg,
        # Legend goes BELOW the chart to avoid overlapping subplot titles
        legend=dict(
            orientation="h",
            yanchor="top", y=-0.04,
            xanchor="left", x=0,
            font=dict(size=12),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=10, r=10, t=80, b=80),
        # Style the subplot title annotations
        annotations=[
            dict(
                text="Price + MA50/200 + Bollinger Bands",
                x=0.5, xref="paper",
                y=1.0, yref="paper",
                xanchor="center", yanchor="bottom",
                showarrow=False,
                font=dict(size=13, color="#94a3b8"),
            ),
        ] + [
            # Keep existing subplot titles but push them down slightly
            ann for ann in fig.layout.annotations
            if ann.text in ("MACD", "RSI (14)", "Volume")
        ],
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor=grid_col)

    # Style all subplot titles to be smaller and muted
    for ann in fig.layout.annotations:
        ann.font = dict(size=12, color="#94a3b8")

    st.plotly_chart(fig, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 — NEWS & SENTIMENT  (includes BUY/SELL/HOLD based on news)
# ──────────────────────────────────────────────────────────────────────────────

with tab2:
    st.markdown("### 📰 News & Sentiment")

    # ── Collect selected news from checkboxes (done BEFORE signal calc) ──
    selected = []
    if news_items:
        for i, item in enumerate(news_items):
            if st.session_state.get(f"news_{symbol}_{i}", False):
                selected.append(item)
    st.session_state.selected_news = selected

    # ── News-only signal ─────────────────────────────────────────────────
    news_signal_analysis = calculate_professional_signal(technical, selected)

    sig_col, detail_col = st.columns([1.2, 2])
    with sig_col:
        sig = news_signal_analysis
        st.markdown(f"""
        <div style='text-align:center;padding:30px 20px;background:{_sbg};
                    border:1px solid {_sbd};border-radius:12px'>
          <p style='margin:0 0 4px 0;font-size:22px;font-weight:700;
                    text-align:left;color:{_tp}'>Recommendation</p>
          <p style='margin:0 0 16px 0;font-size:13px;text-align:left;
                    color:{_cap}'>Technical + News Signal</p>
          <h2 style='margin:0;font-size:36px;font-weight:800;
                     color:{sig["color"]}'>{sig["signal"]}</h2>
          <p style='margin:14px 0 0 0;font-size:16px;color:{_tp}'>
            <strong>Confidence: {sig["confidence"]:.0f}%</strong></p>
          <p style='margin:6px 0 0 0;font-size:12px;color:{_cap}'>
            Based on technical + {len(selected)} news article(s)</p>
        </div>
        """, unsafe_allow_html=True)

    with detail_col:
        st.markdown(f"""
        <p style='margin:0 0 16px 0;font-size:22px;font-weight:700;
                  color:{_tp}'>Signal Confirmations</p>
        {"".join(f"<p style='margin:0 0 14px 0;font-size:16px;color:{_tp}'>{conf}</p>"
                 for conf in sig["confirmations"])}
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Article selection ─────────────────────────────────────────────────
    if not news_items:
        st.warning("No recent news found. Recommendation is based on technicals only.")
    else:
        st.markdown("**Select articles to include in the signal:**")
        st.caption("Tick articles → signal above updates instantly")

        newly_selected = []
        for i, item in enumerate(news_items):
            score = item["sentiment"]
            if score >= 1.5:
                badge = f"🟢 **{score:+.1f}** BULLISH"
                badge_color = "#34d399"
            elif score >= 0.3:
                badge = f"🟡 **{score:+.1f}** mildly bullish"
                badge_color = "#fbbf24"
            elif score <= -1.5:
                badge = f"🔴 **{score:+.1f}** BEARISH"
                badge_color = "#f87171"
            elif score <= -0.3:
                badge = f"🟠 **{score:+.1f}** mildly bearish"
                badge_color = "#fb923c"
            else:
                badge = f"⚪ **{score:+.1f}** neutral"
                badge_color = "#9ca3af"

            cb_col, text_col = st.columns([0.04, 0.96])
            with cb_col:
                checked = st.checkbox(
                    "", key=f"news_{symbol}_{i}",
                    value=st.session_state.get(f"news_{symbol}_{i}", False),
                )
            with text_col:
                pub    = item.get("published", "")[:16]
                source = item.get("source", "")
                st.markdown(
                    f"<span style='color:{badge_color};font-size:13px'>{badge}</span>"
                    f" &nbsp; <a href='{item['link']}' target='_blank' style='color:{_tp}'>{escape(item['title'])}</a>"
                    f" <span style='color:{_cap};font-size:11px'>&nbsp;·&nbsp;{source}&nbsp;{pub}</span>",
                    unsafe_allow_html=True,
                )
            if checked:
                newly_selected.append(item)

        st.session_state.selected_news = newly_selected

# ──────────────────────────────────────────────────────────────────────────────
# TAB 4 — FUNDAMENTALS
# ──────────────────────────────────────────────────────────────────────────────

with tab4:
    st.markdown("### 📊 Fundamentals")
    st.caption("All values calculated from raw financial statements — no pre-computed ratios.")

    def _fmt(val, fmt):
        try:
            return fmt.format(float(val))
        except Exception:
            return "N/A"

    def _fmt_large(val):
        try:
            v = float(val)
            if v >= 1e12: return f"₹{v/1e12:.2f}T"
            if v >= 1e9:  return f"₹{v/1e9:.2f}B"
            if v >= 1e7:  return f"₹{v/1e7:.2f}Cr"
            return f"₹{v:,.0f}"
        except Exception:
            return "N/A"

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("P/E Ratio",
                  _fmt(fundamentals['pe_ratio'], "{:.2f}"),
                  help="Formula: Current Price ÷ EPS (TTM)\nEPS = Net Income (TTM) ÷ Shares Outstanding")
        st.metric("Market Cap",
                  _fmt_large(fundamentals['market_cap']),
                  help="Formula: Current Market Price × Shares Outstanding")
        st.metric("EPS (TTM)",
                  _fmt(fundamentals['eps'], "₹{:.2f}"),
                  help="Formula: Net Income (last 4 quarters) ÷ Shares Outstanding")
    with c2:
        st.metric("Dividend Yield",
                  f"{fundamentals['dividend_yield']:.2f}%" if fundamentals['dividend_yield'] != "N/A" else "N/A",
                  help="Formula: Total dividends paid in last 1 year ÷ Current Price × 100")
        st.metric("Debt / Equity",
                  _fmt(fundamentals['debt_to_equity'], "{:.2f}"),
                  help="Formula: (Short-term Debt + Long-term Debt) ÷ Stockholders Equity × 100\nSource: Latest quarterly balance sheet")
        st.metric("Profit Margin",
                  _fmt(fundamentals['profit_margin'], "{:.2f}%"),
                  help="Formula: Net Income (TTM) ÷ Revenue (TTM) × 100")
    with c3:
        st.metric("52W High",
                  _fmt(fundamentals['52_week_high'], "₹{:.2f}"),
                  help="Formula: max(Daily High price) over last 252 trading days")
        st.metric("52W Low",
                  _fmt(fundamentals['52_week_low'], "₹{:.2f}"),
                  help="Formula: min(Daily Low price) over last 252 trading days")
        st.metric("Revenue (TTM)",
                  _fmt_large(fundamentals['revenue']),
                  help="Formula: Sum of Total Revenue over last 4 quarters (income statement)")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 5 — BACKTESTING
# ──────────────────────────────────────────────────────────────────────────────

with tab5:
    st.markdown("### 🔬 Backtesting")
    if backtest:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Win Rate",          f"{backtest['win_rate']:.1f}%")
        c2.metric("Total Trades",      f"{backtest['total_trades']}")
        c3.metric("Cumulative Return", f"{backtest['cumulative_return']:.2f}%")
        c4.metric("Max Drawdown (Strategy)",
                  f"-{abs(backtest['max_drawdown']):.2f}%",
                  delta=f"-{abs(backtest['max_drawdown']):.2f}%",
                  delta_color="inverse",
                  help="Worst peak-to-trough loss DURING ACTIVE TRADES only (when strategy signal was BUY). Not the same as full price drawdown.")
        st.markdown("---")
        c1b, c2b = st.columns(2)
        c1b.metric("Sharpe Ratio",     f"{backtest['sharpe_ratio']:.2f}")
        c2b.metric("Avg Daily Return", f"{backtest['avg_daily_return']:.3f}%")
        st.info("📌 Strategy: Price > MA200 · RSI 40–70 · MACD positive · Volume above 20d avg")
        st.caption("ℹ️ **Max Drawdown (Strategy)** measures loss only during active BUY signals. The Risk tab shows **Max Drawdown (Full History)** — the worst loss over the entire 3-year price history, which will always be larger.")
    else:
        st.warning("Not enough historical data for backtesting this stock.")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 6 — RISK METRICS
# ──────────────────────────────────────────────────────────────────────────────

with tab6:
    st.markdown("### ⚠️ Risk Metrics")
    c1, c2, c3, c4 = st.columns(4)
    v = risk_metrics.get('volatility',   'N/A')
    s = risk_metrics.get('sharpe_ratio', 'N/A')
    b = risk_metrics.get('beta',         'N/A')
    d = risk_metrics.get('max_drawdown', 'N/A')
    c1.metric("Volatility",   f"{v:.2f}%" if v != "N/A" else "N/A", help="Annualized price volatility")
    c2.metric("Sharpe Ratio", f"{s:.2f}"  if s != "N/A" else "N/A", help=TOOLTIPS.get("SHARPE", ""))
    c3.metric("Beta",         f"{b:.2f}"  if b != "N/A" else "N/A", help=TOOLTIPS.get("BETA", ""))
    c4.metric("Max Drawdown (Full History)",
              f"-{abs(float(d)):.2f}%" if d != "N/A" else "N/A",
              delta=f"-{abs(float(d)):.2f}%" if d != "N/A" else None,
              delta_color="inverse",
              help="Worst peak-to-trough loss over the FULL 3-year price history, regardless of any trading signal. Higher than strategy drawdown since it includes all bad periods.")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 — SECTOR ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────

with tab3:
    st.markdown("### 🎯 Sector Analysis")
    current_sector = find_sector(symbol, industry)
    st.markdown(f"**{symbol}** · Sector: **{current_sector or 'Not mapped'}** · Industry: *{industry}*")
    st.markdown("---")

    peer_symbols = get_peers(symbol, current_sector, max_peers=4)
    all_symbols  = [symbol] + peer_symbols

    if not peer_symbols:
        st.info(f"No peers mapped for **{current_sector or industry}**.")

    peer_closes = {}
    if len(all_symbols) > 1:
        prog = st.progress(0, text="Loading peer data…")
        for i, sym in enumerate(all_symbols):
            c = fetch_peer_close(sym)
            if c is not None:
                peer_closes[sym] = c
            prog.progress((i + 1) / len(all_symbols), text=f"Loaded {sym}")
        prog.empty()
    else:
        peer_closes[symbol] = technical['close_series']

    if not peer_closes:
        st.warning("Could not load peer data. Try again in a moment.")
    else:
        st.markdown("#### 📋 Peer Comparison")
        if peer_symbols:
            st.caption(f"Comparing: {', '.join(peer_closes.keys())}")

        rows = {}
        for sym, c in peer_closes.items():
            try:
                r1y = (c.iloc[-1]-c.iloc[0])/c.iloc[0]*100
                r3m = (c.iloc[-1]-c.iloc[-66])/c.iloc[-66]*100 if len(c)>66 else 0.0
                r1m = (c.iloc[-1]-c.iloc[-22])/c.iloc[-22]*100 if len(c)>22 else 0.0
                vol = c.pct_change().std()*np.sqrt(252)*100
                rows[sym] = {"Price (₹)": round(float(c.iloc[-1]),2),
                             "1M Return": round(float(r1m),2),
                             "3M Return": round(float(r3m),2),
                             "1Y Return": round(float(r1y),2),
                             "Volatility": round(float(vol),2)}
            except Exception:
                pass

        if rows:
            df_p = pd.DataFrame(rows).T
            df_p.index.name = "Symbol"

            def _col(val):
                try: return f"color: {'#34d399' if float(val)>=0 else '#f87171'}"
                except: return ""

            st.dataframe(
                df_p.style.applymap(_col, subset=["1M Return","3M Return","1Y Return"])
                    .format({"Price (₹)":"₹{:.2f}","1M Return":"{:+.2f}%",
                             "3M Return":"{:+.2f}%","1Y Return":"{:+.2f}%","Volatility":"{:.2f}%"}),
                use_container_width=True)

            st.markdown("#### 📈 1-Year Normalised Performance")
            st.caption(f"**{symbol}** shown as thick white line · peers shown thinner")

            # ── Peer toggle checkboxes ────────────────────────────────────
            peer_list = [s for s in peer_closes.keys() if s.upper() != symbol.upper()]
            if peer_list:
                st.markdown("**Toggle peers:**")
                toggle_cols = st.columns(min(len(peer_list), 5))
                visible_peers = set()
                for ci, ps in enumerate(peer_list):
                    key = f"peer_toggle_{symbol}_{ps}"
                    if key not in st.session_state:
                        st.session_state[key] = True
                    with toggle_cols[ci % len(toggle_cols)]:
                        if st.checkbox(ps, value=st.session_state[key], key=key):
                            visible_peers.add(ps)

            # ── Index overlay controls ────────────────────────────────────
            st.markdown("**➕ Add index overlay:**")

            ALL_INDICES = {
                # Broad Market
                "Nifty 50":                "^NSEI",
                "Nifty 100":               "^CNX100",
                "Nifty 200":               "^CNX200",
                "Nifty 500":               "^CNX500",
                "Nifty Next 50":           "^NSMIDCP",
                "Sensex":                  "^BSESN",
                "BSE 100":                 "BSE-100.BO",
                "BSE 500":                 "BSE-500.BO",
                # Mid & Small Cap
                "Nifty Midcap 50":         "^NSEMDCP50",
                "Nifty Midcap 100":        "NIFTY_MIDCAP_100.NS",
                "Nifty Smallcap 100":      "^CNXSC",
                "Nifty Smallcap 250":      "NIFTY_SMLCAP_250.NS",
                "Nifty Microcap 250":      "NIFTY_MICROCAP250.NS",
                "Nifty LargeMidcap 250":   "NIFTY_LARGEMID250.NS",
                # Sector
                "Nifty Bank":              "^NSEBANK",
                "Nifty IT":                "^CNXIT",
                "Nifty Auto":              "^CNXAUTO",
                "Nifty Pharma":            "^CNXPHARMA",
                "Nifty FMCG":              "^CNXFMCG",
                "Nifty Financial Services":"NIFTY_FIN_SERVICE.NS",
                "Nifty Metal":             "^CNXMETAL",
                "Nifty Energy":            "^CNXENERGY",
                "Nifty Realty":            "^CNXREALTY",
                "Nifty Media":             "^CNXMEDIA",
                "Nifty PSU Bank":          "^CNXPSUBANK",
                "Nifty Private Bank":      "NIFTY_PVT_BANK.NS",
                "Nifty Infrastructure":    "^CNXINFRA",
                "Nifty Commodities":       "^CNXCMDT",
                "Nifty Consumption":       "^CNXCONSUM",
                "Nifty Healthcare":        "NIFTY_HEALTHCARE.NS",
                "Nifty India Digital":     "NIFTY_IND_DIGITAL.NS",
                "Nifty Oil & Gas":         "NIFTY_OIL_GAS.NS",
                "Nifty Capital Markets":   "NIFTY_CAPITAL_MKT.NS",
                # Strategy / Theme
                "Nifty Div Opportunities": "^CNXDIVOP",
                "Nifty Growth Sectors 15": "^CNXGS15",
                "Nifty Alpha 50":          "NIFTY_ALPHA_50.NS",
                "Nifty Quality 30":        "NIFTY_QUALITY30.NS",
                "Nifty100 Low Volatility": "NIFTY100_LOWVOL30.NS",
            }

            INDEX_COLORS_MAP = [
                '#94a3b8','#fdba74','#7dd3fc','#a3e635','#f9a8d4',
                '#6ee7b7','#c4b5fd','#fde68a','#bfdbfe','#fca5a5',
            ]

            selected_indices = st.multiselect(
                "Choose indices to overlay on chart",
                options=list(ALL_INDICES.keys()),
                default=[],
                key=f"idx_multiselect_{symbol}",
                placeholder="Select one or more Nifty / BSE indices…",
            )

            @st.cache_data(ttl=300, show_spinner=False)
            def _fetch_index(ticker_sym):
                try:
                    d = yf.download(ticker_sym, period="1y", progress=False, auto_adjust=True)
                    if d.empty:
                        return None
                    c = d["Close"]
                    if isinstance(c, pd.DataFrame):
                        c = c.iloc[:, 0]
                    return c.dropna()
                except Exception:
                    return None

            # ── Build chart ───────────────────────────────────────────────
            PEER_COLORS = ['#fbbf24','#34d399','#60a5fa','#fb923c','#a78bfa']
            fig_n = go.Figure()
            peer_color_idx = 0

            for sym, c in peer_closes.items():
                try:
                    norm = c / c.iloc[0] * 100
                    is_main = (sym.upper() == symbol.upper())
                    if is_main:
                        fig_n.add_trace(go.Scatter(
                            x=norm.index, y=norm, name=f"▶ {sym}",
                            line=dict(color='#ffffff', width=5),
                        ))
                    elif sym in visible_peers:
                        color = PEER_COLORS[peer_color_idx % len(PEER_COLORS)]
                        fig_n.add_trace(go.Scatter(
                            x=norm.index, y=norm, name=sym,
                            line=dict(color=color, width=1.5),
                            opacity=0.65,
                        ))
                        peer_color_idx += 1
                except Exception:
                    pass

            # Add selected indices
            for ci, idx_name in enumerate(selected_indices):
                idx_close = _fetch_index(ALL_INDICES[idx_name])
                if idx_close is not None:
                    try:
                        norm_idx = idx_close / idx_close.iloc[0] * 100
                        color = INDEX_COLORS_MAP[ci % len(INDEX_COLORS_MAP)]
                        fig_n.add_trace(go.Scatter(
                            x=norm_idx.index, y=norm_idx,
                            name=idx_name,
                            line=dict(color=color, width=2, dash='dash'),
                            opacity=0.85,
                        ))
                    except Exception:
                        pass

            fig_n.add_hline(y=100, line_dash="dot", line_color="rgba(128,128,128,0.4)")
            fig_n.update_layout(
                height=460, template=chart_template,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=plot_bg,
                hovermode='x unified', yaxis_title="Rebased to 100",
                legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
                margin=dict(l=10, r=10, t=50, b=10),
            )
            st.plotly_chart(fig_n, use_container_width=True)

            st.markdown("#### 📊 Return Comparison")
            period_col = st.radio(
                "Period",
                ["1M Return", "3M Return", "1Y Return"],
                index=["1M Return", "3M Return", "1Y Return"].index(
                    st.session_state.get("sector_period", "1Y Return")
                ),
                horizontal=True,
                key=f"sector_period_radio_{symbol}",
            )
            st.session_state["sector_period"] = period_col

            bar_vals = df_p[period_col]
            fig_b = go.Figure(go.Bar(x=bar_vals.index, y=bar_vals,
                marker_color=['#34d399' if v>=0 else '#f87171' for v in bar_vals],
                text=[f"{v:+.1f}%" for v in bar_vals], textposition='outside'))
            fig_b.update_layout(height=350, template=chart_template,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=plot_bg,
                yaxis_title=f"{period_col} (%)", margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig_b, use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("**StockSense India** · ⚠️ Educational use only · Not financial advice · Always do your own research")
