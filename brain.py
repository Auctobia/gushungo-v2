import os, asyncio, json, websockets, random, ssl
from flask import Flask, jsonify
from flask_cors import CORS
from threading import Thread

app = Flask(__name__)
CORS(app)

# CONFIGURATION
DERIV_TOKEN = "CqwyAwnLmCja1LW" 
APP_ID = "1089"

# Global flag to track if the brain is active
brain_active = False

current_signal = {
    "asset": "Gushungo AI",
    "price": "0.00",
    "signal": "OFFLINE", # Default state
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
            current_signal["signal"] = "CONNECTING..."
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                # 1. Authorize
                await websocket.send(json.dumps({"authorize": DERIV_TOKEN}))
                auth = await websocket.recv()
                
                if "error" in json.loads(auth):
                    current_signal["signal"] = "INVALID_TOKEN"
                    return # Stop if token is bad

                # 2. Subscribe
                await websocket.send(json.dumps({"ticks": "frxXAUUSD", "subscribe": 1}))
                current_signal["signal"] = "WAITING_FOR_DATA"
                
                while True:
                    data = json.loads(await websocket.recv())
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
            print(f"Error: {e}")
            current_signal["signal"] = "CONNECTION_LOST"
            await asyncio.sleep(5)

# --- THE MAGIC TRIGGER ---
@app.route('/get-signal')
def get_signal():
    global brain_active
    
    # Check if the brain is sleeping. If yes, WAKE IT UP!
    if not brain_active:
        print("--- WAKING UP THE BRAIN ---")
        t = Thread(target=lambda: asyncio.run(deriv_ai_engine()))
        t.daemon = True
        t.start()
        brain_active = True
        return jsonify({"message": "Brain is waking up... Refresh in 5 seconds", "signal": "STARTING..."})
    
    return jsonify(current_signal)

@app.route('/')
def home():
    return "Gushungo AI Server"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
