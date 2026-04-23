# Deployment Guide: Streamlit Cloud

## Prerequisites

- GitHub account
- Code pushed to GitHub repository
- Streamlit Cloud account (free at share.streamlit.io)

---

## Step 1: Push Code to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Nifty 500 Dashboard: Production Ready"

# Create repo on GitHub, then push
git remote add origin https://github.com/YOUR_USERNAME/nifty500_app.git
git branch -M main
git push -u origin main
```

---

## Step 2: Create Streamlit Cloud Account

1. Go to https://share.streamlit.io
2. Click "Sign up with GitHub"
3. Authorize Streamlit to access your repositories
4. Return to https://share.streamlit.io

---

## Step 3: Deploy Your App

1. Click **"Create app"** button
2. Fill in:
   - **Repository:** `YOUR_USERNAME/nifty500_app`
   - **Branch:** `main`
   - **Main file path:** `app.py`
3. Click **"Deploy"**

Streamlit will automatically:
- Detect Python version
- Install `requirements.txt`
- Launch your app

**First deployment takes 2-5 minutes**

---

## Step 4: Share Your App

Once deployed:
- Your app URL: `https://nifty500-app-yourapp.streamlit.app`
- Share this link with anyone
- No installation needed on their end

---

## Updating After Deployment

Every time you push to `main`:

```bash
git add .
git commit -m "Update: better sentiment analysis"
git push origin main
```

Streamlit automatically redeploys within 30 seconds.

Check deployment status: https://share.streamlit.io/your-apps

---

## Troubleshooting Deployment

### "Requirements file not found"
- Ensure `requirements.txt` is in root directory
- Exact filename: `requirements.txt` (not `requirements.txt.txt`)

### "ModuleNotFoundError"
- Add missing package to `requirements.txt`
- Push to GitHub
- Streamlit redeploys automatically

### "App is taking too long to load"
- First load can be slow (cold start)
- Refresh after 1 minute
- Check Streamlit Cloud logs for errors

### "View logs"
- Go to https://share.streamlit.io/your-apps
- Click on your app
- Select "View logs" in dropdown

---

## Free Tier Limits (Streamlit Cloud)

✅ **Included:**
- 3 apps per account
- Unlimited traffic
- Automatic HTTPS
- Custom domain support

⚠️ **Limitations:**
- 1 CPU, 1GB RAM (slower than local)
- App sleeps after 7 days of inactivity
- 15-minute app restart timeout

**Not a concern for this dashboard** — it uses minimal resources.

---

## Performance Tips

### For Faster Loading
1. Reduce cache TTL in `config.py` if desired
2. Optimize images (not applicable here)
3. Use `@st.cache_data` efficiently (already done)

### Monitor App Health
- Check Streamlit Cloud dashboard regularly
- Review logs for errors
- Monitor execution time

---

## Custom Domain (Optional)

1. Go to https://share.streamlit.io/your-apps
2. Click app settings
3. Add custom domain
4. Update DNS CNAME record
5. Wait ~24 hours for propagation

---

## Secrets Management (When Needed)

If you add API keys later:

1. Create `.streamlit/secrets.toml` (local only):
   ```toml
   [api]
   newsapi_key = "your_key_here"
   ```

2. On Streamlit Cloud:
   - App dashboard → Settings → Secrets
   - Paste content of `secrets.toml`
   - Save

3. Access in code:
   ```python
   import streamlit as st
   api_key = st.secrets["api"]["newsapi_key"]
   ```

4. **Never commit secrets.toml to GitHub**

---

## Monitoring & Analytics

Streamlit Cloud provides:
- Real-time app usage
- Performance metrics
- Error logs
- Traffic analytics

Visit https://share.streamlit.io/your-apps to view.

---

## Questions?

- **Streamlit Docs:** https://docs.streamlit.io
- **Community Forum:** https://discuss.streamlit.io
- **GitHub Issues:** Create issue in your repo

---

**Your app is live! 🎉**
