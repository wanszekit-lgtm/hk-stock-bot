import os
from flask import Flask, request
import requests
import csv
import io
import urllib.parse

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")

def fetch_with_fallback(original_url):
    # 3個免費代理，逐個試
    encoded = urllib.parse.quote(original_url, safe='')
    proxies = [
        f"https://api.allorigins.win/raw?url={encoded}",
        f"https://api.codetabs.com/v1/proxy?quest={encoded}",
        f"https://corsproxy.io/?{encoded}",
        original_url  # 最後直接試stooq本身
    ]
    for p_url in proxies:
        try:
            r = requests.get(p_url, timeout=20)
            if r.status_code == 200 and "Symbol" in r.text:
                return r.text
        except:
            continue
    return None

def get_price(code):
    try:
        clean_code = code.lstrip('0') or '0'
        stooq_url = f"https://stooq.com/q/l/?s={clean_code}.hk&f=sd2t2ohlcv&h&e=csv"
        
        csv_text = fetch_with_fallback(stooq_url)
        if not csv_text:
            return f"📈 {code}.HK\n網絡繁忙(代理Timeout)，請30秒後再試700\n(免費版代理半夜唔穩定)"

        reader = csv.DictReader(io.StringIO(csv_text))
        for row in reader:
            close = row.get('Close', 'N/D')
            if close in ('N/D', '', None):
                return f"📈 {code}.HK 收市後無即時數據，明早再試\n(今日可能未開市)"
            return f"📈 {code}.HK 免費版V5\n現價: ${close}\n開: {row.get('Open')} 高: {row.get('High')} 低: {row.get('Low')}\n成交量: {row.get('Volume')}\n來源: stooq"
        return f"搵唔到 {code}.HK"
    except Exception as e:
        return f"V5出錯 {code}: {e}"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.json
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"].strip()
        reply = get_price(text) if text.isdigit() else f"試下打 700 / 2800 / 5"
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", params={"chat_id": chat_id, "text": reply})
    return "ok"

@app.route("/")
def home():
    return "HK Bot V5 三代理備份版運行中"
