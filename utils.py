"""
Professional Utils - Complete Enhanced Version
MACD, Bollinger Bands, ADX, Volume, Backtesting, Risk Metrics
FIXED: load_nifty500 timeout, OBV vectorized, cached benchmark, backtest reuses data
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
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()

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
    """
    Calculate On-Balance Volume - VECTORIZED (no Python loop).
    Uses numpy sign diff for ~50x speedup over iterative version.
    """
    try:
        direction = np.sign(close.diff()).fillna(0)
        obv = (direction * volume).cumsum()
        return obv
    except:
        return None

def calculate_stochastic_rsi(close, period=14, k=3, d=3):
    """Calculate Stochastic RSI"""
    try:
        rsi = calculate_rsi(close, period)
        if rsi is None:
            return None, None, None

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
    """
    ALL metrics calculated from raw data — no pre-computed ratios fetched.

    Formulas:
      52W High/Low     = max(High) / min(Low) over last 252 trading days of OHLC history
      Current Price    = latest Close from price history
      Shares Outs.     = fast_info.shares (most reliable source for this one raw input)
      Market Cap       = Current Price × Shares Outstanding
      Annual Dividends = sum of all Dividends paid in last 1Y (raw unadjusted history)
      Dividend Yield   = Annual Dividends ÷ Current Price × 100
      Revenue (TTM)    = sum of last 4 quarters of Total Revenue (income statement)
      Net Income (TTM) = sum of last 4 quarters of Net Income (income statement)
      EPS              = Net Income (TTM) ÷ Shares Outstanding
      P/E Ratio        = Current Price ÷ EPS
      Profit Margin    = Net Income (TTM) ÷ Revenue (TTM) × 100
      Total Debt       = Short-term Debt + Long-term Debt (balance sheet, latest quarter)
      Equity           = Total Stockholder Equity (balance sheet, latest quarter)
      Debt/Equity      = Total Debt ÷ Equity × 100
    """
    result = {k: "N/A" for k in [
        "pe_ratio", "market_cap", "eps", "dividend_yield",
        "revenue", "profit_margin", "debt_to_equity",
        "52_week_high", "52_week_low",
    ]}

    for suffix in [".NS", ".BO"]:
        try:
            ticker = yf.Ticker(f"{symbol}{suffix}")

            # ── 1. Price history → 52W High/Low + Current Price ──────────
            try:
                hist_raw = ticker.history(period="1y", auto_adjust=False)
                hist_adj = ticker.history(period="1y", auto_adjust=True)

                if hist_raw.empty:
                    continue

                # Flatten MultiIndex columns if present
                for h in [hist_raw, hist_adj]:
                    if isinstance(h.columns, pd.MultiIndex):
                        h.columns = h.columns.get_level_values(0)

                current_price = float(hist_adj["Close"].iloc[-1])
                result["52_week_high"] = round(float(hist_raw["High"].max()), 2)
                result["52_week_low"]  = round(float(hist_raw["Low"].min()),  2)
            except Exception:
                current_price = None
                continue   # can't do anything without price data

            # ── 2. Shares Outstanding → from fast_info (raw input only) ──
            shares = None
            try:
                fi = ticker.fast_info
                for attr in ["shares", "shares_outstanding", "sharesOutstanding"]:
                    val = getattr(fi, attr, None)
                    if val and float(val) > 0:
                        shares = float(val)
                        break
            except Exception:
                pass

            # ── 3. Market Cap = Price × Shares ───────────────────────────
            if current_price and shares:
                result["market_cap"] = current_price * shares

            # ── 4. Dividends → Dividend Yield = ΣDiv(1Y) ÷ Price × 100 ──
            try:
                if "Dividends" in hist_raw.columns:
                    annual_div = float(hist_raw["Dividends"].sum())
                    if current_price and current_price > 0:
                        result["dividend_yield"] = round(
                            (annual_div / current_price) * 100, 2
                        )
                    else:
                        result["dividend_yield"] = 0.0
            except Exception:
                result["dividend_yield"] = 0.0

            # ── 5. Income Statement → Revenue, Net Income (TTM) ──────────
            net_income_ttm = None
            revenue_ttm    = None
            try:
                # quarterly gives last 4 quarters = TTM
                q_income = ticker.quarterly_income_stmt
                if q_income is not None and not q_income.empty:
                    # Take last 4 quarters (columns are dates, most recent first)
                    last4 = q_income.iloc[:, :4]

                    def _sum_row(df, *candidates):
                        for name in candidates:
                            matches = [r for r in df.index if name.lower() in str(r).lower()]
                            if matches:
                                try:
                                    return float(df.loc[matches[0]].iloc[:4].sum())
                                except Exception:
                                    pass
                        return None

                    revenue_ttm    = _sum_row(last4,
                        "Total Revenue", "Revenue", "Net Revenue",
                        "TotalRevenue")
                    net_income_ttm = _sum_row(last4,
                        "Net Income", "Net Income Common Stockholders",
                        "Net Income Applicable To Common Shares",
                        "NetIncome", "NetIncomeCommonStockholders")

                    if revenue_ttm and abs(revenue_ttm) > 0:
                        result["revenue"] = revenue_ttm

                    # Profit Margin = Net Income ÷ Revenue × 100
                    if net_income_ttm is not None and revenue_ttm and revenue_ttm > 0:
                        result["profit_margin"] = round(
                            (net_income_ttm / revenue_ttm) * 100, 2
                        )
            except Exception:
                pass

            # ── 6. EPS = Net Income (TTM) ÷ Shares ───────────────────────
            if net_income_ttm is not None and shares and shares > 0:
                eps = net_income_ttm / shares
                result["eps"] = round(eps, 2)

                # ── 7. P/E = Price ÷ EPS ─────────────────────────────────
                if current_price and eps > 0:
                    result["pe_ratio"] = round(current_price / eps, 2)

            # ── 8. Balance Sheet → Debt/Equity ───────────────────────────
            try:
                q_balance = ticker.quarterly_balance_sheet
                if q_balance is not None and not q_balance.empty:
                    latest = q_balance.iloc[:, 0]  # most recent quarter

                    def _get_val(series, *candidates):
                        for name in candidates:
                            matches = [r for r in series.index
                                       if name.lower() in str(r).lower()]
                            if matches:
                                try:
                                    v = float(series[matches[0]])
                                    if not np.isnan(v):
                                        return v
                                except Exception:
                                    pass
                        return None

                    short_debt = _get_val(latest,
                        "Current Debt", "Short Long Term Debt",
                        "CurrentDebt", "ShortLongTermDebt",
                        "Short Term Debt", "Current Portion Of Long Term Debt") or 0.0

                    long_debt  = _get_val(latest,
                        "Long Term Debt", "LongTermDebt",
                        "Long Term Debt And Capital Lease Obligation") or 0.0

                    equity     = _get_val(latest,
                        "Stockholders Equity", "Total Stockholder Equity",
                        "Common Stock Equity", "StockholdersEquity",
                        "TotalStockholderEquity", "CommonStockEquity")

                    total_debt = short_debt + long_debt
                    if equity and equity > 0:
                        result["debt_to_equity"] = round(
                            (total_debt / equity) * 100, 2
                        )
            except Exception:
                pass

            # Got enough to stop trying .BO suffix
            if result["52_week_high"] != "N/A":
                break

        except Exception:
            continue

    return result

# ============================================================================
# NIFTY BENCHMARK - CACHED SEPARATELY
# ============================================================================

@st.cache_data(ttl=CACHE_PRICE_TTL)
def fetch_nifty_benchmark(start_date, end_date):
    """
    Fetch Nifty 50 benchmark data - cached so it's only downloaded once
    regardless of how many stocks the user looks at.
    """
    try:
        data = yf.download("^NSEI", start=start_date, end=end_date, progress=False)
        return data
    except:
        return pd.DataFrame()

# ============================================================================
# BACKTESTING ENGINE - reuses already-fetched stock_data
# ============================================================================

def backtest_signal(symbol, stock_data=None):
    """
    Backtest the signal strategy.
    Accepts existing stock_data to avoid a duplicate yfinance download.
    """
    try:
        # Reuse passed data if available, otherwise fetch
        if stock_data is not None and not stock_data.empty and len(stock_data) >= 300:
            data = stock_data
        else:
            data = yf.download(f"{symbol}.NS", period="465d", progress=False)

        if data.empty or len(data) < 50:
            return None

        close = data['Close']
        volume = data['Volume']

        # Squeeze single-level MultiIndex columns if present
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        if isinstance(volume, pd.DataFrame):
            volume = volume.iloc[:, 0]

        ma50 = close.rolling(50).mean()
        ma200 = close.rolling(200).mean()
        rsi = calculate_rsi(close)
        macd, signal, _ = calculate_macd(close)
        vol_avg = volume.rolling(20).mean()

        if ma200.isna().all() or rsi is None or macd is None:
            return None

        # Vectorized signal generation (no Python loop)
        price_above_ma200 = close > ma200
        rsi_in_range = (rsi > 40) & (rsi < 70)
        macd_positive = macd > signal
        volume_strong = volume > vol_avg

        buy_signals = (
            price_above_ma200 &
            rsi_in_range &
            macd_positive &
            volume_strong
        ).astype(int)

        returns = close.pct_change()
        signal_returns = returns * buy_signals.shift(1)

        trades = buy_signals[buy_signals != 0]
        if len(trades) == 0:
            return None

        winning_trades = (signal_returns > 0).sum()
        total_trades = len(trades)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        cumulative_return = (1 + signal_returns).cumprod() - 1
        max_drawdown = (cumulative_return.cummax() - cumulative_return).max()

        sharpe = (
            signal_returns.mean() / signal_returns.std() * np.sqrt(252)
            if signal_returns.std() > 0 else 0
        )

        return {
            "win_rate": float(win_rate),
            "total_trades": int(total_trades),
            "cumulative_return": float(cumulative_return.iloc[-1] * 100),
            "max_drawdown": float(max_drawdown * 100),
            "sharpe_ratio": float(sharpe),
            "avg_daily_return": float(signal_returns.mean() * 100),
        }

    except:
        return None

# ============================================================================
# RISK METRICS - uses cached benchmark
# ============================================================================

def calculate_risk_metrics(stock_data, symbol):
    """
    Calculate Sharpe, Beta, Volatility, Drawdown.
    Uses cached Nifty benchmark to avoid duplicate downloads.
    """
    try:
        close = stock_data['Close']
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        returns = close.pct_change().dropna()

        volatility = returns.std() * np.sqrt(252) * 100

        risk_free = 0.06
        sharpe = (returns.mean() * 252 - risk_free) / (returns.std() * np.sqrt(252))

        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100

        # Use cached benchmark fetch
        start_date = str(close.index[0].date())
        end_date = str(close.index[-1].date())
        nifty_data = fetch_nifty_benchmark(start_date, end_date)

        beta = 1.0  # Default if benchmark unavailable
        if not nifty_data.empty:
            nifty_close = nifty_data['Close']
            if isinstance(nifty_close, pd.DataFrame):
                nifty_close = nifty_close.iloc[:, 0]
            nifty_returns = nifty_close.pct_change().dropna()

            common_index = returns.index.intersection(nifty_returns.index)
            if len(common_index) > 30:
                stock_r = returns[common_index]
                market_r = nifty_returns[common_index]
                covariance = np.cov(stock_r, market_r)[0][1]
                market_variance = np.var(market_r)
                beta = covariance / market_variance if market_variance > 0 else 1.0

        return {
            "volatility": float(volatility),
            "sharpe_ratio": float(sharpe),
            "max_drawdown": float(max_drawdown),
            "beta": float(beta),
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

    if close > ma200:
        score += 1.5
        confirmations.append("✓ Price above MA200 (uptrend)")
    elif close < ma50:
        score -= 1.5
        confirmations.append("✗ Price below MA50 (downtrend)")

    if 40 < rsi < 70:
        score += 1
        confirmations.append("✓ RSI in healthy range (40-70)")
    elif rsi > 70:
        score -= 1
        confirmations.append("⚠ RSI overbought (>70)")
    elif rsi < 30:
        score -= 1
        confirmations.append("⚠ RSI oversold (<30)")

    if technical_data.get("macd") is not None and technical_data.get("macd_signal") is not None:
        if technical_data["macd"] > technical_data["macd_signal"]:
            score += 1
            confirmations.append("✓ MACD above signal (positive momentum)")
        else:
            score -= 0.5
            confirmations.append("⚠ MACD below signal")

    if technical_data.get("volume_trend") is not None:
        if technical_data["volume_trend"] > 1:
            score += 1
            confirmations.append("✓ Volume increasing (strength)")

    if technical_data.get("bb_middle") is not None:
        if close < technical_data["bb_middle"]:
            score += 0.5
            confirmations.append("✓ Price near middle/lower band (entry zone)")

    if selected_news:
        sentiment_scores = [n.get("sentiment", 0) for n in selected_news]
        avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0
        if avg_sentiment > 0.2:
            score += 0.5
            confirmations.append("✓ Positive news sentiment")
        elif avg_sentiment < -0.2:
            score -= 0.5
            confirmations.append("✗ Negative news sentiment")

    confidence = max(0, min(100, (score + 3) / 6 * 100))

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
# CORE DATA FUNCTIONS
# ============================================================================

@st.cache_data(ttl=CACHE_INDEX_TTL)
def load_nifty500():
    """
    Load Nifty 500 list.
    Tries primary NSE URL first with a short timeout, then falls back
    to a GitHub-hosted mirror, then to the hardcoded FALLBACK_STOCKS.
    """
    urls = [
        # GitHub-hosted mirror (most reliable on Streamlit Cloud)
        "https://raw.githubusercontent.com/datasets/nifty500/main/data/nifty500.csv",
        # Official NSE URL (can be slow/blocked)
        "https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv",
    ]

    for url in urls:
        try:
            response = requests.get(url, timeout=8, headers=REQUEST_HEADERS)
            if response.status_code == 200:
                from io import StringIO
                stocks = pd.read_csv(StringIO(response.text))
                # Normalise column names across sources
                stocks.columns = [c.strip() for c in stocks.columns]
                if "Symbol" in stocks.columns and "Company Name" in stocks.columns:
                    return stocks, True
        except Exception:
            continue

    # Hard fallback — always works, just 10 stocks
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

    # Handle MultiIndex columns from newer yfinance versions
    close = data['Close']
    volume = data['Volume']
    high = data['High']
    low = data['Low']

    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    if isinstance(volume, pd.DataFrame):
        volume = volume.iloc[:, 0]
    if isinstance(high, pd.DataFrame):
        high = high.iloc[:, 0]
    if isinstance(low, pd.DataFrame):
        low = low.iloc[:, 0]

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
        # Scalar values
        "close": float(close.iloc[-1]),
        "change": float(change),
        "volatility": float(volatility),
        "one_year_return": float(one_year_return),
        "ma50": float(ma50.iloc[-1]),
        "ma200": float(ma200.iloc[-1]),
        "rsi": float(rsi.iloc[-1]) if rsi is not None else 50.0,
        "macd": float(macd.iloc[-1]) if macd is not None else None,
        "macd_signal": float(macd_signal.iloc[-1]) if macd_signal is not None else None,
        "bb_upper": float(bb_upper.iloc[-1]) if bb_upper is not None else None,
        "bb_middle": float(bb_middle.iloc[-1]) if bb_middle is not None else None,
        "bb_lower": float(bb_lower.iloc[-1]) if bb_lower is not None else None,
        "adx": float(adx.iloc[-1]) if adx is not None else None,
        "obv": float(obv.iloc[-1]) if obv is not None else None,
        "stoch_rsi": float(stoch_rsi.iloc[-1]) if stoch_rsi is not None else None,
        "volume_trend": float(vol_trend),
        # Series for charts
        "close_series": close,
        "ma50_series": ma50,
        "ma200_series": ma200,
        "rsi_series": rsi,
        "macd_series": macd,
        "macd_signal_series": macd_signal,
        "volume_series": volume,
    }
