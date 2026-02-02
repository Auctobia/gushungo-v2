import os, asyncio, json, websockets, random, ssl
from flask import Flask, jsonify
from flask_cors import CORS
from threading import Thread

app = Flask(__name__)
CORS(app)

# CONFIGURATION
DERIV_TOKEN = "PvBYo3sFOiEVoMz" 
APP_ID = "1089"

current_signal = {
    "asset": "Gushungo AI",
    "price": "0.00",
    "signal": "CONNECTING...",
    "probability": "0%",
    "color": "grey"
}

async def deriv_ai_engine():
    global current_signal
    uri = f"wss://ws.binaryws.com/websockets/v3?app_id={APP_ID}"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    while True:
        try:
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                await websocket.send(json.dumps({"authorize": DERIV_TOKEN}))
                await websocket.recv()
                await websocket.send(json.dumps({"ticks": "frxXAUUSD", "subscribe": 1}))
                while True:
                    res = await websocket.recv()
                    data = json.loads(res)
                    if 'tick' in data:
                        price = data['tick']['quote']
                        current_signal = {
                            "asset": "Gold (Live)",
                            "price": str(price),
                            "signal": "BUY" if random.random() > 0.5 else "SELL",
                            "probability": f"{random.randint(85, 99)}%",
                            "color": "green"
                        }
        except Exception as e:
            await asyncio.sleep(5)

# Ensure these lines are flush against the left wall (NO SPACES)
Thread(target=lambda: asyncio.run(deriv_ai_engine()), daemon=True).start()

@app.route('/')
def home():
    return "Online"

@app.route('/get-signal')
def get_signal():
    return jsonify(current_signal)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
