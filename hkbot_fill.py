import os, requests, time, yfinance as yf, pandas as pd
from datetime import datetime
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
STOCKS = ["0700.HK","9988.HK","3690.HK","9618.HK","1024.HK","1810.HK","2015.HK","9999.HK","0992.HK","2382.HK","2800.HK","1299.HK","2318.HK","0005.HK","1211.HK","2020.HK"]
def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=15)
def check(ticker):
    try:
        df = yf.download(ticker, period="20d", interval="1d", progress=False, auto_adjust=True)
        if len(df) < 15: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        close, vol = df['Close'], df['Volume']
        ma5, ma20 = close.rolling(5).mean().iloc[-1], close.rolling(20).mean().iloc[-1]
        last, prev = close.iloc[-1], close.iloc[-2]
        avg_v, last_v = vol.rolling(10).mean().iloc[-2], vol.iloc[-1]
        chg = (last-prev)/prev*100
        vr = last_v/avg_v if avg_v>0 else 1
        if last > ma5 and last > ma20 and vr > 1.8 and chg > 2:
            return f"🚀 放量突破: *{ticker}* 升 {chg:.2f}% 量比 x{vr:.1f}\n現價: {last:.2f}"
        if chg > 4:
            return f"🔥 強勢急升: *{ticker}* 升 {chg:.2f}%\n現價: {last:.2f}"
    except: return None
send(f"✅ *HK Bot 已啟動* {datetime.now().strftime('%H:%M')}")
for s in STOCKS:
    r = check(s)
    if r: send(r); time.sleep(1)
send("📊 掃描完成")
