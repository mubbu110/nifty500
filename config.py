# Professional Configuration - Enhanced

# ============================================================================
# API KEYS (Free Tier - Get from https://finnhub.io)
# ============================================================================

FINNHUB_API_KEY = "YOUR_FINNHUB_KEY"  # Get free at finnhub.io

# ============================================================================
# THEME CONFIGURATION
# ============================================================================

THEMES = {
    "dark": {
        "bg_primary": "#0a0e27",
        "bg_secondary": "#0f1629",
        "bg_card": "rgba(20, 25, 60, 0.8)",
        "border_color": "rgba(139, 92, 246, 0.5)",
        "text_primary": "#f0f4ff",
        "text_secondary": "#c7d2fe",
        "accent": "#c084fc",
        "green": "#34d399",
        "red": "#f87171",
        "yellow": "#fbbf24",
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

# Moving Averages
MA_PERIOD_SHORT = 50
MA_PERIOD_LONG = 200

# RSI
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# MACD
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Bollinger Bands
BB_PERIOD = 20
BB_STD = 2

# Stochastic RSI
STOCH_RSI_PERIOD = 14
STOCH_RSI_K = 3
STOCH_RSI_D = 3

# ADX (Trend Strength)
ADX_PERIOD = 14
ADX_STRONG = 25
ADX_VERY_STRONG = 40

# Volume
VOLUME_PERIOD = 20

# ============================================================================
# BACKTESTING PARAMETERS
# ============================================================================

BACKTEST_PERIODS = [
    ("1 Month", 30),
    ("3 Months", 90),
    ("6 Months", 180),
    ("1 Year", 365),
]

BACKTEST_INITIAL_CAPITAL = 100000  # Rs
BACKTEST_POSITION_SIZE = 0.95  # Use 95% of capital per trade

# ============================================================================
# SIGNAL CONFIRMATION RULES
# ============================================================================

# BUY Signal Requirements (must meet ALL)
BUY_REQUIREMENTS = {
    "trend": "Price above MA200",  # Long-term trend
    "momentum": "RSI > 40",  # Not oversold
    "macd": "MACD above signal",  # Momentum positive
    "volume": "Volume above 20-day avg",  # Strength confirmation
    "bollinger": "Price near lower band OR above middle",  # Entry zone
}

# SELL Signal Requirements (must meet ANY 2)
SELL_REQUIREMENTS = {
    "trend": "Price below MA50",
    "momentum": "RSI > 70",
    "macd": "MACD below signal",
    "volume": "High volume on down days",
}

# ============================================================================
# RISK MANAGEMENT
# ============================================================================

RISK_PER_TRADE = 0.02  # Risk 2% per trade
REWARD_TO_RISK_MIN = 2.0  # Min 2:1 reward/risk
POSITION_SIZE_PERCENT = 0.05  # 5% of capital per position

# ============================================================================
# CACHE TTL (Time To Live in seconds)
# ============================================================================

CACHE_INDEX_TTL = 24 * 60 * 60  # 24 hours
CACHE_PRICE_TTL = 5 * 60  # 5 minutes
CACHE_FUNDAMENTALS_TTL = 24 * 60 * 60  # 24 hours
CACHE_NEWS_TTL = 5 * 60  # 5 minutes

# ============================================================================
# DATA FETCHING
# ============================================================================

PRICE_HISTORY_YEARS = 3
REQUEST_TIMEOUT = 10
MAX_NEWS_ARTICLES = 15

# ============================================================================
# NIFTY 500 CONFIG
# ============================================================================

INDEX_URL = "https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv"

STOCK_STOPWORDS = {
    "ltd", "limited", "india", "indian", "industries", "industry",
    "company", "corporation", "corp", "services", "service",
    "bank", "finance", "financial", "holdings", "holding",
    "the", "and", "of", "nse", "bse", "inc", "pvt",
}

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/csv,application/json,*/*",
}

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
# TOOLTIPS & HELP TEXT
# ============================================================================

TOOLTIPS = {
    "MA50": "50-day Moving Average: Average price over 50 days (short-term trend)",
    "MA200": "200-day Moving Average: Average price over 200 days (long-term trend)",
    "RSI": "Relative Strength Index (0-100): >70=overbought, <30=oversold",
    "MACD": "Moving Average Convergence Divergence: Momentum indicator",
    "BB": "Bollinger Bands: Price bounces off bands, squeeze=volatility break",
    "STOCH_RSI": "Stochastic RSI: More sensitive momentum indicator",
    "ADX": "Average Directional Index: Trend strength (>25=strong)",
    "VOLUME": "Volume Trend: Confirms price moves with buying/selling pressure",
    "SHARPE": "Sharpe Ratio: Return per unit of risk (higher=better)",
    "BETA": "Beta: Stock volatility vs market (>1=more volatile)",
    "DRAWDOWN": "Maximum Drawdown: Worst loss from peak",
    "WIN_RATE": "Win Rate: % of trades that were profitable (backtested)",
}

# ============================================================================
# SECTOR MAPPING (Nifty 500)
# ============================================================================

SECTOR_MAPPING = {
    "Financial Services": ["HDFCBANK", "ICICIBANK", "AXISBANK", "SBIN", "KOTAK", "HDFC", "INDIABULLS"],
    "Information Technology": ["TCS", "INFY", "WIPRO", "HCL", "TECH"],
    "Oil Gas & Energy": ["RELIANCE", "BPCL", "IOCL", "NTPC"],
    "Automobiles": ["MARUTI", "TATA", "HYUNDAI", "BAJAJ"],
    "Telecommunications": ["BHARTIARTL", "JIO", "VODAFONE"],
    "FMCG": ["ITC", "HINDUNILVR", "BRITANNIA"],
    "Real Estate": ["DLF", "OBEROI", "LODHA"],
    "Construction": ["LT", "ADANIPORTS"],
}
