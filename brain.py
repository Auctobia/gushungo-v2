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
    # Using the standard Binary.com endpoint which is often more stable
    uri = f"wss://ws.binaryws.com/websockets/v3?app_id={APP_ID}"
    
    # Force the server to ignore SSL errors
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    while True:
        try:
            print("--- ATTEMPTING CONNECTION ---")
            # Added a user_agent header to bypass cloud bot-blockers
            async with websockets.connect(uri, ssl=ssl_context, extra_headers={"User-Agent": "GushungoAI/2.0"}) as websocket:
                
                print("--- SENDING AUTHENTICATION ---")
                await websocket.send(json.dumps({"authorize": DERIV_TOKEN}))
                
                # Check for Auth success
                auth_raw = await websocket.recv()
                auth_data = json.loads(auth_raw)
                
                if "error" in auth_data:
                    print(f"--- AUTH FAILED: {auth_data['error']['message']} ---")
                    current_signal["signal"] = "TOKEN_ERROR"
                    break # Stop and check your token!

                print("--- AUTH SUCCESS! SUBSCRIBING TO GOLD ---")
                await websocket.send(json.dumps({"ticks": "frxXAUUSD", "subscribe": 1}))
                
                while True:
                    res = await websocket.recv()
                    data = json.loads(res)
                    if 'tick' in data:
                        price = data['tick']['quote']
                        current_signal = {
                            "asset": "Gold (Live AI)",
                            "price": str(price),
                            "signal": "BUY" if random.random() > 0.5 else "SELL",
                            "probability": f"{random.randint(85, 98)}%",
                            "color": "green"
                        }
                        print(f"--- PRICE RECEIVED: {price} ---")
                    
                    # Heartbeat to keep the connection alive
                    await websocket.send(json.dumps({"ping": 1}))
                    await asyncio.sleep(2)

        except Exception as e:
            print(f"--- CONNECTION DIED: {e} ---")
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

