# Quick Start Guide

## ⚡ Get Running in 5 Minutes

### Local Development

```bash
# 1. Clone/navigate to project
cd nifty500_app

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run app
streamlit run app.py

# 5. Open browser to localhost:8501
```

---

## ☁️ Deploy to Streamlit Cloud

```bash
# 1. Push to GitHub
git add .
git commit -m "Initial: Nifty 500 Dashboard"
git push origin main

# 2. Go to https://share.streamlit.io
# 3. Click "Create app"
# 4. Select repo + app.py
# 5. Deploy

# Your app live at: https://nifty500-app-username.streamlit.app
```

**That's it.** No API keys, no database, no backend needed.

---

## 📂 What You Get

```
10 Files Total:
├── 5 Python files (450 lines total)
├── 3 Documentation files
├── 1 Config file (Streamlit)
└── 1 Dependencies file
```

**Ready to use.** No modifications needed.

---

## 🎯 Key Features

✅ **Nifty 500 Support** — All 500 stocks  
✅ **3-Year Price Data** — Technical analysis  
✅ **Live News Feed** — Yahoo Finance RSS  
✅ **Smart Sentiment** — Pattern-based, not word counting  
✅ **Multi-Select News** — Combine multiple articles  
✅ **Dark/Light Mode** — User choice  
✅ **Professional Charts** — Interactive Plotly  
✅ **Mobile Friendly** — Responsive design  
✅ **Zero Dependencies** — Free APIs only  
✅ **Production Ready** — Deployed on Streamlit Cloud  

---

## 🔧 Customization (5 Minutes Each)

### Change Colors
Edit `config.py`, section `THEMES`:
```python
"dark": {
    "accent": "#a78bfa",  # Change this
    ...
}
```

### Add Sentiment Keywords
Edit `config.py`, section `BULLISH_SIGNALS`:
```python
BULLISH_SIGNALS = {
    "breakout": 2.0,  # Add this
    "beats": 2.0,
    ...
}
```

### Change Technical Thresholds
Edit `config.py`:
```python
RSI_OVERBOUGHT = 70      # Change from 70
RSI_OVERSOLD = 30        # Change from 30
SCORE_BUY = 3.0          # Change recommendation threshold
```

---

## 📊 How It Works (Simple Version)

```
1. User picks stock
   ↓
2. App fetches 3-year price data
   ↓
3. Calculates: Price, MA50, MA200, RSI, Volatility
   ↓
4. App fetches latest news (Yahoo Finance)
   ↓
5. Analyzes each headline for sentiment
   ↓
6. Combines technical score (60%) + news (40%)
   ↓
7. Shows BUY/SELL/HOLD with explanation
```

---

## ⚠️ Important Limits

**Free Tier (Streamlit Cloud):**
- 1 GB RAM (slow but works)
- Sleeps after 7 days inactivity
- Free tier is good for learning/hobby

**No Issues For:**
- Educational use ✅
- Portfolio piece ✅
- Small-scale trading ✅
- Personal learning ✅

---

## 🚀 Next Steps

### Immediate (Deploy Now)
1. Read `DEPLOYMENT.md`
2. Push to GitHub
3. Deploy to Streamlit Cloud
4. Share link with friends

### Short Term (Polish)
1. Read `CHANGES.md` to understand new code
2. Customize colors in `config.py`
3. Add your own sentiment keywords
4. Test different stocks

### Long Term (Extend)
1. Add more indicators (MACD, Bollinger Bands)
2. Support other indices (Nifty 50, Sensex)
3. Add email alerts
4. Track portfolio

---

## 📚 Documentation Map

| File | Purpose | Read if... |
|------|---------|-----------|
| `README.md` | Complete guide | Starting fresh |
| `DEPLOYMENT.md` | Deploy to cloud | Going live |
| `CHANGES.md` | What changed | Want to understand code |
| `PROJECT_STRUCTURE.md` | File organization | Making major changes |
| `config.py` | All settings | Customizing |

---

## ❓ Quick FAQs

**Q: Can I modify the code?**  
A: Yes. Edit any `.py` file, push to GitHub, redeploys automatically.

**Q: Can I use this for trading?**  
A: No. It's educational only. Never trade based on one indicator.

**Q: Will this work on mobile?**  
A: Yes. Streamlit is responsive. Works on phones + tablets.

**Q: Do I need an API key?**  
A: No. Uses free Yahoo Finance + RSS feeds.

**Q: Can I sell this?**  
A: Not legally without compliance. For educational use only.

**Q: How often does data update?**  
A: Prices every 15 min, news every 5 min (can customize in config.py).

**Q: What if news source breaks?**  
A: Error message shows. Switch to manual headlines while we fix.

---

## 🆘 Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Port 8501 already in use"
```bash
streamlit run app.py --logger.level=debug --client.toolbarMode=minimal
```

### "App running slow"
- Reduce cache TTL in `config.py`
- Free tier is naturally slower
- Local runs much faster

### "News not loading"
- Yahoo RSS can be slow
- Try "Fetch News" again
- Use manual headline feature

---

## 📞 Support

- **Errors?** Check `.streamlit/logs/` folder
- **Streamlit help?** https://discuss.streamlit.io
- **Code questions?** Read docstrings in Python files
- **Ideas?** Create GitHub issue

---

## ✨ You're Ready!

This app is **production-ready**. No modifications needed to deploy.

```bash
# Three commands to go live:
git add .
git commit -m "Nifty 500 Dashboard"
git push origin main
```

**Deployed in 30 seconds.** ⚡

---

**Happy analyzing!** 📈
