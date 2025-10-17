#  Portfolio Monitor (Lightweight)

This lightweight Streamlit app scrapes Berkshire Hathaway holdings (from Dataroma), fetches live prices via yfinance, and shows news headlines with VADER sentiment. It is optimized for quick deployment on Streamlit Cloud.

## Files
- `streamlit_app.py` - main app
- `data_feed.py` - price & RSS fetching utilities
- `utils.py` - dataroma parsing & sentiment helper
- `requirements.txt` - Python packages
- `packages.txt` - system packages for Streamlit Cloud
- `runtime.txt` - Python runtime for Streamlit Cloud

## Deploy
1. Push this repo to GitHub.
2. On Streamlit Cloud, create a new app pointing to this repo.
3. Deploy — it should install system packages and Python packages and start quickly.
