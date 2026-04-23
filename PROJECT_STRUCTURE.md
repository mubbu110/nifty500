# Project Structure & File Organization

```
nifty500_app/
│
├── 📱 app.py                      [Main Application]
│   ├── Imports: utils, theme, ui, config
│   ├── Sidebar: Stock selection + news fetching
│   ├── Main content: Charts + analysis
│   └── Footer + recommendations
│
├── 🔧 utils.py                    [Data & Logic]
│   ├── load_nifty500()            → Fetch stock list from NSE
│   ├── fetch_stock_data()         → Get price data from Yahoo
│   ├── calculate_technical_summary()  → Technical analysis
│   ├── fetch_stock_news()         → RSS feed parsing
│   ├── analyze_sentiment()        → News sentiment scoring
│   └── generate_recommendation()  → Final BUY/SELL/HOLD
│
├── 🎨 theme.py                    [Styling & Appearance]
│   ├── apply_theme_css()          → Generate CSS dynamically
│   ├── get_theme()                → Get current theme
│   ├── set_theme()                → Change theme
│   ├── get_colors()               → Get color palette
│   └── theme_toggle_button()      → UI toggle in sidebar
│
├── 🖼️  ui.py                      [Reusable Components]
│   ├── display_recommendation_card()  → Show BUY/SELL/HOLD
│   ├── display_metrics()          → Show price, MA, RSI
│   ├── plot_technical_chart()     → Interactive Plotly chart
│   ├── display_news_item()        → Format single news
│   ├── display_news_list_multiselect()  → Multi-select UI
│   └── display_footer()           → Bottom disclaimer
│
├── ⚙️  config.py                  [Settings & Constants]
│   ├── THEMES                     → Dark/light colors
│   ├── Technical parameters       → MA periods, RSI thresholds
│   ├── Sentiment weights          → BULLISH_SIGNALS, BEARISH_SIGNALS
│   ├── TOOLTIPS                   → Help text for mixed audience
│   ├── Recommendation thresholds  → BUY/SELL/HOLD scores
│   └── API settings               → Headers, timeouts, caches
│
├── .streamlit/
│   └── config.toml                [Streamlit Cloud Config]
│       ├── Theme colors (primary, secondary)
│       ├── Server settings (port, upload limit)
│       └── Logger & browser settings
│
├── requirements.txt               [Python Dependencies]
│   ├── streamlit>=1.40.0
│   ├── plotly>=5.24.0
│   ├── pandas>=2.2.0
│   ├── numpy>=1.26.0
│   ├── requests>=2.31.0
│   └── feedparser>=6.0.11
│
├── README.md                      [User Guide]
│   ├── Features overview
│   ├── Quick start (local + cloud)
│   ├── How to use
│   ├── Customization guide
│   └── Troubleshooting
│
├── DEPLOYMENT.md                  [Streamlit Cloud Deploy]
│   ├── Step-by-step deployment
│   ├── Custom domains
│   ├── Secrets management
│   └── Monitoring tips
│
├── CHANGES.md                     [What's New]
│   ├── Problems fixed
│   ├── Before/after comparisons
│   ├── Migration guide
│   └── Customization reference
│
└── .gitignore                     [Git Exclusions]
    └── Excludes: __pycache__, venv/, .env, etc.
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│             User Interface (app.py)                  │
│  ┌──────────────────────────────────────────────┐   │
│  │ Sidebar: Stock Selection + News Fetching     │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │ Main: Charts + Recommendation + Analysis     │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
         ↓                        ↓              ↓
    ┌─────────────┐      ┌──────────────┐  ┌────────┐
    │   utils.py  │      │  theme.py    │  │ ui.py  │
    │             │      │              │  │        │
    │ • fetch()   │      │ • colors()   │  │ • plot │
    │ • calc()    │      │ • toggle()   │  │ • card │
    │ • sentiment │      │ • css()      │  │ • list │
    └─────────────┘      └──────────────┘  └────────┘
         ↓                        ↓
    ┌──────────────────┐    ┌────────────┐
    │  config.py       │    │ Remote     │
    │                  │    │ Data:      │
    │ • Thresholds     │    │ • Yahoo    │
    │ • Sentiment wts  │    │ • RSS      │
    │ • Colors         │    │ • NSE      │
    │ • Tooltips       │    └────────────┘
    └──────────────────┘
```

---

## 🔄 Execution Flow (Simplified)

```
1. User loads app.py
   ↓
2. Load configuration (config.py)
   ↓
3. Apply theme CSS (theme.py)
   ↓
4. Sidebar initialization
   ├─ Load stock list (utils.load_nifty500)
   ├─ Allow search & selection
   └─ Wait for user action
   ↓
5. User selects stock & clicks "Fetch News"
   ├─ fetch_stock_data() → Yahoo Finance
   ├─ calculate_technical_summary() → Technical analysis
   ├─ fetch_stock_news() → RSS feed
   └─ Display in main content
   ↓
6. User selects news headlines
   ↓
7. Main content updates
   ├─ generate_recommendation() → Combined score
   ├─ display_recommendation_card() → BUY/SELL/HOLD
   ├─ display_metrics() → Price, MAs, RSI
   ├─ plot_technical_chart() → Plotly chart
   └─ display_news_item() → Sentiment for each
   ↓
8. User can toggle theme
   ├─ set_theme()
   ├─ apply_theme_css()
   └─ st.rerun() → Full refresh with new colors
```

---

## 📂 File Dependencies

### app.py depends on:
```
config.py  → Settings
utils.py   → Data fetching & logic
theme.py   → Styling & toggle
ui.py      → UI components
```

### utils.py depends on:
```
config.py  → All parameters (thresholds, URLs, timeouts)
pandas, numpy, requests, feedparser  → External libraries
```

### theme.py depends on:
```
config.py  → THEMES dict
streamlit  → Session state
```

### ui.py depends on:
```
config.py  → TOOLTIPS
theme.py   → get_colors()
plotly     → Charts
pandas     → Data handling
```

---

## 🚀 Deployment Structure

```
GitHub Repository
    ↓
.gitignore (excludes __pycache__, venv/, .env)
    ↓
Streamlit Cloud (share.streamlit.io)
    ↓
Reads:
    ├─ requirements.txt (installs dependencies)
    ├─ .streamlit/config.toml (settings)
    └─ app.py (entry point)
    ↓
Runs: streamlit run app.py
    ↓
Live at: https://nifty500-app-yourname.streamlit.app
```

---

## 📝 Important Notes

### Module Imports

All modules can be imported independently:
```python
# In any file:
from utils import fetch_stock_data
from config import SCORE_BUY
from theme import get_colors
from ui import display_metrics
```

### No Circular Dependencies
- `config.py` imports nothing (safe to import anywhere)
- `utils.py` only imports config + external libs
- `theme.py` imports config + streamlit
- `ui.py` imports config + theme + streamlit
- `app.py` imports all (orchestrator)

### Thread Safety
- All `@st.cache_data` functions are thread-safe
- Session state handles concurrent users
- No global state issues

---

## ✅ Testing Structure (When Needed)

```
tests/
├── test_utils.py
│   ├── test_sentiment_analysis()
│   ├── test_technical_scoring()
│   └── test_news_filtering()
├── test_config.py
│   └── test_sentiment_weights()
└── test_theme.py
    └── test_color_generation()

# Run: pytest tests/
```

---

**This modular structure makes it easy to:**
- ✅ Add new features
- ✅ Fix bugs in isolated areas
- ✅ Test individual components
- ✅ Onboard other developers
- ✅ Scale to multiple indices
