"""
Nifty 500 Stock Impact Dashboard
Educational tool combining technical analysis + news sentiment
Author: [Your Name]
"""

import pandas as pd
import streamlit as st
from html import escape

from config import SCORE_BUY, SCORE_SELL
from utils import (
    load_nifty500,
    fetch_stock_data,
    calculate_technical_summary,
    fetch_stock_news,
    analyze_sentiment,
    generate_recommendation,
)
from theme import get_theme, set_theme, apply_theme_css, theme_toggle_button
from ui import (
    display_recommendation_card,
    display_analysis_reasons,
    display_metrics,
    plot_technical_chart,
    display_news_item,
    display_news_list_multiselect,
    display_footer,
)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Nifty 500 Stock Impact",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply theme CSS
apply_theme_css()

# Initialize session state
if "selected_news" not in st.session_state:
    st.session_state.selected_news = []

if "current_symbol" not in st.session_state:
    st.session_state.current_symbol = None

if "news_list" not in st.session_state:
    st.session_state.news_list = []

if "fetch_message" not in st.session_state:
    st.session_state.fetch_message = ""

if "manual_headline" not in st.session_state:
    st.session_state.manual_headline = ""


# ============================================================================
# SIDEBAR: STOCK SELECTION & NEWS FETCHING
# ============================================================================

with st.sidebar:
    # Title
    st.markdown('<div class="title">Nifty 500<br>Impact</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Stock Analysis Dashboard</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Theme toggle
    theme_toggle_button()
    
    st.markdown("---")
    
    # Load stocks
    stocks, live_data = load_nifty500()
    stocks["Label"] = stocks["Company Name"] + " (" + stocks["Symbol"] + ")"
    
    # Stock search & selection
    st.markdown("### 🔍 Select Stock")
    
    search_text = st.text_input(
        "Search stocks",
        value="",
        placeholder="e.g., Reliance, INFY",
        label_visibility="collapsed"
    )
    
    if search_text.strip():
        query = search_text.strip().lower()
        filtered_stocks = stocks[
            stocks["Label"].str.lower().str.contains(query, regex=False)
        ].copy()
    else:
        filtered_stocks = stocks.copy()
    
    if filtered_stocks.empty:
        st.warning("No matching stocks. Try a different search.")
        filtered_stocks = stocks.copy()
    
    selected_label = st.selectbox(
        "Choose from Nifty 500",
        filtered_stocks["Label"].tolist(),
        index=0,
        label_visibility="collapsed"
    )
    
    selected_row = filtered_stocks.loc[filtered_stocks["Label"] == selected_label].iloc[0]
    symbol = selected_row["Symbol"]
    company_name = selected_row["Company Name"]
    
    # Data source indicator
    if live_data:
        st.caption("✅ Live Nifty 500 list loaded")
    else:
        st.caption("⚠️ Using fallback stock list")
    
    # Reset state if stock changed
    if st.session_state.current_symbol != symbol:
        st.session_state.current_symbol = symbol
        st.session_state.news_list = []
        st.session_state.selected_news = []
        st.session_state.fetch_message = ""
        st.session_state.manual_headline = ""
    
    # News fetching section
    st.markdown("---")
    st.markdown("### 📰 News & Sentiment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Fetch News", width="stretch"):
            with st.spinner("Fetching latest news..."):
                st.session_state.news_list = fetch_stock_news(symbol, company_name)
                st.session_state.selected_news = []
            
            if st.session_state.news_list:
                st.session_state.fetch_message = f"✅ Loaded {len(st.session_state.news_list)} headlines"
            else:
                st.session_state.fetch_message = f"⚠️ No recent news found for {symbol}"
    
    with col2:
        if st.button("🗑️ Clear", width="stretch"):
            st.session_state.news_list = []
            st.session_state.selected_news = []
            st.session_state.fetch_message = ""
            st.session_state.manual_headline = ""
    
    if st.session_state.fetch_message:
        st.caption(st.session_state.fetch_message)
    
    # Manual headline input
    st.markdown("### ✍️ Paste Headline")
    
    manual = st.text_area(
        "Add custom headline to analyze",
        value=st.session_state.manual_headline,
        height=70,
        label_visibility="collapsed"
    )
    
    if st.button("Analyze Custom", width="stretch"):
        if manual.strip():
            st.session_state.manual_headline = manual.strip()
            st.session_state.selected_news = [
                {"title": st.session_state.manual_headline, "source": "Manual Entry", "date": ""}
            ]
        else:
            st.warning("Please enter a headline first")


# ============================================================================
# MAIN CONTENT: ANALYSIS & CHARTS
# ============================================================================

# Fetch data
stock_data = fetch_stock_data(symbol)
technical_analysis = calculate_technical_summary(stock_data)

# Get recommendation
recommendation, rec_class, rec_score, rec_reasons = generate_recommendation(
    technical_analysis,
    st.session_state.selected_news
)

# Page title
st.markdown(f'<div class="title">{escape(company_name)}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">{escape(symbol)}.NS | Nifty 500 Constituent</div>', unsafe_allow_html=True)

# Top recommendation cards
col_rec, col_reasons = st.columns([1.2, 2.2], gap="large")

with col_rec:
    display_recommendation_card(recommendation, rec_class, rec_score)

with col_reasons:
    display_analysis_reasons(rec_reasons)

# Disclaimer
st.info(
    "⚠️ **Educational Use Only** | This is a technical + sentiment analysis tool, "
    "not financial advice. Always do your own research and consult professionals."
)

# ============================================================================
# TECHNICAL ANALYSIS SECTION
# ============================================================================

st.markdown('<div class="section">📊 Technical Analysis</div>', unsafe_allow_html=True)

if technical_analysis is None:
    st.error(
        f"❌ Unable to fetch price data for {symbol}. "
        "Ensure you've selected the exact stock from the list."
    )
else:
    # Metrics row
    display_metrics(technical_analysis)
    
    st.markdown("---")
    
    # Price chart with MAs and RSI
    st.subheader("Price Trend (Last 1 Year)", anchor=False)
    plot_technical_chart(technical_analysis)

# ============================================================================
# NEWS & SENTIMENT SECTION
# ============================================================================

st.markdown('<div class="section">📰 Stock News & Sentiment</div>', unsafe_allow_html=True)

# Two-column layout: fetched news + selected analysis
col_fetch, col_analysis = st.columns([1.5, 1.5], gap="large")

with col_fetch:
    st.subheader("Available Headlines", anchor=False)
    
    if st.session_state.news_list:
        selected_indices = display_news_list_multiselect(st.session_state.news_list)
        
        if selected_indices:
            st.session_state.selected_news = [
                st.session_state.news_list[idx] for idx in selected_indices
            ]
            
            if st.button("📊 Analyze Selected", width="stretch", key="analyze_fetched"):
                st.success(f"Analyzing {len(st.session_state.selected_news)} article(s)...")
    else:
        st.info("Click 'Fetch News' to load headlines")

with col_analysis:
    st.subheader("Sentiment Analysis", anchor=False)
    
    if st.session_state.selected_news:
        for i, news in enumerate(st.session_state.selected_news):
            score, label, color, confidence = analyze_sentiment(news["title"])
            display_news_item(news, score, label, color, confidence)
    else:
        st.info("Select headlines to see sentiment analysis")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
display_footer()
