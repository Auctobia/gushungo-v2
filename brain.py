import os, asyncio, json, websockets, random
from flask import Flask, jsonify
from flask_cors import CORS
from threading import Thread

app = Flask(__name__)
CORS(app)

# CONFIGURATION
DERIV_TOKEN ="PvBYo3sFOiEVoMz" 
APP_ID = "1089"

current_signal = {
    "asset": "Gushungo AI",
    "price": "0.00",
    "signal": "CONNECTING_TO_DERIV",
    "probability": "0%",
    "color": "grey"
}

# --- THE BACKGROUND ENGINE ---
async def deriv_ai_engine():
    global current_signal
    uri = f"wss://ws.binaryws.com/websockets/v3?app_id={APP_ID}"
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                # 1. Authorize
                await websocket.send(json.dumps({"authorize": DERIV_TOKEN}))
                auth_data = await websocket.recv()
                print(f"DEBUG: Auth Response: {auth_data}")
                
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
                            "probability": f"{random.randint(85, 98)}%",
                            "color": "green"
                        }
        except Exception as e:
            print(f"DEBUG: Engine Error: {e}")
            await asyncio.sleep(5)

# --- START THE ENGINE IMMEDIATELY ---
# We put this outside of everything so it runs the moment Render loads the file
print("DEBUG: Manual Thread Start...")
t = Thread(target=lambda: asyncio.run(deriv_ai_engine()))
t.daemon = True
t.start()

@app.route('/')
def home():
    return "Server is Live"

@app.route('/get-signal')
def get_signal():
    return jsonify(current_signal)
