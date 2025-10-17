import requests, pandas as pd, time
from datetime import datetime
import yfinance as yf

class DataFeed:
    def __init__(self):
        pass

    def get_bulk_price(self, tickers):
        rows = []
        if not tickers:
            return pd.DataFrame(columns=['Ticker','price','change_pct'])
        try:
            data = yf.download(tickers=tickers, period="2d", interval="1d", progress=False, threads=True, group_by='ticker', auto_adjust=False)
            if isinstance(data.columns, pd.MultiIndex):
                for t in tickers:
                    try:
                        df = data[t]['Close'].dropna()
                        if df.empty:
                            rows.append({'Ticker':t, 'price': None, 'change_pct': None})
                        else:
                            last = df.iloc[-1]
                            prev = df.iloc[-2] if len(df)>=2 else last
                            pct = None if prev==0 else (last-prev)/prev*100.0
                            rows.append({'Ticker':t, 'price': float(last), 'change_pct': float(pct) if pct is not None else None})
                    except Exception:
                        rows.append({'Ticker':t, 'price': None, 'change_pct': None})
            else:
                df = data['Close'].dropna() if 'Close' in data else data.dropna()
                last = df.iloc[-1] if not df.empty else None
                prev = df.iloc[-2] if len(df)>=2 else last
                pct = None if prev==0 else (last-prev)/prev*100.0 if last is not None else None
                rows.append({'Ticker': tickers[0], 'price': float(last) if last is not None else None, 'change_pct': float(pct) if pct is not None else None})
        except Exception:
            for t in tickers:
                try:
                    info = yf.Ticker(t).history(period="2d", interval="1d")
                    if info is None or info.empty:
                        rows.append({'Ticker':t, 'price': None, 'change_pct': None})
                    else:
                        s = info['Close']
                        last = s.iloc[-1]
                        prev = s.iloc[-2] if len(s)>=2 else last
                        pct = None if prev==0 else (last-prev)/prev*100.0
                        rows.append({'Ticker':t, 'price': float(last), 'change_pct': float(pct) if pct is not None else None})
                except Exception:
                    rows.append({'Ticker':t, 'price': None, 'change_pct': None})
        return pd.DataFrame(rows)

    def fetch_rss_headlines(self, limit=100):
        try:
            import feedparser
        except Exception:
            return pd.DataFrame(columns=['source','title','link','published'])
        feeds = [
            ("Reuters Business","http://feeds.reuters.com/reuters/businessNews"),
            ("CNBC Tech","https://www.cnbc.com/id/19854910/device/rss/rss.html"),
            ("The Verge","https://www.theverge.com/rss/index.xml"),
            ("CoinDesk","https://www.coindesk.com/arc/outboundfeeds/rss/"),
            ("Yahoo Finance","https://finance.yahoo.com/news/rssindex")
        ]
        rows = []
        for name, url in feeds:
            try:
                d = feedparser.parse(url)
                for e in d.entries[:max(1, limit//len(feeds))]:
                    rows.append({'source':name, 'title': e.get('title',''), 'link': e.get('link',''), 'published': e.get('published','')})
            except Exception:
                continue
        return pd.DataFrame(rows)
