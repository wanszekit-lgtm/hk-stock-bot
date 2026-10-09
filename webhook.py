from flask import Flask, request
import os, requests, json
from datetime import datetime

app = Flask(__name__)
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 模擬倉設定
START_CAPITAL = 100000.0
PORTFOLIO_FILE = "portfolio.json"

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)

def load_pf():
    try:
        with open(PORTFOLIO_FILE, 'r') as f: return json.load(f)
    except:
        return {"cash": START_CAPITAL, "positions": {}, "trades": []}

def save_pf(pf):
    with open(PORTFOLIO_FILE, 'w') as f: json.dump(f, f)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True) or {}
    ticker = data.get('ticker', '0700.HK').upper()
    action = data.get('action', 'BUY').upper() # BUY or SELL
    price = float(data.get('price', 0))
    
    pf = load_pf()
    
    if action == "BUY" and pf["cash"] > price * 100: # 假設1手100股
        qty = int((pf["cash"] * 0.2) // price // 100 * 100) # 每次用20%倉位
        if qty > 0:
            cost = qty * price
            pf["cash"] -= cost
            pf["positions"][ticker] = pf["positions"].get(ticker, 0) + qty
            pf["trades"].append(f"{datetime.now().strftime('%m-%d %H:%M')} BUY {ticker} {qty}股 @ {price}")
            save_pf(pf)
            send(f"🤖 *模擬買入成交*\n📌 {ticker} {qty}股 @ {price}\n💰 成本: ${cost:.0f}\n💵 剩餘現金: ${pf['cash']:.0f}\n📝 {data.get('message','')}")
    
    elif action == "SELL" and ticker in pf["positions"]:
        qty = pf["positions"][ticker]
        pf["cash"] += qty * price
        del pf["positions"][ticker]
        pf["trades"].append(f"{datetime.now().strftime('%m-%d %H:%M')} SELL {ticker} {qty}股 @ {price}")
        save_pf(pf)
        total = pf["cash"] + sum([100*400 for _ in pf["positions"]]) # 簡化
        pnl = pf["cash"] + qty*price - START_CAPITAL
        send(f"💸 *模擬賣出成交*\n📌 {ticker} {qty}股 @ {price}\n💰 套現: ${qty*price:.0f}\n📊 總P&L: ${pnl:.0f}\n💵 現金: ${pf['cash']:.0f}")

    return "OK", 200

@app.route('/')
def home():
    pf = load_pf()
    return f"Running. Cash: {pf['cash']} Positions: {pf['positions']}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
