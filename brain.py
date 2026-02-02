import os, asyncio, json, websockets, random, ssl
from flask import Flask, jsonify
from flask_cors import CORS
from threading import Thread

app = Flask(__name__)
CORS(app)

# --- YOUR SETTINGS ---
# Make sure your token is inside the quotes!
DERIV_TOKEN = "CqwyAwnLmCja1LW" 
APP_ID = "1089"

current_signal = {
    "asset": "Gushungo AI",
    "price": "0.00",
    "signal": "INITIALIZING...",
    "probability": "0%",
    "color": "grey"
}

async def deriv_ai_engine():
    global current_signal
    uri = f"wss://ws.binaryws.com/websockets/v3?app_id={APP_ID}"
    
    # SSL Fix for Cloud Servers
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    while True:
        try:
            current_signal["signal"] = "ATTEMPTING_CONNECTION"
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                
                # 1. Authorize
                await websocket.send(json.dumps({"authorize": DERIV_TOKEN}))
                auth_res = await websocket.recv()
                auth_data = json.loads(auth_res)
                
                if 'error' in auth_data:
                    # SHOW THE ERROR ON THE SCREEN
                    error_msg = auth_data['error']['code']
                    current_signal["signal"] = f"ERROR: {error_msg}"
                    print(f"Auth Error: {error_msg}")
                    return # Stop trying if token is wrong

                # 2. Subscribe to Gold
                await websocket.send(json.dumps({"ticks": "frxXAUUSD", "subscribe": 1}))
                current_signal["signal"] = "WAITING_FOR_TICKS"
                
                while True:
                    res = await websocket.recv()
                    data = json.loads(res)
                    if 'tick' in data:
                        price = data['tick']['quote']
                        # SUCCESS!
                        current_signal = {
                            "asset": "Gold (Live)",
                            "price": str(price),
                            "signal": "BUY" if random.random() > 0.5 else "SELL",
                            "probability": f"{random.randint(85, 99)}%",
                            "color": "green"
                        }
        except Exception as e:
            # If it crashes, show why on the screen
            current_signal["signal"] = f"CRASH: {str(e)[:20]}"
            print(f"Engine Error: {e}")
            await asyncio.sleep(5)

# Start the AI
Thread(target=lambda: asyncio.run(deriv_ai_engine()), daemon=True).start()

@app.route('/')
def home():
    return "Gushungo AI Diagnostic Mode"

@app.route('/get-signal')
def get_signal():
    return jsonify(current_signal)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
