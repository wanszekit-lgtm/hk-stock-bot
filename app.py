import os
from flask import Flask, request
import requests
import yfinance as yf

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")

def get_price(code):
    ticker = f"{int(code):04d}.HK" if code.isdigit() else code
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2d")
        if len(hist) < 1:
            return f"搵唔到 {ticker}"
        price = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2] if len(hist) > 1 else price
        change = price - prev
        pct = (change / prev * 100) if prev else 0
        return f"📈 {ticker}\n現價: ${price:.2f}\n升跌: {change:+.2f} ({pct:+.2f}%)"
    except Exception as e:
        return f"搵唔到 {ticker}: {e}"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.json
    if "message" in data and "text" in data["message"]:
        # 呢度係修正重點！
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"].strip()
        
        if text.isdigit():
            reply = get_price(text)
            if text == "700":
                reply = f"騰訊 {reply}"
        else:
            reply = f"你打咗: {text}，試下打 700 或 5"

        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", params={"chat_id": chat_id, "text": reply})
    return "ok"

@app.route("/")
def home():
    return "HK Bot V3 正式版運行中 - 已修正 chat_id"
