"""
Utility functions for data processing, technical analysis, and news sentiment
"""

from io import StringIO
import pandas as pd
import numpy as np
import requests
import feedparser
import streamlit as st
from config import (
    REQUEST_HEADERS, REQUEST_TIMEOUT, INDEX_URL, FALLBACK_STOCKS,
    CACHE_INDEX_TTL, CACHE_PRICE_TTL, CACHE_NEWS_TTL,
    STOCK_STOPWORDS, TICKER_SUFFIXES, MAX_NEWS_ARTICLES,
    MA_PERIOD_SHORT, MA_PERIOD_LONG, RSI_PERIOD,
    RSI_OVERBOUGHT, RSI_OVERSOLD, RSI_OVERBOUGHT_EXTREME, RSI_OVERSOLD_EXTREME,
    BULLISH_SIGNALS, BEARISH_SIGNALS, SENTIMENT_MIN, SENTIMENT_MAX,
    VOLATILITY_PERIOD_DAYS, PRICE_HISTORY_YEARS,
)

# ============================================================================
# STOCK DATA LOADING
# ============================================================================

@st.cache_data(ttl=CACHE_INDEX_TTL, show_spinner=False)
def load_nifty500():
    """
    Load Nifty 500 constituents from official index.
    Falls back to hardcoded list if fetch fails.
    
    Returns:
        tuple: (DataFrame with stocks, bool indicating if live data loaded)
    """
    try:
        response = requests.get(INDEX_URL, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = pd.read_csv(StringIO(response.text))
        
        required = {"Company Name", "Symbol"}
        if not required.issubset(set(data.columns)):
            raise ValueError("Unexpected Nifty 500 CSV format")
        
        columns = ["Company Name", "Symbol"]
        if "Industry" in data.columns:
            columns.append("Industry")
        
        data = data[columns].dropna(subset=["Symbol"]).copy()
        data["Symbol"] = data["Symbol"].astype(str).str.strip().str.upper()
        data["Company Name"] = data["Company Name"].astype(str).str.strip()
        
        if "Industry" not in data.columns:
            data["Industry"] = ""
        
        return data.sort_values("Company Name").reset_index(drop=True), True
    
    except Exception as e:
        st.warning(f"Using fallback stock list (couldn't fetch live: {str(e)[:50]})")
        return pd.DataFrame(FALLBACK_STOCKS), False


# ============================================================================
# PRICE DATA FETCHING
# ============================================================================

@st.cache_data(ttl=CACHE_PRICE_TTL, show_spinner=False)
def fetch_stock_data(symbol):
    """
    Fetch 3-year daily OHLCV data from Yahoo Finance.
    Auto-detects best ticker (.NS or .BO).
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE')
    
    Returns:
        pd.DataFrame with columns [Open, High, Low, Close, Volume] or None
    """
    YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    
    # Try NSE first, then BSE
    for suffix in [TICKER_SUFFIXES["primary"], TICKER_SUFFIXES["secondary"]]:
        ticker = f"{symbol}{suffix}"
        try:
            response = requests.get(
                YAHOO_CHART_URL.format(ticker=requests.utils.quote(ticker, safe="")),
                params={"range": f"{PRICE_HISTORY_YEARS}y", "interval": "1d", "events": "history"},
                headers=REQUEST_HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            payload = response.json()
            
            result = payload["chart"]["result"][0]
            timestamps = result.get("timestamp") or []
            quote = result["indicators"]["quote"][0]
            
            if not timestamps or not quote.get("close"):
                continue
            
            data = pd.DataFrame(
                {
                    "Open": quote.get("open"),
                    "High": quote.get("high"),
                    "Low": quote.get("low"),
                    "Close": quote.get("close"),
                    "Volume": quote.get("volume"),
                },
                index=pd.to_datetime(timestamps, unit="s", utc=True)
                    .tz_convert("Asia/Kolkata")
                    .tz_localize(None),
            )
            
            data = data.apply(pd.to_numeric, errors="coerce").dropna(subset=["Close"])
            data["Volume"] = data["Volume"].fillna(0)
            
            if len(data) >= 200:
                return data
        
        except Exception:
            continue
    
    return None


# ============================================================================
# TECHNICAL INDICATORS
# ============================================================================

def wma(series, period):
    """
    Weighted Moving Average: Recent values weighted more heavily.
    
    Args:
        series: pd.Series of prices
        period: Window size
    
    Returns:
        pd.Series of WMA values
    """
    if series is None or len(series) < period:
        return None
    
    weights = np.arange(1, period + 1)
    return series.rolling(period).apply(
        lambda x: np.sum(weights * x) / np.sum(weights),
        raw=False
    )


def calculate_rsi(close, period=RSI_PERIOD):
    """
    Relative Strength Index: Momentum indicator (0-100).
    
    Args:
        close: pd.Series of closing prices
        period: RSI lookback period (default 14)
    
    Returns:
        pd.Series of RSI values
    """
    if close is None or len(close) < period:
        return None
    
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.fillna(50)


# ============================================================================
# NEWS FETCHING & FILTERING
# ============================================================================

def extract_stock_terms(symbol, company_name):
    """
    Extract keywords to identify stock-specific news.
    Filters out generic words like 'Ltd', 'Bank', etc.
    
    Args:
        symbol: Stock symbol
        company_name: Full company name
    
    Returns:
        set of lowercase terms
    """
    terms = {symbol.lower()}
    
    for raw_word in str(company_name).replace("&", " ").replace("-", " ").split():
        word = "".join(ch for ch in raw_word.lower() if ch.isalnum())
        if len(word) >= 4 and word not in STOCK_STOPWORDS:
            terms.add(word)
    
    return terms


def is_stock_specific(headline, symbol, company_name):
    """
    Check if headline mentions the specific stock.
    
    Args:
        headline: News headline text
        symbol: Stock symbol
        company_name: Company name
    
    Returns:
        bool
    """
    text = str(headline).lower()
    return any(term in text for term in extract_stock_terms(symbol, company_name))


@st.cache_data(ttl=CACHE_NEWS_TTL, show_spinner=False)
def fetch_stock_news(symbol, company_name):
    """
    Fetch stock-specific news from Yahoo Finance RSS feed.
    Filters by stock relevance, deduplicates, sorts by recency.
    
    Args:
        symbol: Stock symbol
        company_name: Company name
    
    Returns:
        list of dicts with keys: title, source, date
    """
    news = []
    seen = set()
    
    # Yahoo Finance RSS feed is more reliable than Google News
    feeds_to_try = [
        f"https://feeds.finance.yahoo.com/rss/2.0/headline?symbols={symbol}.NS",
        f"https://feeds.finance.yahoo.com/rss/2.0/headline?symbols={symbol}.BO",
    ]
    
    for feed_url in feeds_to_try:
        try:
            response = requests.get(feed_url, headers=REQUEST_HEADERS, timeout=15)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            for entry in feed.entries[:20]:
                title = str(entry.get("title", "")).strip()
                
                # Skip if not stock-specific
                if not title or not is_stock_specific(title, symbol, company_name):
                    continue
                
                # Deduplicate
                key = title.lower()
                if key in seen:
                    continue
                seen.add(key)
                
                # Extract source
                source = entry.get("source", {})
                source_name = (
                    source.get("title", "Yahoo Finance")
                    if hasattr(source, "get")
                    else "Yahoo Finance"
                )
                
                # Get publish date if available
                pub_date = entry.get("published", "")
                
                news.append({
                    "title": title,
                    "source": str(source_name),
                    "date": pub_date,
                })
        
        except Exception:
            continue
    
    # Return sorted by recency (newest first)
    return sorted(news, key=lambda x: x.get("date", ""), reverse=True)[:MAX_NEWS_ARTICLES]


# ============================================================================
# SENTIMENT ANALYSIS
# ============================================================================

def analyze_sentiment(headline):
    """
    Analyze news headline for bullish/bearish sentiment.
    Uses weighted keyword matching (not simple word counting).
    
    Args:
        headline: News headline text
    
    Returns:
        tuple: (score, label, color, confidence)
        - score: -10 to +10 range
        - label: 'BULLISH', 'BEARISH', or 'NEUTRAL'
        - color: Hex color code
        - confidence: 0.0 to 1.0 (based on signal strength)
    """
    text = str(headline).lower()
    
    score = 0
    signals_found = []
    
    # Check bullish signals
    for word, weight in BULLISH_SIGNALS.items():
        if word in text:
            score += weight
            signals_found.append((word, weight))
    
    # Check bearish signals
    for word, weight in BEARISH_SIGNALS.items():
        if word in text:
            score += weight
            signals_found.append((word, weight))
    
    # Normalize score
    score = max(SENTIMENT_MIN, min(SENTIMENT_MAX, score))
    
    # Calculate confidence: more signals = higher confidence
    confidence = min(1.0, len(signals_found) / 5.0)
    
    # Determine label and color
    if score >= 4:
        return score, "BULLISH", "#6ee7b7", confidence
    elif score <= -4:
        return score, "BEARISH", "#fca5a5", confidence
    else:
        return score, "NEUTRAL", "#fcd34d", confidence


# ============================================================================
# TECHNICAL SUMMARY
# ============================================================================

def calculate_technical_summary(data):
    """
    Comprehensive technical analysis: trend, momentum, volatility.
    
    Args:
        data: pd.DataFrame with OHLCV data
    
    Returns:
        dict with all metrics or None if insufficient data
    """
    if data is None or len(data) < 200:
        return None
    
    close = pd.to_numeric(data["Close"].squeeze(), errors="coerce").dropna()
    
    if len(close) < 200:
        return None
    
    # Calculate indicators
    ma50 = wma(close, MA_PERIOD_SHORT)
    ma200 = wma(close, MA_PERIOD_LONG)
    rsi = calculate_rsi(close, RSI_PERIOD)
    
    # Latest values
    latest_close = float(close.iloc[-1])
    previous_close = float(close.iloc[-2])
    latest_ma50 = float(ma50.iloc[-1])
    latest_ma200 = float(ma200.iloc[-1])
    latest_rsi = float(rsi.iloc[-1])
    
    # Daily change
    change = latest_close - previous_close
    change_pct = (change / previous_close * 100) if previous_close else 0
    
    # 1-year return
    one_year_ago = close.index[-1] - pd.Timedelta(days=365)
    one_year_data = close[close.index >= one_year_ago]
    
    if len(one_year_data) > 1:
        one_year_return = ((latest_close / float(one_year_data.iloc[0])) - 1) * 100
    else:
        one_year_return = 0
    
    # Volatility (20-day)
    recent = close.iloc[-VOLATILITY_PERIOD_DAYS:]
    volatility = (recent.std() / recent.mean() * 100) if len(recent) > 1 else 0
    
    # TECHNICAL SCORING (weighted, non-linear)
    score = 0
    reasons = []
    
    # Trend alignment (most important)
    price_above_ma50 = latest_close > latest_ma50
    price_above_ma200 = latest_close > latest_ma200
    ma50_above_ma200 = latest_ma50 > latest_ma200
    
    if price_above_ma50 and price_above_ma200 and ma50_above_ma200:
        score += 2.5
        reasons.append("🟢 Strong uptrend: Price > MA50 > MA200")
    elif price_above_ma200 and ma50_above_ma200:
        score += 1.5
        reasons.append("🟢 Moderate uptrend: Above 200-day MA")
    elif price_above_ma50:
        score += 0.5
        reasons.append("🟡 Short-term strength: Above 50-day MA")
    else:
        score -= 1.0
        reasons.append("🔴 Below key moving averages")
    
    # RSI momentum (non-linear)
    if latest_rsi > RSI_OVERBOUGHT_EXTREME:
        score -= 1.5
        reasons.append(f"🔴 Extremely overbought: RSI {latest_rsi:.0f}")
    elif latest_rsi > RSI_OVERBOUGHT:
        score -= 0.5
        reasons.append(f"🟡 Overbought: RSI {latest_rsi:.0f}")
    elif latest_rsi < RSI_OVERSOLD_EXTREME:
        score += 1.5
        reasons.append(f"🟢 Extremely oversold: RSI {latest_rsi:.0f} — reversal risk")
    elif latest_rsi < RSI_OVERSOLD:
        score += 0.5
        reasons.append(f"🟡 Oversold: RSI {latest_rsi:.0f}")
    else:
        reasons.append(f"🟡 RSI neutral: {latest_rsi:.0f}")
    
    # Volatility context
    if volatility > 3.5:
        reasons.append(f"⚠️ Very high volatility: {volatility:.1f}% — use tight stops")
    elif volatility > 2.5:
        reasons.append(f"⚠️ High volatility: {volatility:.1f}%")
    
    return {
        "close": latest_close,
        "previous_close": previous_close,
        "change": change,
        "change_pct": change_pct,
        "ma50": latest_ma50,
        "ma200": latest_ma200,
        "rsi": latest_rsi,
        "volatility": volatility,
        "one_year_return": one_year_return,
        "score": score,
        "reasons": reasons,
        "close_series": close,
        "ma50_series": ma50,
        "ma200_series": ma200,
        "rsi_series": rsi,
    }


# ============================================================================
# RECOMMENDATION LOGIC
# ============================================================================

def generate_recommendation(technical_data, selected_news_list):
    """
    Generate BUY/SELL/HOLD recommendation from technical + sentiment.
    
    Args:
        technical_data: dict from calculate_technical_summary()
        selected_news_list: list of dicts with 'title' key
    
    Returns:
        tuple: (recommendation, css_class, score, reasons)
    """
    if technical_data is None:
        return "HOLD", "hold", 0, ["Insufficient technical data available"]
    
    score = technical_data["score"]
    reasons = list(technical_data["reasons"])
    
    # Incorporate news sentiment if selected
    if selected_news_list:
        news_scores = []
        news_labels = []
        
        for news in selected_news_list:
            n_score, n_label, _, confidence = analyze_sentiment(news["title"])
            # Weight by confidence
            weighted_score = n_score * confidence
            news_scores.append(weighted_score)
            news_labels.append(n_label)
        
        # Average sentiment from selected news (dampened impact)
        avg_news_score = sum(news_scores) / len(news_scores)
        score += avg_news_score * 0.4  # News is 40% of final score
        
        # Summary
        label_summary = f"{news_labels[0]} ({'+'+ news_labels[0] if len(news_labels) > 1 else news_labels[0]})"
        reasons.append(f"📰 News consensus: {label_summary} ({len(selected_news_list)} articles)")
    else:
        reasons.append("📰 No news selected for analysis")
    
    # Final recommendation
    if score >= 3.0:
        return "BUY", "buy", score, reasons
    elif score <= -2.0:
        return "SELL", "sell", score, reasons
    else:
        return "HOLD", "hold", score, reasons
