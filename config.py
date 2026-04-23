"""
Configuration file for Nifty 500 Stock Impact Dashboard
Centralized settings for styling, thresholds, and analysis parameters
"""

# ============================================================================
# THEME CONFIGURATION
# ============================================================================

THEMES = {
    "dark": {
        "bg_primary": "#0a0e27",
        "bg_secondary": "#0f1629",
        "bg_card": "rgba(30,27,75,0.6)",
        "border_color": "rgba(99,102,241,0.3)",
        "text_primary": "#e0e7ff",
        "text_secondary": "#a5b4fc",
        "accent": "#a78bfa",
        "green": "#6ee7b7",
        "red": "#fca5a5",
        "yellow": "#fcd34d",
    },
    "light": {
        "bg_primary": "#ffffff",
        "bg_secondary": "#f8f9fa",
        "bg_card": "rgba(255,255,255,0.95)",
        "border_color": "rgba(99,102,241,0.2)",
        "text_primary": "#1f2937",
        "text_secondary": "#6b7280",
        "accent": "#7c3aed",
        "green": "#059669",
        "red": "#dc2626",
        "yellow": "#d97706",
    },
}

# ============================================================================
# TECHNICAL ANALYSIS PARAMETERS
# ============================================================================

# Moving averages
MA_PERIOD_SHORT = 50
MA_PERIOD_LONG = 200

# RSI settings
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERBOUGHT_EXTREME = 80
RSI_OVERSOLD = 30
RSI_OVERSOLD_EXTREME = 20

# Volatility thresholds (%)
VOLATILITY_HIGH = 3.0
VOLATILITY_MEDIUM = 2.0

# Technical score thresholds for recommendation
SCORE_BUY = 3.0
SCORE_SELL = -2.0

# ============================================================================
# SENTIMENT ANALYSIS WEIGHTS
# ============================================================================

BULLISH_SIGNALS = {
    "beats": 2.0,
    "profit": 2.0,
    "growth": 1.5,
    "surge": 2.0,
    "rally": 2.0,
    "upgrade": 2.0,
    "approval": 2.0,
    "expansion": 2.0,
    "record": 1.5,
    "launches": 1.0,
    "wins": 2.0,
    "raises": 1.5,
    "buyback": 1.5,
    "strong": 1.0,
    "order": 1.0,
}

BEARISH_SIGNALS = {
    "misses": -2.0,
    "loss": -2.0,
    "fraud": -3.0,
    "probe": -2.0,
    "downgrade": -2.0,
    "penalty": -2.0,
    "resigns": -1.5,
    "crash": -3.0,
    "weak": -1.0,
    "falls": -1.5,
    "default": -3.0,
    "debt": -1.0,
    "selloff": -2.0,
    "drop": -1.5,
    "cuts": -1.0,
}

# Sentiment score normalization
SENTIMENT_MIN = -10
SENTIMENT_MAX = 10

# ============================================================================
# DATA FETCHING PARAMETERS
# ============================================================================

# Cache TTL in seconds
CACHE_INDEX_TTL = 24 * 60 * 60  # 24 hours for stock list
CACHE_PRICE_TTL = 15 * 60       # 15 minutes for price data
CACHE_NEWS_TTL = 5 * 60         # 5 minutes for news

# Historical data
PRICE_HISTORY_YEARS = 3
RSI_LOOKBACK_DAYS = 200
VOLATILITY_PERIOD_DAYS = 20

# News
MAX_NEWS_ARTICLES = 15
MIN_HEADLINE_LENGTH = 10

# ============================================================================
# TICKER CONFIGURATIONS
# ============================================================================

TICKER_SUFFIXES = {
    "primary": ".NS",      # NSE (National Stock Exchange)
    "secondary": ".BO",    # BSE (Bombay Stock Exchange)
}

# Stock stopwords for filtering (removing noise from company names)
STOCK_STOPWORDS = {
    "ltd", "limited", "india", "indian", "industries", "industry",
    "company", "corporation", "corp", "services", "service",
    "bank", "finance", "financial", "holdings", "holding",
    "the", "and", "of", "nse", "bse", "inc", "pvt",
}

# ============================================================================
# API & REQUEST SETTINGS
# ============================================================================

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/csv,application/rss+xml,application/xml,text/xml,application/json,*/*",
}

REQUEST_TIMEOUT = 20  # seconds

# ============================================================================
# NIFTY 500 INDEX URL
# ============================================================================

INDEX_URL = "https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv"

# Fallback stocks for when live data unavailable
FALLBACK_STOCKS = [
    {"Company Name": "Reliance Industries Ltd.", "Symbol": "RELIANCE", "Industry": "Oil Gas & Consumable Fuels"},
    {"Company Name": "HDFC Bank Ltd.", "Symbol": "HDFCBANK", "Industry": "Financial Services"},
    {"Company Name": "ICICI Bank Ltd.", "Symbol": "ICICIBANK", "Industry": "Financial Services"},
    {"Company Name": "Infosys Ltd.", "Symbol": "INFY", "Industry": "Information Technology"},
    {"Company Name": "Tata Consultancy Services Ltd.", "Symbol": "TCS", "Industry": "Information Technology"},
    {"Company Name": "Larsen & Toubro Ltd.", "Symbol": "LT", "Industry": "Construction"},
    {"Company Name": "State Bank of India", "Symbol": "SBIN", "Industry": "Financial Services"},
    {"Company Name": "Bharti Airtel Ltd.", "Symbol": "BHARTIARTL", "Industry": "Telecommunication"},
    {"Company Name": "ITC Ltd.", "Symbol": "ITC", "Industry": "Fast Moving Consumer Goods"},
    {"Company Name": "Axis Bank Ltd.", "Symbol": "AXISBANK", "Industry": "Financial Services"},
]

# ============================================================================
# TOOLTIP & HELP TEXT (For mixed audience explanation)
# ============================================================================

TOOLTIPS = {
    "MA50": "50-day Moving Average: Average closing price over 50 days. Shows short-term trend.",
    "MA200": "200-day Moving Average: Average closing price over 200 days. Shows long-term trend.",
    "RSI": "Relative Strength Index (0-100): Measures momentum. Above 70 = overbought, below 30 = oversold.",
    "WMA": "Weighted Moving Average: Recent prices weighted higher than older prices.",
    "VOLATILITY": "Price movement range. Higher % = wilder swings = more risk.",
    "ONE_YEAR_RETURN": "Total gain/loss over 12 months (%). Negative = stock down.",
    "SENTIMENT": "AI score based on positive/negative keywords in news. Not financial advice.",
    "TECHNICAL_SCORE": "Composite score from trend + momentum. Range: -4 to +4.",
}

# ============================================================================
# RECOMMENDATION THRESHOLDS
# ============================================================================

RECOMMENDATION_RULES = {
    "BUY": {
        "score_threshold": 3.0,
        "color": "green",
        "description": "Technical factors + news alignment suggest upside",
    },
    "SELL": {
        "score_threshold": -2.0,
        "color": "red",
        "description": "Technical weakness + negative news indicate downside risk",
    },
    "HOLD": {
        "score_threshold": None,  # Default for mid-range
        "color": "yellow",
        "description": "Balanced signal or insufficient data",
    },
}
