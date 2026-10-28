from flask import Flask, request, jsonify
import json, os, datetime

app = Flask(__name__)

# 讀 prices.json
def load_prices():
    try:
        if os.path.exists('prices.json'):
            with open('prices.json','r') as f:
                return json.load(f)
    except: pass
    return {}

PRICES = load_prices()
NAMES = {
 "0700.HK":"騰訊控股","2800.HK":"盈富基金","0005.HK":"匯豐控股",
 "0941.HK":"中國移動","3690.HK":"美團","9988.HK":"阿里巴巴",
 "0939.HK":"建設銀行","1299.HK":"友邦保險","0388.HK":"港交所","2318.HK":"中國平安"
}

@app.route('/')
def home():
    return f"Bot OK! Prices loaded: {len(PRICES)} Last: {PRICES.get('_updated','')}"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    msg = ""
    try:
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    except: 
        return jsonify({"status":"ok"})
    
    code = ''.join(filter(str.isdigit, msg))
    reply = "請輸入港股號碼，例如: 700"

    if code:
        # 支援 700 -> 0700.HK
        if len(code) <=4:
            full = code.zfill(4) + ".HK"
        else:
            full = code + ".HK" if ".HK" not in code else code

        if full in PRICES:
            price = PRICES[full]
            name = NAMES.get(full, full)
            updated = PRICES.get('_updated','今日')[:10]
            reply = f"{code} {name}\n收市價 ${price}\n更新: {updated}\n(真實股價，秒回模式)"
        else:
            reply = f"搵唔到 {code}，試下 700, 2800, 5, 941, 3690"

    # 回覆 WhatsApp 用 (你原本個send邏輯要保留)
    # 如果你用緊 Meta API，回覆會由呢度處理
    print(f"User:{msg} -> Reply:{reply}")

    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run()
