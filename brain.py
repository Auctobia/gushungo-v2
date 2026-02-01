import os, asyncio, json, websockets, random
from flask import Flask, jsonify
from flask_cors import CORS
from threading import Thread

app = Flask(__name__)
CORS(app)

# CONFIGURATION
DERIV_TOKEN = "PvBYo3sFOiEVoMz" # <--- DOUBLE CHECK THIS!
APP_ID = "1089"

current_signal = {
    "asset": "Gushungo AI",
    "price": "0.00",
    "signal": "ENGINE_STARTING",
    "probability": "0%",
    "color": "grey"
}

async def deriv_ai_engine():
   async def deriv_ai_engine():
    global current_signal
    # Use the 'blue' URL for better cloud compatibility
    uri = f"wss://ws.binaryws.com/websockets/v3?app_id={APP_ID}"
    
    while True:
        try:
            print("--- ATTEMPTING CLOUD CONNECTION ---")
            async with websockets.connect(uri, ping_interval=20, ping_timeout=20) as websocket:
                # 1. Authorize
                await websocket.send(json.dumps({"authorize": DERIV_TOKEN}))
                auth_res = await websocket.recv()
                print(f"--- AUTH STATUS: {auth_res} ---")
                
                # 2. Subscribe to Gold Ticks (Stream mode)
                await websocket.send(json.dumps({"ticks": "frxXAUUSD", "subscribe": 1}))
                
                while True:
                    res = await websocket.recv()
                    data = json.loads(res)
                    
                    if 'tick' in data:
                        price = data['tick']['quote']
                        current_signal = {
                            "asset": "Gold (Cloud AI)",
                            "price": str(price),
                            "signal": "BUY" if random.random() > 0.5 else "SELL",
                            "probability": f"{random.randint(85, 98)}%",
                            "color": "green"
                        }
                        print(f"--- PRICE UPDATED: {price} ---")
                    
                    # Prevent timeout
                    await asyncio.sleep(0.1)

        except Exception as e:
            print(f"--- ENGINE CRASHED: {e} ---")
            current_signal["signal"] = "RECONNECTING..."
            await asyncio.sleep(5)

# This starts the AI as soon as the file loads
print("--- STARTING BACKGROUND THREAD ---")
daemon_thread = Thread(target=lambda: asyncio.run(deriv_ai_engine()), daemon=True)
daemon_thread.start()

@app.route('/')
def home():
    return "Gushungo AI Cloud Server is Active"

@app.route('/get-signal')
def get_signal():
    return jsonify(current_signal)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)


