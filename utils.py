import requests
from bs4 import BeautifulSoup
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def parse_dataroma_holdings():
    url = "https://www.dataroma.com/m/holdings.php?m=BRK"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", {"class":"grid"})
    if table is None:
        table = soup.find("table")
        if table is None:
            return pd.DataFrame()
    rows = []
    for tr in table.find_all("tr")[1:]:
        cols = tr.find_all("td")
        if len(cols) < 6:
            continue
        try:
            stock_cell = cols[1]
            a = stock_cell.find("a")
            name = a.text.strip() if a else stock_cell.text.strip()
            ticker = None
            if "(" in name and ")" in name:
                parts = name.split("(")
                name = parts[0].strip()
                ticker = parts[-1].replace(")","").strip()
            pct_text = cols[-1].text.strip().replace('%','').replace(',','')
            try:
                pct = float(pct_text)
            except:
                pct = 0.0
            rows.append({"Ticker": ticker if ticker else name, "Name": name, "Pct": pct})
        except Exception:
            continue
    df = pd.DataFrame(rows)
    df = df[df['Ticker'].notna()].reset_index(drop=True)
    def clean_t(t):
        t = str(t).strip()
        if t.isupper() and len(t)<=6:
            return t
        return t.split()[0] if t else t
    df['Ticker'] = df['Ticker'].apply(clean_t)
    return df

def sentiment_of_headlines(headlines):
    analyzer = SentimentIntensityAnalyzer()
    out = {}
    for h in headlines:
        try:
            s = analyzer.polarity_scores(h)
            out[h] = s['compound']
        except Exception:
            out[h] = 0.0
    return out
