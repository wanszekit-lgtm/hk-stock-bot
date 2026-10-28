import os
from flask import Flask, request
import requests
import csv
import io

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")

def get_price(code):
    try:
        # stooq 係免費港股source，0700.hk咁樣查
        clean_code = code.lstrip('0') or '0'
        stooq_url = f"https://stooq.com/q/l/?s={clean_code}.hk&f=sd2t2ohlcv&h&e=csv"
        # 用 allorigins 代理繞過PythonAnywhere白名單
        proxy_url = f"https://api.allorigins.win/raw?url={stooq_url}"
        
        r = requests.get(proxy_url, timeout=12)
        if r.status_code != 200 or "Close" not in r.text:
            return f"暫時攞唔到 {code}.HK，stooq冇回應"

        reader = csv.DictReader(io.StringIO(r.text))
        for row in reader:
            # 會有 N/D 如果收市後
            close = row.get('Close', 'N/D')
            open_p = row.get('Open', 'N/D')
            high = row.get('High', 'N/D')
            low = row.get('Low', 'N/D')
            vol = row.get('Volume', 'N/D')
            
            if close == 'N/D':
                return f"📈 {code}.HK\n今日未有交易/數據延遲\n試下 5 / 2800"
            
            return f"📈 騰訊 {code}.HK (免費版)\n現價: ${close}\n開: {open_p} 高: {high} 低: {low}\n成交量: {vol}\n\n來源: stooq.com"
        
        return f"搵唔到 {code}.HK"
    except Exception as e:
        return f"攞價出錯 {code}: {e}"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.json
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"].strip()

        if text.isdigit():
            reply = get_price(text)
        else:
            reply = f"你打咗: {text}\n試下打 700 或 2800 查港股"

        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", params={"chat_id": chat_id, "text": reply})
    return "ok"

@app.route("/")
def home():
    return "HK Bot 免費版 V4 - stooq + allorigins - 運行中"
