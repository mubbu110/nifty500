# Professional Configuration - Enhanced

# ============================================================================
# API KEYS
# ============================================================================
FINNHUB_API_KEY = "YOUR_FINNHUB_KEY"

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
MA_PERIOD_SHORT = 50
MA_PERIOD_LONG = 200
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BB_PERIOD = 20
BB_STD = 2
STOCH_RSI_PERIOD = 14
STOCH_RSI_K = 3
STOCH_RSI_D = 3
ADX_PERIOD = 14
ADX_STRONG = 25
ADX_VERY_STRONG = 40
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
BACKTEST_INITIAL_CAPITAL = 100000
BACKTEST_POSITION_SIZE = 0.95

# ============================================================================
# SIGNAL CONFIRMATION RULES
# ============================================================================
BUY_REQUIREMENTS = {
    "trend": "Price above MA200",
    "momentum": "RSI > 40",
    "macd": "MACD above signal",
    "volume": "Volume above 20-day avg",
    "bollinger": "Price near lower band OR above middle",
}
SELL_REQUIREMENTS = {
    "trend": "Price below MA50",
    "momentum": "RSI > 70",
    "macd": "MACD below signal",
    "volume": "High volume on down days",
}

# ============================================================================
# RISK MANAGEMENT
# ============================================================================
RISK_PER_TRADE = 0.02
REWARD_TO_RISK_MIN = 2.0
POSITION_SIZE_PERCENT = 0.05

# ============================================================================
# CACHE TTL
# ============================================================================
CACHE_INDEX_TTL = 24 * 60 * 60
CACHE_PRICE_TTL = 5 * 60
CACHE_FUNDAMENTALS_TTL = 24 * 60 * 60
CACHE_NEWS_TTL = 5 * 60

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
    {"Company Name": "Larsen & Toubro Ltd.", "Symbol": "LT", "Industry": "Capital Goods"},
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
# SECTOR MAPPING — covers all major Nifty 500 industries
# Key = Industry name as it appears in the NSE CSV (case-insensitive match used in app)
# Up to 4 peers per sector to keep API calls manageable
# ============================================================================
SECTOR_MAPPING = {
    # Financial Services
    "Financial Services": ["HDFCBANK", "ICICIBANK", "AXISBANK", "SBIN", "KOTAKBANK", "INDUSINDBK", "BANDHANBNK", "FEDERALBNK"],
    "Banking": ["HDFCBANK", "ICICIBANK", "AXISBANK", "SBIN", "KOTAKBANK", "INDUSINDBK"],

    # IT
    "Information Technology": ["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM", "LTIM", "MPHASIS", "COFORGE"],
    "IT": ["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM"],

    # Oil & Gas
    "Oil Gas & Consumable Fuels": ["RELIANCE", "ONGC", "BPCL", "IOC", "GAIL", "HINDPETRO"],
    "Oil Gas & Energy": ["RELIANCE", "ONGC", "BPCL", "IOC", "GAIL"],

    # Pharma
    "Pharmaceuticals": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "AUROPHARMA", "LUPIN", "ALKEM", "BIOCON"],
    "Pharmaceuticals & Biotechnology": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "AUROPHARMA", "LUPIN"],

    # Auto
    "Automobile and Auto Components": ["MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "EICHERMOT", "HEROMOTOCO", "TVSMOTOR", "ASHOKLEY"],
    "Automobiles": ["MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "EICHERMOT"],
    "Auto Components": ["MOTHERSON", "BOSCHLTD", "APOLLOTYRE", "CEATLTD", "MRF"],

    # FMCG
    "Fast Moving Consumer Goods": ["ITC", "HINDUNILVR", "NESTLEIND", "BRITANNIA", "DABUR", "MARICO", "GODREJCP", "COLPAL"],
    "FMCG": ["ITC", "HINDUNILVR", "NESTLEIND", "BRITANNIA", "DABUR"],

    # Capital Goods / Industrials
    "Capital Goods": ["LT", "SIEMENS", "ABB", "BHEL", "CUMMINSIND", "APLAPOLLO", "THERMAX", "HAVELLS"],
    "Industrial Manufacturing": ["LT", "SIEMENS", "ABB", "BHEL", "CUMMINSIND", "THERMAX"],

    # Telecom
    "Telecommunication": ["BHARTIARTL", "INDUSTOWER", "TATACOMM", "HFCL"],
    "Telecom": ["BHARTIARTL", "INDUSTOWER", "TATACOMM"],

    # Metals & Mining
    "Metals & Mining": ["TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "SAIL", "NMDC", "COALINDIA", "HINDCOPPER"],
    "Metals": ["TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "SAIL"],

    # Power & Energy
    "Power": ["NTPC", "POWERGRID", "ADANIPOWER", "TATAPOWER", "TORNTPOWER", "CESC"],
    "Utilities": ["NTPC", "POWERGRID", "TATAPOWER", "TORNTPOWER"],

    # Real Estate
    "Realty": ["DLF", "GODREJPROP", "PRESTIGE", "OBEROIRLTY", "PHOENIXLTD", "LODHA"],
    "Real Estate": ["DLF", "GODREJPROP", "PRESTIGE", "OBEROIRLTY"],

    # Construction / Infrastructure
    "Construction": ["LT", "NCC", "KNR", "KNRCON", "IRB", "HGINFRA", "PNC"],
    "Infrastructure": ["LT", "ADANIPORTS", "IRB", "HGINFRA"],

    # Consumer Durables
    "Consumer Durables": ["TITAN", "VOLTAS", "HAVELLS", "CROMPTON", "DIXON", "BLUESTAR", "WHIRLPOOL"],

    # Chemicals
    "Chemicals": ["PIDILITIND", "AARTIIND", "DEEPAKNTR", "ALKYLAMINE", "NAVINFLUOR", "VINATIORGA", "BALCHEMLTD"],
    "Specialty Chemicals": ["PIDILITIND", "AARTIIND", "DEEPAKNTR", "ALKYLAMINE", "NAVINFLUOR"],

    # Cement
    "Cement & Cement Products": ["ULTRACEMCO", "AMBUJACEM", "ACC", "SHREECEM", "RAMCOCEM", "JKCEMENT"],
    "Cement": ["ULTRACEMCO", "AMBUJACEM", "ACC", "SHREECEM"],

    # Textiles
    "Textiles": ["PAGEIND", "VIPIND", "RAYMOND", "TRIDENT", "WELSPUNIND"],

    # Media & Entertainment
    "Media Entertainment & Publication": ["ZEEL", "SUNTV", "PVRINOX", "INOXGREEN"],
    "Media": ["ZEEL", "SUNTV", "PVRINOX"],

    # Insurance
    "Insurance": ["SBILIFE", "HDFCLIFE", "ICICIPRULI", "LICI", "STARHEALTH"],

    # Healthcare Services
    "Healthcare": ["APOLLOHOSP", "FORTIS", "MAXHEALTH", "MEDANTA", "NARAYANHRUDAYALAYA"],

    # Retail
    "Retailing": ["DMART", "TRENT", "ABFRL", "SHOPERSTOP", "NYKAA"],

    # IT Services / Fintech
    "Financial Technology": ["PAYTM", "POLICYBZR", "ZOMATO", "NAUKRI", "JUSTDIAL"],

    # Logistics
    "Transportation": ["IRCTC", "CONCOR", "BLUEDART", "MAHLOG", "DELHIVERY"],
    "Logistics": ["IRCTC", "CONCOR", "BLUEDART", "DELHIVERY"],

    # Diversified
    "Diversified": ["TATAMOTORS", "RELIANCE", "ITC", "LT", "ADANIENT"],
}
