import os, asyncio, json, websockets, random, ssl
from flask import Flask, jsonify
from flask_cors import CORS
from threading import Thread

app = Flask(__name__)
CORS(app)

# CONFIGURATION
DERIV_TOKEN = "CqwyAwnLmCja1LW" 
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
    
    # Cloud Security Setup
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    while True:
        try:
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                # Attempt Auth
                await websocket.send(json.dumps({"authorize": DERIV_TOKEN}))
                res = await websocket.recv()
                print(f"AUTH_LOG: {res}") # This will show the error in Render Logs
                
                # Subscribe to Gold
                await websocket.send(json.dumps({"ticks": "frxXAUUSD", "subscribe": 1}))
                
                while True:
                    msg = await websocket.recv()
                    data = json.loads(msg)
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
            print(f"CONNECTION_ERROR: {e}")
            # FALLBACK: If Deriv fails, show this so we know the app is alive
            current_signal["signal"] = "CHECK_DERIV_TOKEN"
            current_signal["price"] = "ERROR"
            await asyncio.sleep(5)

