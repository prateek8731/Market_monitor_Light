import streamlit as st
from data_feed import DataFeed
from utils import parse_dataroma_holdings, sentiment_of_headlines
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Buffett Portfolio Monitor (Light)", layout="wide")

st.title("📈 Buffett Portfolio Monitor — Lightweight")

st.sidebar.markdown("## Controls")
refresh = st.sidebar.button("Refresh Data")
top_n = st.sidebar.slider("Top N holdings to show", 5, 25, 10)

df_holdings = None
with st.spinner("Loading holdings (cached)..."):
    try:
        df_holdings = parse_dataroma_holdings()
    except Exception as e:
        st.error(f"Failed to fetch holdings: {e}")

if df_holdings is None or df_holdings.empty:
    st.warning("No holdings data available. Try refreshing or check network.")
else:
    st.sidebar.markdown(f"Found **{len(df_holdings)}** holdings (parsed).")
    st.header("Portfolio Summary")
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Top holdings")
        st.dataframe(df_holdings.head(top_n).reset_index(drop=True))
    with col2:
        st.subheader("Top holdings (% of portfolio)")
        fig = px.pie(df_holdings.head(top_n), names='Ticker', values='Pct', title='Top holdings by % of portfolio')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Live Prices for Top Holdings (yfinance)")
    tickers = df_holdings['Ticker'].head(top_n).tolist()
    df_prices = None
    with st.spinner("Fetching prices..."):
        df_prices = DataFeed().get_bulk_price(tickers)
    if df_prices is not None and not df_prices.empty:
        merged = df_holdings.set_index('Ticker').join(df_prices.set_index('Ticker'), how='left')
        merged = merged.reset_index()
        st.dataframe(merged[['Ticker','Name','Pct','price','change_pct']].rename(columns={'Pct':'% of portfolio','price':'Price','change_pct':'24h %'}))
        st.markdown("### Holdings Market Value Estimate (using % weight * hypothetical portfolio size)")
        port_size = st.number_input("Assumed portfolio size (USD)", value=1000000.0, step=10000.0)
        merged['est_value'] = merged['Pct']/100.0 * port_size
        st.dataframe(merged[['Ticker','Name','Pct','price','est_value']].rename(columns={'Pct':'% of portfolio'}))
    else:
        st.info("Price data unavailable.")

    st.markdown("---")
    st.subheader("News & Sentiment (Headlines from RSS)")
    with st.spinner("Fetching headlines..."):
        try:
            headlines = DataFeed().fetch_rss_headlines(limit=50)
            sent = sentiment_of_headlines(headlines['title'].tolist())
            headlines['sentiment'] = headlines['title'].apply(lambda t: sent.get(t, 0.0))
            st.dataframe(headlines[['source','title','published','sentiment']].head(50))
            avg_sent = headlines['sentiment'].mean()
            st.metric("Average sentiment (VADER compound)", f"{avg_sent:.3f}")
        except Exception as e:
            st.error(f"Failed to fetch headlines: {e}")

st.markdown("---")
st.caption("Lightweight app: data scraped from dataroma.com and prices from yfinance. Not financial advice.")
