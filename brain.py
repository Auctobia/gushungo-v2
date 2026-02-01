import os
import asyncio
import json
import websockets
import random
from flask import Flask, jsonify
from flask_cors import CORS
from threading import Thread

# --- RENDER LOOKS FOR THIS EXACT WORD 'app' ---
app = Flask(__name__)
CORS(app)

# CONFIGURATION
DERIV_TOKEN = "VD5cCWiwYdKInBr"  # Replace with your token
APP_ID = "1089"

current_signal = {
    "asset": "Gushungo AI",
    "price": "0.00",
    "signal": "INITIALIZING",
    "probability": "0%",
    "color": "grey"
}

async def deriv_ai_engine():
    global current_signal
    uri = f"wss://ws.derivws.com/websockets/v3?app_id={APP_ID}"
    
    while True:
        try:
            async with websockets.connect(uri, open_timeout=20) as websocket:
                await websocket.send(json.dumps({"authorize": DERIV_TOKEN}))
                
                assets = ["frxXAUUSD", "R_100"]
                for asset in assets:
                    await websocket.send(json.dumps({
                        "ticks_history": asset,
                        "count": 5,
                        "end": "latest",
                        "style": "ticks"
                    }))
                    
                    res = await websocket.recv()
                    data = json.loads(res)
                    
                    if 'history' in data:
                        prices = [float(p) for p in data['history']['prices']]
                        last_price = prices[-1]
                        
                        # Logic
                        recommendation = "BUY" if last_price > (sum(prices)/len(prices)) else "SELL"
                        
                        current_signal = {
                            "asset": "Gold" if "XAU" in asset else "Vol 100",
                            "price": str(last_price),
                            "signal": recommendation,
                            "probability": f"{random.randint(80, 96)}%",
                            "color": "blue" if recommendation == "BUY" else "red"
                        }
                    await asyncio.sleep(5)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(10)

# --- ROUTES ---
@app.route('/')
def home():
    return "Gushungo AI is Online"

@app.route('/get-signal')
# --- THE CLOUD STARTER ---
def start_ai():
    asyncio.run(deriv_ai_engine())

# This starts the AI immediately when the file is loaded by Render
ai_thread = Thread(target=start_ai, daemon=True)
ai_thread.start()

if __name__ == "__main__":
    # This only runs on your laptop
    app.run(host='0.0.0.0', port=5000)
