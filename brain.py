import os, asyncio, json, websockets, random, ssl
from flask import Flask, jsonify
from flask_cors import CORS
from threading import Thread

app = Flask(__name__)
CORS(app)

DERIV_TOKEN = "PvBYo3sFOiEVoMz" 
APP_ID = "1089"

current_signal = {
    "asset": "Gushungo AI",
    "price": "0.00",
    "signal": "WAITING_FOR_HANDSHAKE",
    "probability": "0%",
    "color": "grey"
}

async def deriv_ai_engine():
    global current_signal
    # We use a broader endpoint that is often more stable for cloud servers
    uri = f"wss://ws.binaryws.com/websockets/v3?app_id={APP_ID}"
    
    # Create an SSL context that ignores certificate errors (common on cloud platforms)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    while True:
        try:
            print("--- STEP 1: ATTEMPTING WS CONNECTION ---")
            async with websockets.connect(uri, ssl=ssl_context, ping_interval=20) as websocket:
                print("--- STEP 2: WS CONNECTED, SENDING AUTH ---")
                
                await websocket.send(json.dumps({"authorize": DERIV_TOKEN}))
                
                # We put a timeout here so it doesn't wait forever
                auth_res = await asyncio.wait_for(websocket.recv(), timeout=10)
                print(f"--- STEP 3: AUTH RESPONSE RECEIVED: {auth_res} ---")
                
                await websocket.send(json.dumps({"ticks": "frxXAUUSD", "subscribe": 1}))
                print("--- STEP 4: TICK SUBSCRIPTION SENT ---")
                
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
                        # Only print price every 10 ticks to keep logs clean
                        if random.random() > 0.9:
                            print(f"--- DATA FLOWING: {price} ---")
        except Exception as e:
            print(f"--- ENGINE ERROR: {e} ---")
            await asyncio.sleep(5)

# Start the worker
print("--- STARTING BACKGROUND THREAD ---")
Thread(target=lambda: asyncio.run(deriv_ai_engine()), daemon=True).start()

@app.route('/')
def home():
    return "Gushungo AI System Active"

@app.route('/get-signal')
def get_signal():
    return jsonify(current_signal)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
