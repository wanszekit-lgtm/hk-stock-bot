import os, requests, yfinance as yf, pandas as pd
from tradingview_ta import TA_Handler, Interval
TOKEN=os.getenv("TOKEN"); CHAT_ID=os.getenv("CHAT_ID")
def send(m): requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id":CHAT_ID,"text":m,"parse_mode":"Markdown"})
def check(t):
    try:
        tv=TA_Handler(symbol=t.replace(".HK",""), exchange="HKEX", screener="hongkong", interval=Interval.INTERVAL_1_DAY).get_analysis().summary
        if tv["RECOMMENDATION"] not in ["BUY","STRONG_BUY"]: return None
        df=yf.download(t, period="20d", progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex): df.columns=df.columns.get_level_values(0)
        last=df['Close'].iloc[-1]; prev=df['Close'].iloc[-2]
        vr=df['Volume'].iloc[-1]/df['Volume'].rolling(10).mean().iloc[-2]
        chg=(last-prev)/prev*100
        if vr>1.5 and chg>1: return f"✅ *{t}* {tv['RECOMMENDATION']} 升{chg:.1f}% 量比x{vr:.1f} 現價{last:.1f}"
    except: return None
send("✅ HK Bot V3 已啟動")
for s in ["0700.HK","9988.HK","3690.HK","1810.HK","2800.HK","1211.HK"]:
    r=check(s)
    if r: send(r)
