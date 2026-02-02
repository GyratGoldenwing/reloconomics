# Reloconomics Deployment Research Document

**Student:** Jeremiah Williams
**Course:** Project & Portfolio IV (CSBS-AI)
**Date:** January 2026
**Project:** Reloconomics - Predictive Cost of Living Comparison Tool

---

## Executive Summary

This document outlines the deployment strategy for Reloconomics, a Streamlit-based Python web application. The recommended approach uses **Streamlit Community Cloud** (free tier) for zero-cost deployment with minimal configuration. Alternative options are provided for different use cases.

---

## 1. Application Overview

### Technology Stack
| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Streamlit | 1.29+ |
| Language | Python | 3.10+ |
| ML Library | scikit-learn | 1.3+ |
| Visualization | Plotly | 5.18+ |
| Data Format | JSON | - |

### System Requirements
- **Runtime:** Python 3.10 or higher
- **Memory:** ~512MB RAM (sufficient for free tier hosting)
- **Storage:** <50MB (code + data files)
- **Dependencies:** Listed in `requirements.txt`

### File Structure
```
reloconomics/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml        # Streamlit configuration
├── utils/
│   ├── tax_calculator.py
│   ├── cost_of_living.py
│   ├── forecaster.py
│   └── affordability_map.py
└── data/
    ├── federal_brackets_2024.json
    ├── state_taxes.json
    ├── cost_of_living.json
    ├── historical_expenses.json
    └── state_rpp.json
```

---

## 2. Recommended Deployment: Streamlit Community Cloud

### Why Streamlit Cloud?
- **Cost:** Free (Community tier)
- **Setup time:** <5 minutes
- **Maintenance:** Zero - automatic updates on git push
- **SSL:** Included (HTTPS)
- **Custom domain:** Supported (paid tier)

### Deployment Steps

#### Step 1: Prepare Repository
Ensure your GitHub repository contains:
```
✓ app.py (main application file)
✓ requirements.txt (dependencies)
✓ All data files in data/ folder
```

**requirements.txt:**
```
streamlit>=1.29.0
plotly>=5.18.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
```

#### Step 2: Create Streamlit Cloud Account
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign up" and authenticate with GitHub
3. Authorize Streamlit to access your repositories

#### Step 3: Deploy Application
1. Click "New app"
2. Select your GitHub repository
3. Select branch (usually `main`)
4. Set main file path: `app.py`
5. Click "Deploy"

#### Step 4: Configure Settings (Optional)
In `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#3498db"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#262730"
textColor = "#fafafa"

[server]
headless = true
port = 8501
```

### Deployment URL Format
```
https://[app-name]-[random-hash].streamlit.app
```

Example: `https://reloconomics-tfgjsjjfjvc6tq4vcosnv7.streamlit.app`

### Updating the Application
Simply push changes to GitHub:
```bash
git add .
git commit -m "Update feature"
git push origin main
```
Streamlit Cloud automatically redeploys within 1-2 minutes.

### Limitations (Free Tier)
- Apps sleep after 7 days of inactivity (wake on visit)
- 1GB memory limit
- Public repositories only
- No custom domain without paid tier

---

## 3. Alternative Deployment Options

### Option A: Hugging Face Spaces (Free)

**Pros:**
- Free hosting
- Good for ML-focused apps
- Large community

**Cons:**
- Requires Hugging Face account
- Slightly more setup than Streamlit Cloud

**Steps:**
1. Create account at huggingface.co
2. Create new Space, select "Streamlit" SDK
3. Upload files or connect GitHub repo
4. App deploys automatically

### Option B: Railway (Free Tier Available)

**Pros:**
- More control over environment
- Supports databases
- $5/month free credit

**Cons:**
- More complex setup
- May need Procfile configuration

**Procfile:**
```
web: streamlit run app.py --server.port $PORT --server.headless true
```

### Option C: Render (Free Tier Available)

**Pros:**
- Free static site + web service tiers
- Auto-deploy from GitHub
- Good documentation

**Cons:**
- Free tier services spin down after inactivity
- Cold starts can take 30+ seconds

### Option D: Self-Hosted (VPS)

**Pros:**
- Full control
- No platform limitations

**Cons:**
- Requires server management
- Costs $5-10/month minimum (DigitalOcean, Linode)
- Must handle SSL, security, updates

**Basic VPS Setup:**
```bash
# On Ubuntu server
sudo apt update
sudo apt install python3-pip python3-venv

# Clone and setup
git clone https://github.com/username/reloconomics.git
cd reloconomics
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with screen/tmux for persistence
streamlit run app.py --server.port 8501 --server.headless true
```

---

## 4. Deployment Comparison Matrix

| Platform | Cost | Setup Time | Auto-Deploy | SSL | Best For |
|----------|------|------------|-------------|-----|----------|
| **Streamlit Cloud** | Free | 5 min | Yes | Yes | Streamlit apps |
| Hugging Face | Free | 10 min | Yes | Yes | ML demos |
| Railway | Free/$5 | 15 min | Yes | Yes | Full-stack |
| Render | Free | 15 min | Yes | Yes | Web services |
| VPS | $5+/mo | 1+ hour | Manual | Manual | Full control |

---

## 5. Production Considerations

### Security
- **Secrets:** Use Streamlit's secrets management for API keys
  ```python
  # Access via st.secrets
  api_key = st.secrets["API_KEY"]
  ```
- **Input validation:** Already implemented for salary and city inputs
- **No sensitive data:** App uses public government data only

### Performance
- **Caching:** Use `@st.cache_data` for expensive computations
  ```python
  @st.cache_data
  def load_historical_expenses():
      # ... loading code
  ```
- **Session state:** Currently minimal; no persistence needed

### Monitoring
- Streamlit Cloud provides basic analytics (views, unique visitors)
- For detailed monitoring, integrate Google Analytics via custom component

### Scaling
- Free tier handles ~100 concurrent users adequately
- For higher traffic, consider paid tiers or self-hosting with load balancer

---

## 6. Current Deployment Status

**Live URL:** https://reloconomics-tfgjsjjfjvc6tq4vcosnv7.streamlit.app

**Platform:** Streamlit Community Cloud

**Repository:** Connected to GitHub (auto-deploy enabled)

**Status:** Active and accessible

---

## 7. Maintenance Checklist

### Weekly
- [ ] Verify app loads correctly
- [ ] Check for Streamlit version updates

### Monthly
- [ ] Review error logs (if available)
- [ ] Update dependencies if security patches released

### Annually
- [ ] Update tax bracket data (January - new IRS rates)
- [ ] Update state tax rates (if changed)
- [ ] Refresh historical expense data

---

## 8. Rollback Procedure

If a deployment causes issues:

1. **Streamlit Cloud:** Redeploy previous commit
   ```bash
   git revert HEAD
   git push origin main
   ```

2. **Manual rollback:**
   - Go to Streamlit Cloud dashboard
   - Click app settings
   - Select previous commit to deploy

---

## 9. Cost Summary

| Item | Cost | Notes |
|------|------|-------|
| Streamlit Cloud hosting | $0 | Free tier |
| GitHub repository | $0 | Public repo |
| Domain (optional) | $0-12/yr | Custom domain optional |
| SSL certificate | $0 | Included |
| **Total** | **$0** | Fully free deployment |

---

## 10. Conclusion

Streamlit Community Cloud provides the optimal deployment solution for Reloconomics:
- **Zero cost** for hosting
- **Minimal setup** (under 5 minutes)
- **Automatic updates** on git push
- **SSL included** for security
- **No maintenance** required

The application is currently deployed and accessible at the live URL. Future updates require only a git push to the connected repository.

---

## Appendix: Quick Reference Commands

```bash
# Local development
streamlit run app.py

# Install dependencies
pip install -r requirements.txt

# Deploy (after Streamlit Cloud setup)
git push origin main

# Check Streamlit version
streamlit version

# Generate requirements.txt from environment
pip freeze > requirements.txt
```

---

*Document prepared for PP4 Iteration 4 submission - Extra Credit Assignment*
