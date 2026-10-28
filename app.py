import os
from flask import Flask, request
import requests

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN") # Token喺PythonAnywhere度設定，唔寫喺Code度

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.json
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"].strip()
        # 你原本700查股價嘅邏輯放返呢度
        if text == "700":
            reply = "騰訊 700: 測試中 (GitHub版 V3已啟動)"
        else:
            reply = f"你打咗: {text}"
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={reply}")
    return "ok"

@app.route("/")
def home():
    return "HK Bot V3 GitHub版運行中"