import os
import requests

TOKEN = os.getenv('BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or "8754867964:AAEYLfChXr8bYjlUbMmUQh-1jYG1DPiOQBU"
CHAT_ID = os.getenv('CHAT_ID') or "YOUR_CHAT_ID"

def send(m):
    if not TOKEN or "None" in str(TOKEN):
        print(f"SKIP SEND (No TOKEN): {m}")
        return
    try:
        # PythonAnywhere 免費版要用Proxy，唔用就會503
        # Web環境會自動處理，Console就Skip
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": m, "parse_mode": "Markdown"},
                      timeout=10)
    except Exception as e:
        print(f"Send failed (ignore): {e}")

# 開機通知唔好喺import時就send，會搞死WSGI
# send(" HK Bot V3 已啟動")  <- 呢行要刪咗或者加 #
