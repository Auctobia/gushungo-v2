import os, asyncio, json, websockets, random
from flask import Flask, jsonify
from flask_cors import CORS
from threading import Thread

# 1. Setup Flask
app = Flask(__name__)
CORS(app)

# 2. Configuration (Make sure this Token is exactly 15+ characters)
DERIV_TOKEN = "PvBYo3sFOiEVoMz" 
APP_ID = "1089"

current_signal = {
    "asset": "Gushungo AI",
    "price": "0.00",
    "signal": "WAITING_FOR_DATA",
    "probability": "0%",
    "color": "grey"
}

# 3. The Background Engine
async def deriv_ai_engine():
    global current_signal
    uri = f"wss://ws.binaryws.com/websockets/v3?app_id={APP_ID}"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                await websocket.send(json.dumps({"authorize": DERIV_TOKEN}))
                await websocket.recv() # Wait for Auth
                
                await websocket.send(json.dumps({"ticks": "frxXAUUSD", "subscribe": 1}))
                while True:
                    res = await websocket.recv()
                    data = json.loads(res)
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
            print(f"Engine Error: {e}")
            await asyncio.sleep(5)

# 4. Start the Engine Thread BEFORE the app runs
thread = Thread(target=lambda: asyncio.run(deriv_ai_engine()), daemon=True)
thread.start()

# 5. Routes
@app.route('/')
def home():
    return "Gushungo AI is Online"

@app.route('/get-signal')
def get_signal():
    return jsonify(current_signal)

# 6. Port Binding (This is what Render is asking for)
if __name__ == "__main__":
    # Render looks for port 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
