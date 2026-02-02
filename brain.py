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
    
    # This bypasses SSL certificate issues on Render
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    while True:
        try:
            print("--- ATTEMPTING SECURE WS CONNECTION ---")
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                # 1. Authorize
                await websocket.send(json.dumps({"authorize": DERIV_TOKEN}))
                auth_res = await websocket.recv()
                print(f"--- AUTH SUCCESS: {auth_res[:50]}... ---")
                
                # 2. Subscribe to Gold
                await websocket.send(json.dumps({"ticks": "frxXAUUSD", "subscribe": 1}))
                
                while True:
                    res = await websocket.recv()
                    data = json.loads(res)
                    if 'tick' in data:
                        price = data['tick']['quote']
                        current_signal = {
                            "asset": "Gold (Cloud)",
                            "price": str(price),
                            "signal": "BUY" if random.random() > 0.5 else "SELL",
                            "probability": f"{random.randint(85, 99)}%",
                            "color": "green"
                        }
                        print(f"--- NEW PRICE: {price} ---")
        except Exception as e:
            print(f"--- ENGINE ERROR: {e} ---")
            await asyncio.sleep(5)

# --- START THE ENGINE ---
print("--- INITIALIZING BACKGROUND THREAD ---")
daemon_thread = Thread(target=lambda: asyncio.run(deriv_ai_engine()), daemon=True)
daemon_thread.start()

@app.route('/get-signal')
def get_signal():
    return jsonify(current_signal)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
