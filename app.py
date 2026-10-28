import json, os, requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN") or "YOUR_TELEGRAM_TOKEN_HERE"  # 你如果set咗env就唔使改
GITHUB_JSON = "https://raw.githubusercontent.com/KitMonaAndAd/hk-stock-bot/main/prices.json"

NAMES = {
 "0700.HK":"騰訊控股","2800.HK":"盈富基金","0005.HK":"匯豐控股",
 "0941.HK":"中國移動","3690.HK":"美團","9988.HK":"阿里巴巴",
 "0939.HK":"建設銀行","1299.HK":"友邦保險","0388.HK":"港交所","2318.HK":"中國平安"
}

def load_prices():
    # 1. 先試本地
    try:
        if os.path.exists("prices.json"):
            with open("prices.json","r") as f:
                d=json.load(f)
                if d: return d
    except Exception as e: print("local load fail",e)
    # 2. 再試GitHub
    try:
        r=requests.get(GITHUB_JSON, timeout=8)
        return r.json()
    except Exception as e:
        print("github load fail", e)
        return {}

def send_msg(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id":chat_id,"text":text}, timeout=10)
    except Exception as e:
        print("send fail", e)

@app.route('/', methods=['GET'])
def home():
    p=load_prices()
    return f"OK {len(p)} stocks, updated {p.get('_updated','')}"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    try:
        msg = data['message']
        chat_id = msg['chat']['id']
        text = msg.get('text','').strip()
    except:
        return "ok"

    PRICES = load_prices()
    
    code_digits = ''.join(filter(str.isdigit, text))
    if not code_digits:
        send_msg(chat_id, "請輸入港股號碼，例如: 700")
        return "ok"

    if len(code_digits) <=4:
        full = code_digits.zfill(4)+".HK"
    else:
        full = code_digits

    if full in PRICES:
        val = PRICES[full]
        # 兼容兩種格式：608.5 或 {"price":608.5}
        if isinstance(val, dict):
            price = val.get('price') or val.get('close') or list(val.values())[0]
        else:
            price = val
        
        name = NAMES.get(full, full)
        updated = PRICES.get('_updated','今日')[:10]
        reply = f"📈 {code_digits} {name}\n收市價 ${price}\n更新: {updated}\n(秒回模式，無需等待)"
    else:
        reply = f"搵唔到 {code_digits}，試下 700, 5, 2800, 941, 3690\n現有: {', '.join(list(PRICES.keys())[:5])}"

    send_msg(chat_id, reply)
    return "ok"
