import os, requests, json
from flask import Flask, request

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")

def get_price(code):
    try:
        c = f"{int(code):04d}.HK" if code.isdigit() else code
        if len(c)==4: c = f"0{c}" # 700 -> 0700.HK
        if ".HK" not in c: c = f"{int(code):04d}.HK"
        # 讀自己GitHub的json，一定在白名單
        url = "https://raw.githubusercontent.com/wanszekit-lgtm/hk-stock-bot/main/prices.json"
        r = requests.get(url, timeout=10)
        data = r.json()
        if c in data:
            p = data[c]
            return f"📈 {c} (GitHub自動更新)\n現價: ${p['close']}\n開: {p['open']} 高: {p['high']} 低: {p['low']}\n更新: {data.get('_time','')[:16]}"
        else:
            return f"{c} 未在自動列表，支援: 0700, 0005, 2800, 0001, 0388\n(可在update.yml加更多)"
    except Exception as e:
        return f"讀取GitHub價格失敗: {e}"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.json
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"].strip()
        reply = get_price(text) if text.isdigit() else "打 700 / 5 / 2800 試下"
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", params={"chat_id": chat_id, "text": reply})
    return "ok"

@app.route("/")
def home():
    return "V6 GitHub Action版 運行中"
