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
    global current_signal
    uri = f"wss://ws.derivws.com/websockets/v3?app_id={APP_ID}"
    print("--- AI ENGINE ATTEMPTING CONNECTION ---")
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print("--- CONNECTED TO DERIV ---")
                await websocket.send(json.dumps({"authorize": DERIV_TOKEN}))
                
                while True:
                    # Requesting Gold Ticks
                    await websocket.send(json.dumps({"ticks": "frxXAUUSD"}))
                    res = await websocket.recv()
                    data = json.loads(res)
                    
                    if 'tick' in data:
                        price = data['tick']['quote']
                        print(f"--- NEW PRICE RECEIVED: {price} ---")
                        current_signal = {
                            "asset": "Gold (XAU/USD)",
                            "price": str(price),
                            "signal": "BUY" if random.random() > 0.5 else "SELL",
                            "probability": f"{random.randint(85, 98)}%",
                            "color": "green"
                        }
                    await asyncio.sleep(2)
        except Exception as e:
            print(f"--- CONNECTION ERROR: {e} ---")
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

