"""
Professional Utils - Complete Enhanced Version
MACD, Bollinger Bands, ADX, Volume, Backtesting, Risk Metrics
"""

import pandas as pd
import numpy as np
import streamlit as st
import requests
import yfinance as yf
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

from config import *

# ============================================================================
# TECHNICAL INDICATORS - ADVANCED
# ============================================================================

def calculate_macd(close, fast=12, slow=26, signal=9):
    """Calculate MACD indicator"""
    try:
        ema_fast = close.ewm(span=fast).mean()
        ema_slow = close.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    except:
        return None, None, None

def calculate_bollinger_bands(close, period=20, std_dev=2):
    """Calculate Bollinger Bands"""
    try:
        sma = close.rolling(period).mean()
        std = close.rolling(period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower
    except:
        return None, None, None

def calculate_adx(high, low, close, period=14):
    """Calculate ADX - Trend Strength"""
    try:
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        
        # Directional Movement
        up = high.diff()
        down = -low.diff()
        
        pos_dm = up.where((up > down) & (up > 0), 0)
        neg_dm = down.where((down > up) & (down > 0), 0)
        
        pos_di = 100 * (pos_dm.rolling(period).mean() / atr)
        neg_di = 100 * (neg_dm.rolling(period).mean() / atr)
        
        di_diff = abs(pos_di - neg_di)
        di_sum = pos_di + neg_di
        dx = 100 * (di_diff / di_sum)
        adx = dx.rolling(period).mean()
        
        return adx, pos_di, neg_di
    except:
        return None, None, None

def calculate_obv(close, volume):
    """Calculate On-Balance Volume"""
    try:
        obv = pd.Series(0, index=close.index)
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv
    except:
        return None

def calculate_stochastic_rsi(close, period=14, k=3, d=3):
    """Calculate Stochastic RSI"""
    try:
        # First calculate RSI
        rsi = calculate_rsi(close, period)
        if rsi is None:
            return None, None, None
        
        # Then apply stochastic to RSI
        min_rsi = rsi.rolling(period).min()
        max_rsi = rsi.rolling(period).max()
        
        stoch_rsi = 100 * ((rsi - min_rsi) / (max_rsi - min_rsi))
        k_line = stoch_rsi.rolling(k).mean()
        d_line = k_line.rolling(d).mean()
        
        return stoch_rsi, k_line, d_line
    except:
        return None, None, None

def calculate_rsi(close, period=14):
    """Calculate RSI"""
    if close is None or len(close) < period:
        return None
    
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.fillna(50)

def calculate_wma(series, period):
    """Weighted Moving Average"""
    weights = np.arange(1, period + 1)
    return series.rolling(period).apply(lambda x: np.sum(weights * x) / np.sum(weights), raw=False)

# ============================================================================
# FUNDAMENTALS
# ============================================================================

@st.cache_data(ttl=CACHE_FUNDAMENTALS_TTL)
def fetch_fundamentals(symbol):
    """Fetch company fundamentals from yfinance"""
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        info = ticker.info
        
        fundamentals = {
            "pe_ratio": info.get("trailingPE", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "eps": info.get("trailingEps", "N/A"),
            "dividend_yield": info.get("dividendYield", "N/A"),
            "revenue": info.get("totalRevenue", "N/A"),
            "profit_margin": info.get("profitMargins", "N/A"),
            "debt_to_equity": info.get("debtToEquity", "N/A"),
            "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
        }
        
        return fundamentals
    except:
        return {k: "N/A" for k in ["pe_ratio", "market_cap", "eps", "dividend_yield", "revenue", "profit_margin", "debt_to_equity", "52_week_high", "52_week_low"]}

# ============================================================================
# BACKTESTING ENGINE
# ============================================================================

def backtest_signal(symbol, period_days=365):
    """Backtest the signal strategy"""
    try:
        stock_data = yf.download(f"{symbol}.NS", period=f"{period_days+100}d", progress=False)
        
        if stock_data.empty or len(stock_data) < 50:
            return None
        
        close = stock_data['Close']
        volume = stock_data['Volume']
        
        # Calculate indicators
        ma50 = close.rolling(50).mean()
        ma200 = close.rolling(200).mean()
        rsi = calculate_rsi(close)
        macd, signal, _ = calculate_macd(close)
        vol_avg = volume.rolling(20).mean()
        
        # Generate signals
        signals = pd.Series(0, index=close.index)
        
        for i in range(200, len(close)):
            buy_signal = (
                close.iloc[i] > ma200.iloc[i] and
                rsi.iloc[i] > 40 and
                rsi.iloc[i] < 70 and
                macd.iloc[i] > signal.iloc[i] and
                volume.iloc[i] > vol_avg.iloc[i]
            )
            
            if buy_signal:
                signals.iloc[i] = 1
        
        # Calculate returns
        returns = close.pct_change()
        signal_returns = returns * signals.shift(1)
        
        trades = signals[signals != 0]
        if len(trades) == 0:
            return None
        
        # Metrics
        winning_trades = sum(signal_returns > 0)
        total_trades = len(trades)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        cumulative_return = (1 + signal_returns).cumprod() - 1
        max_return = cumulative_return.max()
        max_drawdown = (cumulative_return.cummax() - cumulative_return).max()
        
        # Sharpe ratio
        sharpe = signal_returns.mean() / signal_returns.std() * np.sqrt(252) if signal_returns.std() > 0 else 0
        
        return {
            "win_rate": win_rate,
            "total_trades": total_trades,
            "cumulative_return": cumulative_return.iloc[-1] * 100,
            "max_drawdown": max_drawdown * 100,
            "sharpe_ratio": sharpe,
            "avg_daily_return": signal_returns.mean() * 100,
        }
    
    except:
        return None

# ============================================================================
# RISK METRICS
# ============================================================================

def calculate_risk_metrics(stock_data, symbol):
    """Calculate Sharpe, Beta, Volatility, Drawdown"""
    try:
        close = stock_data['Close']
        returns = close.pct_change().dropna()
        
        # Volatility (annualized)
        volatility = returns.std() * np.sqrt(252) * 100
        
        # Sharpe Ratio (assuming 6% risk-free rate)
        risk_free = 0.06
        sharpe = (returns.mean() * 252 - risk_free) / (returns.std() * np.sqrt(252))
        
        # Maximum Drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # Beta (vs Nifty 50 - simplified)
        nifty_data = yf.download("^NSEI", start=close.index[0], end=close.index[-1], progress=False)
        nifty_returns = nifty_data['Close'].pct_change().dropna()
        
        # Align returns
        common_index = returns.index.intersection(nifty_returns.index)
        stock_returns = returns[common_index]
        market_returns = nifty_returns[common_index]
        
        covariance = np.cov(stock_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        beta = covariance / market_variance if market_variance > 0 else 1
        
        return {
            "volatility": volatility,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_drawdown,
            "beta": beta,
        }
    
    except:
        return {
            "volatility": "N/A",
            "sharpe_ratio": "N/A",
            "max_drawdown": "N/A",
            "beta": "N/A",
        }

# ============================================================================
# PROFESSIONAL SIGNAL GENERATION
# ============================================================================

def calculate_professional_signal(technical_data, selected_news):
    """Generate signal with confidence scoring"""
    
    score = 0
    confirmations = []
    
    close = technical_data["close"]
    ma50 = technical_data["ma50"]
    ma200 = technical_data["ma200"]
    rsi = technical_data["rsi"]
    
    # Trend confirmation
    if close.iloc[-1] > ma200.iloc[-1]:
        score += 1.5
        confirmations.append("✓ Price above MA200 (uptrend)")
    elif close.iloc[-1] < ma50.iloc[-1]:
        score -= 1.5
        confirmations.append("✗ Price below MA50 (downtrend)")
    
    # Momentum confirmation
    if 40 < rsi.iloc[-1] < 70:
        score += 1
        confirmations.append("✓ RSI in healthy range (40-70)")
    elif rsi.iloc[-1] > 70:
        score -= 1
        confirmations.append("⚠ RSI overbought (>70)")
    elif rsi.iloc[-1] < 30:
        score -= 1
        confirmations.append("⚠ RSI oversold (<30)")
    
    # MACD confirmation
    if "macd" in technical_data:
        macd = technical_data["macd"]
        signal = technical_data["macd_signal"]
        if macd.iloc[-1] > signal.iloc[-1]:
            score += 1
            confirmations.append("✓ MACD above signal (positive momentum)")
        else:
            score -= 0.5
            confirmations.append("⚠ MACD below signal")
    
    # Volume confirmation
    if "volume_trend" in technical_data:
        if technical_data["volume_trend"] > 1:
            score += 1
            confirmations.append("✓ Volume increasing (strength)")
    
    # Bollinger Bands
    if "bb_upper" in technical_data:
        if close.iloc[-1] < technical_data["bb_middle"].iloc[-1]:
            score += 0.5
            confirmations.append("✓ Price near middle/lower band (entry zone)")
    
    # News sentiment
    if selected_news:
        sentiment_scores = [n.get("sentiment", 0) for n in selected_news]
        avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0
        if avg_sentiment > 0.2:
            score += 0.5
            confirmations.append("✓ Positive news sentiment")
        elif avg_sentiment < -0.2:
            score -= 0.5
            confirmations.append("✗ Negative news sentiment")
    
    # Calculate confidence (0-100%)
    confidence = max(0, min(100, (score + 3) / 6 * 100))
    
    # Determine signal
    if score >= 3:
        signal = "🟢 STRONG BUY"
        color = "#34d399"
    elif score >= 1.5:
        signal = "🟡 BUY"
        color = "#fbbf24"
    elif score <= -2:
        signal = "🔴 STRONG SELL"
        color = "#f87171"
    elif score <= -0.5:
        signal = "🟠 SELL"
        color = "#fb923c"
    else:
        signal = "⚪ HOLD"
        color = "#9ca3af"
    
    return {
        "signal": signal,
        "score": score,
        "confidence": confidence,
        "confirmations": confirmations,
        "color": color,
    }

# ============================================================================
# EXISTING FUNCTIONS (Keep from original)
# ============================================================================

@st.cache_data(ttl=CACHE_INDEX_TTL)
def load_nifty500():
    """Load Nifty 500 list"""
    try:
        stocks = pd.read_csv(INDEX_URL)
        return stocks, True
    except:
        return pd.DataFrame(FALLBACK_STOCKS), False

@st.cache_data(ttl=CACHE_PRICE_TTL)
def fetch_stock_data(symbol):
    """Fetch stock data from Yahoo Finance"""
    try:
        data = yf.download(f"{symbol}.NS", period="3y", progress=False)
        if data.empty:
            data = yf.download(f"{symbol}.BO", period="3y", progress=False)
        
        if len(data) < 200:
            return None
        
        return data
    except:
        return None

def calculate_technical_summary(data):
    """Calculate all technical indicators"""
    if data is None or len(data) < 200:
        return None
    
    close = data['Close']
    volume = data['Volume']
    high = data['High']
    low = data['Low']
    
    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()
    rsi = calculate_rsi(close)
    macd, macd_signal, macd_hist = calculate_macd(close)
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(close)
    adx, pos_di, neg_di = calculate_adx(high, low, close)
    obv = calculate_obv(close, volume)
    stoch_rsi, k_line, d_line = calculate_stochastic_rsi(close)
    
    vol_avg = volume.rolling(20).mean()
    vol_trend = volume.iloc[-1] / vol_avg.iloc[-1] if vol_avg.iloc[-1] > 0 else 1
    
    change = ((close.iloc[-1] - close.iloc[-250]) / close.iloc[-250] * 100) if len(close) > 250 else 0
    volatility = close.pct_change().std() * np.sqrt(252) * 100
    one_year_return = ((close.iloc[-1] - close.iloc[-252]) / close.iloc[-252] * 100) if len(close) > 252 else 0
    
    return {
        "close": close.iloc[-1],
        "change": change,
        "volatility": volatility,
        "one_year_return": one_year_return,
        "ma50": ma50.iloc[-1],
        "ma200": ma200.iloc[-1],
        "rsi": rsi.iloc[-1],
        "macd": macd.iloc[-1] if macd is not None else None,
        "macd_signal": macd_signal.iloc[-1] if macd_signal is not None else None,
        "bb_upper": bb_upper.iloc[-1],
        "bb_middle": bb_middle.iloc[-1],
        "bb_lower": bb_lower.iloc[-1],
        "adx": adx.iloc[-1] if adx is not None else None,
        "obv": obv.iloc[-1] if obv is not None else None,
        "stoch_rsi": stoch_rsi.iloc[-1] if stoch_rsi is not None else None,
        "volume_trend": vol_trend,
        "close_series": close,
        "ma50_series": ma50,
        "ma200_series": ma200,
        "rsi_series": rsi,
        "macd_series": macd,
        "macd_signal_series": macd_signal,
        "volume_series": volume,
    }
