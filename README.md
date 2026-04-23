# Nifty 500 Stock Impact Dashboard

A professional educational tool for analyzing Nifty 500 stocks using technical analysis and news sentiment. Combines weighted technical indicators with AI-powered sentiment analysis from financial news.

**Demo:** [Live on Streamlit Cloud]

---

## 🎯 Features

### Technical Analysis
- **Price Trend:** 3-year daily data with weighted moving averages
- **Moving Averages:** 50-day (short-term) and 200-day (long-term) trends
- **RSI (Relative Strength Index):** Momentum indicator (0-100 scale)
- **Volatility Analysis:** Identifies risk levels in price movement
- **Composite Scoring:** Weighted technical score (-4 to +4 range)

### News & Sentiment
- **Multi-Select Headlines:** Analyze multiple articles simultaneously
- **Smart Sentiment Scoring:** Pattern-based keyword weighting (not simple word count)
- **Confidence Metrics:** Transparency on signal strength
- **Auto-Fetching:** Pulls latest news from Yahoo Finance RSS
- **Manual Input:** Paste custom headlines to test

### Smart Recommendations
- **BUY:** Strong technical + bullish news consensus
- **SELL:** Technical weakness + bearish signals
- **HOLD:** Balanced or mixed signals
- **Composite Scoring:** Technical (60%) + News (40%) weighted combination

### User Experience
- **Dark/Light Theme Toggle:** Adaptive interface for any environment
- **Mixed Audience Support:** Tooltips for beginners, advanced metrics for pros
- **Multi-Stock Search:** Instant filtering across 500 Nifty constituents
- **Professional Charts:** Interactive Plotly visualizations

---

## 📊 Technical Details

### Data Sources
- **Prices:** Yahoo Finance (3-year history, daily candles)
- **News:** Yahoo Finance RSS Feed
- **Index:** National Stock Exchange (NSE) official Nifty 500 list

### Architecture
```
app.py          → Main Streamlit app (UI orchestration)
utils.py        → Data fetching & calculations (technical + sentiment)
theme.py        → Dynamic theme management (dark/light toggle)
ui.py           → Reusable UI components
config.py       → Centralized settings (thresholds, weights, colors)
requirements.txt → Dependencies
.streamlit/     → Streamlit Cloud configuration
```

### Technical Scoring Algorithm

**Trend Component (2.5 pts max):**
- Strong uptrend (Price > MA50 > MA200): +2.5
- Moderate uptrend (Above MA200): +1.5
- Short-term strength (Above MA50): +0.5
- Below MAs: -1.0

**Momentum Component (1.5 pts max):**
- Extremely oversold (RSI < 20): +1.5
- Oversold (RSI < 30): +0.5
- Extremely overbought (RSI > 80): -1.5
- Overbought (RSI > 70): -0.5

**News Impact (40% of final score):**
- Averaged sentiment from selected articles
- Weighted by confidence (signal strength)
- Limited impact to prevent overvaluation

### Sentiment Analysis

**Bullish Keywords** (with weights):
- beats, profit, growth, surge, rally, upgrade, approval, expansion, record, launches, wins, raises, buyback, strong, order

**Bearish Keywords** (with negative weights):
- misses, loss, fraud, probe, downgrade, penalty, resigns, crash, weak, falls, default, debt, selloff, drop, cuts

**Scoring:** -10 to +10 range normalized from signal combinations

---

## 🚀 Quick Start

### Local Development

1. **Clone and navigate:**
   ```bash
   git clone <your-repo-url>
   cd nifty500_app
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run locally:**
   ```bash
   streamlit run app.py
   ```

5. **Open browser:**
   Navigate to `http://localhost:8501`

---

## ☁️ Deploy to Streamlit Cloud

### Setup (First Time Only)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Initial commit: Nifty 500 Dashboard"
   git push origin main
   ```

2. **Sign in to Streamlit Cloud:**
   - Go to https://share.streamlit.io
   - Click "Create app"
   - Connect your GitHub repo
   - Select this repo and `app.py` as the main file

3. **Configure:**
   - Runtime: Python 3.11+
   - No API keys required (uses free Yahoo Finance)

4. **Deploy:**
   - Click "Deploy"
   - Streamlit automatically reads `requirements.txt`

### After Deployment

Every push to `main` automatically redeploys your app. Check logs for errors.

---

## 🎨 Customization

### Theme Colors

Edit `config.py`:

```python
THEMES = {
    "dark": {
        "bg_primary": "#0a0e27",      # Change background
        "accent": "#a78bfa",           # Change accent color
        # ... other colors
    },
    "light": { ... }
}
```

### Technical Thresholds

Modify in `config.py`:

```python
RSI_OVERBOUGHT = 70        # Change overbought threshold
RSI_OVERSOLD = 30          # Change oversold threshold
SCORE_BUY = 3.0            # Change BUY recommendation threshold
SCORE_SELL = -2.0          # Change SELL recommendation threshold
```

### Sentiment Keywords

Add/remove keywords in `config.py`:

```python
BULLISH_SIGNALS = {
    "your_word": 2.0,      # Weight of 2.0
    # ... more words
}
```

---

## 📈 How to Use

### Basic Workflow

1. **Select Stock:** Search or scroll to find any Nifty 500 stock
2. **View Technicals:** See price, MAs, RSI, volatility automatically
3. **Fetch News:** Click "Fetch News" to load recent headlines
4. **Select Headlines:** Multi-select articles to analyze
5. **View Sentiment:** See impact score for each article
6. **Read Recommendation:** Combined BUY/SELL/HOLD with reasoning

### Advanced Usage

**Test Sentiment on Custom Headlines:**
- Paste your own news in the sidebar
- See how different wording affects sentiment score
- Learn what keywords matter for technical interpretation

**Study Historical Patterns:**
- Interactive charts show 1-year price history
- See how stock reacted to past trends
- Understand technical indicator behavior

---

## ⚠️ Disclaimer

**This is an educational tool. Not investment advice.**

- Use only for learning technical analysis and sentiment basics
- Always do your own research before trading
- Past performance ≠ future results
- Consult a financial professional before making trades
- Markets are unpredictable; no indicator is 100% accurate

---

## 🔧 Troubleshooting

### "Could not load enough price data"
- Stock may be too new or delisted
- Try another stock from the Nifty 500 list
- Check internet connection

### "No recent news found"
- Yahoo Finance RSS feed may be slow
- Try again in a few minutes
- Use manual headline input to test sentiment

### Slow performance on Streamlit Cloud
- Free tier is slower than local
- Dashboard caches data (15 min for prices, 5 min for news)
- Refresh manually if needed

### Theme not persisting
- Streamlit Cloud resets session on browser refresh
- Select theme each time (being fixed in next update)

---

## 📚 Learning Resources

### Technical Analysis
- [Investopedia: Moving Averages](https://www.investopedia.com/terms/m/movingaverage.asp)
- [RSI Explained](https://www.investopedia.com/terms/r/rsi.asp)
- [Nifty 500 Index Guide](https://www.niftyindices.com/)

### Sentiment Analysis
- [How News Affects Stock Prices](https://www.investopedia.com/articles/investing/082515/how-news-affects-stock-prices.asp)

### Python & Streamlit
- [Streamlit Docs](https://docs.streamlit.io)
- [Plotly Documentation](https://plotly.com/python/)

---

## 🤝 Contributing

Found a bug? Have ideas? Open an issue or submit a pull request.

### Areas for Contribution
- Add more sentiment keywords
- Support other stock indices
- Improve chart visualizations
- Add more technical indicators
- Optimize performance

---

## 📄 License

MIT License - Use freely for educational purposes.

---

## 👨‍💻 Author

[Your Name]
- GitHub: [@yourprofile](https://github.com/yourprofile)
- LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)

---

## 🎯 Roadmap

- [ ] Support BSE, Sensex, Nifty 50
- [ ] Historical comparison (how stock reacted to similar news before)
- [ ] Volume analysis
- [ ] Advanced indicators (Bollinger Bands, MACD)
- [ ] Email alerts for significant moves
- [ ] Portfolio tracking
- [ ] Dark mode fixes for Streamlit Cloud persistence

---

**Last Updated:** April 2026  
**Status:** Stable (Educational Use)
