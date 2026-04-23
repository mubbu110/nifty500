"""
Reusable UI components for displaying data, charts, and tooltips
"""

from html import escape
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from config import TOOLTIPS
from theme import get_colors


def display_recommendation_card(recommendation, rec_class, score):
    """
    Display main recommendation card (BUY/SELL/HOLD).
    
    Args:
        recommendation: 'BUY', 'SELL', or 'HOLD'
        rec_class: CSS class name (buy, sell, hold)
        score: Numerical composite score
    """
    colors = get_colors()
    
    html = f'''
    <div class="card {rec_class}">
        <div style="opacity: 0.8; font-size: 12px;">Recommendation</div>
        <div class="signal">{recommendation}</div>
        <div class="small-note">Composite score: {score:+.1f}/10</div>
    </div>
    '''
    
    st.markdown(html, unsafe_allow_html=True)


def display_analysis_reasons(reasons):
    """
    Display list of reasons supporting the recommendation.
    
    Args:
        reasons: List of reason strings
    """
    colors = get_colors()
    
    reason_html = "<br>".join(escape(reason) for reason in reasons[:6])
    
    html = f'''
    <div class="card">
        <strong>Why this signal?</strong>
        <div style="margin-top: 8px;" class="small-note">
            {reason_html}
        </div>
    </div>
    '''
    
    st.markdown(html, unsafe_allow_html=True)


def display_metrics(technical_data):
    """
    Display key technical metrics in columns.
    
    Args:
        technical_data: Dict from calculate_technical_summary()
    """
    if technical_data is None:
        st.warning("Unable to load technical data for this stock")
        return
    
    m1, m2, m3, m4, m5 = st.columns(5)
    
    with m1:
        st.metric(
            "Price",
            f"₹{technical_data['close']:,.2f}",
            f"{technical_data['change']:+.2f} ({technical_data['change_pct']:+.2f}%)",
            help="Current closing price and daily change"
        )
    
    with m2:
        st.metric(
            "1Y Return",
            f"{technical_data['one_year_return']:+.1f}%",
            help=TOOLTIPS["ONE_YEAR_RETURN"]
        )
    
    with m3:
        st.metric(
            "MA 50",
            f"₹{technical_data['ma50']:,.2f}",
            help=TOOLTIPS["MA50"]
        )
    
    with m4:
        st.metric(
            "MA 200",
            f"₹{technical_data['ma200']:,.2f}",
            help=TOOLTIPS["MA200"]
        )
    
    with m5:
        rsi_value = technical_data['rsi']
        rsi_status = (
            "⚠️ Overbought" if rsi_value > 70
            else "⚠️ Oversold" if rsi_value < 30
            else "Neutral"
        )
        st.metric(
            "RSI (14)",
            f"{rsi_value:.0f}",
            rsi_status,
            help=TOOLTIPS["RSI"]
        )


def plot_technical_chart(technical_data):
    """
    Create professional chart: price + MAs above, RSI below.
    
    Args:
        technical_data: Dict from calculate_technical_summary()
    """
    colors = get_colors()
    
    # Get 1-year data
    close = technical_data["close_series"]
    ma50 = technical_data["ma50_series"]
    ma200 = technical_data["ma200_series"]
    rsi = technical_data["rsi_series"]
    
    one_year_ago = close.index[-1] - pd.Timedelta(days=365)
    close_1y = close[close.index >= one_year_ago]
    ma50_1y = ma50[ma50.index >= one_year_ago]
    ma200_1y = ma200[ma200.index >= one_year_ago]
    rsi_1y = rsi[rsi.index >= one_year_ago]
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.68, 0.32],
        vertical_spacing=0.1
    )
    
    # Price chart
    fig.add_trace(
        go.Scatter(
            x=close_1y.index, y=close_1y,
            name="Price",
            line=dict(color="#a5b4fc", width=2.5),
            hovertemplate="<b>%{x|%d %b}</b><br>₹%{y:,.2f}<extra></extra>"
        ),
        row=1, col=1
    )
    
    # MA 50
    fig.add_trace(
        go.Scatter(
            x=ma50_1y.index, y=ma50_1y,
            name="MA 50",
            line=dict(color="#6ee7b7", width=1.5, dash="dash"),
            hovertemplate="MA 50: ₹%{y:,.2f}<extra></extra>"
        ),
        row=1, col=1
    )
    
    # MA 200
    fig.add_trace(
        go.Scatter(
            x=ma200_1y.index, y=ma200_1y,
            name="MA 200",
            line=dict(color="#fcd34d", width=1.5, dash="dash"),
            hovertemplate="MA 200: ₹%{y:,.2f}<extra></extra>"
        ),
        row=1, col=1
    )
    
    # RSI chart
    fig.add_trace(
        go.Scatter(
            x=rsi_1y.index, y=rsi_1y,
            name="RSI",
            line=dict(color="#ec4899", width=2),
            fill="tozeroy",
            fillcolor="rgba(236,72,153,0.1)",
            hovertemplate="RSI: %{y:.0f}<extra></extra>"
        ),
        row=2, col=1
    )
    
    # RSI reference lines
    fig.add_hline(70, line_dash="dash", line_color="rgba(252,165,165,0.5)", row=2, col=1, annotation_text="Overbought")
    fig.add_hline(30, line_dash="dash", line_color="rgba(110,231,183,0.5)", row=2, col=1, annotation_text="Oversold")
    fig.add_hline(50, line_dash="dot", line_color="rgba(165,180,252,0.3)", row=2, col=1)
    
    # Update layout
    fig.update_layout(
        height=620,
        hovermode="x unified",
        plot_bgcolor="rgba(30,27,75,0.2)" if colors.get("bg_primary") == "#0a0e27" else "rgba(248,249,250,0.5)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=colors.get("text_primary", "#e0e7ff"), size=12),
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(0,0,0,0.3)"),
        margin=dict(l=50, r=50, t=50, b=50),
    )
    
    # Y-axis labels
    fig.update_yaxes(title_text="Price (₹)", row=1, col=1, gridcolor="rgba(99,102,241,0.1)")
    fig.update_yaxes(title_text="RSI", row=2, col=1, gridcolor="rgba(99,102,241,0.1)")
    fig.update_xaxes(title_text="Date", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)


def display_news_item(news, sentiment_score, sentiment_label, sentiment_color, confidence):
    """
    Display single news article with sentiment analysis.
    
    Args:
        news: Dict with title, source, date
        sentiment_score: -10 to +10
        sentiment_label: 'BULLISH', 'BEARISH', 'NEUTRAL'
        sentiment_color: Hex color
        confidence: 0-1
    """
    title = escape(news["title"])
    source = escape(news["source"])
    
    html = f'''
    <div class="news-box" style="border-left-color: {sentiment_color};">
        <strong>{title}</strong>
        <br>
        <span class="small-note">
            📰 {source} | 
            Impact: <b>{sentiment_label}</b> ({sentiment_score:+.1f}) | 
            Confidence: {confidence*100:.0f}%
        </span>
    </div>
    '''
    
    st.markdown(html, unsafe_allow_html=True)


def display_news_list_multiselect(news_articles):
    """
    Multi-select interface for news articles.
    Returns indices of selected articles.
    
    Args:
        news_articles: List of news dicts
    
    Returns:
        List of selected indices or empty list
    """
    if not news_articles:
        st.info("No news articles available. Click 'Fetch Latest News' to load headlines.")
        return []
    
    # Create display labels
    news_labels = [
        f"{i+1}. {article['title'][:70]}..." 
        for i, article in enumerate(news_articles)
    ]
    
    selected_labels = st.multiselect(
        "Select headlines to analyze (multiple allowed)",
        options=range(len(news_articles)),
        format_func=lambda idx: news_labels[idx],
        default=[]
    )
    
    return selected_labels


def display_tooltip(key):
    """
    Display small tooltip icon with hover text.
    
    Args:
        key: Tooltip key from config.TOOLTIPS
    """
    if key in TOOLTIPS:
        st.caption(f"ℹ️ {TOOLTIPS[key]}")


def display_footer():
    """Display app footer"""
    colors = get_colors()
    
    html = f'''
    <div class="footer">
        <hr>
        <p>
            <strong>Nifty 500 Stock Impact Dashboard</strong><br>
            Educational tool only | Not investment advice | Data via Yahoo Finance + News APIs<br>
            {colors.get('text_secondary', '#a5b4fc')}
        </p>
    </div>
    '''
    
    st.markdown(html, unsafe_allow_html=True)
