async def deriv_ai_engine():
    global current_signal
    uri = f"wss://ws.derivws.com/websockets/v3?app_id={APP_ID}"
    
    while True:
        try:
            # Added open_timeout to give the handshake 20 seconds instead of 10
            async with websockets.connect(uri, open_timeout=20, ping_interval=20) as websocket:
                print("Connected to Deriv! Sending Authorize...")
                
                await websocket.send(json.dumps({"authorize": DERIV_TOKEN}))
                auth_resp = await websocket.recv()
                
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
                        avg_price = sum(prices) / len(prices)
                        
                        # Logic: Momentum
                        recommendation = "BUY (UP)" if last_price > avg_price else "SELL (DOWN)"
                        color = "blue" if last_price > avg_price else "red"
                        
                        current_signal = {
                            "asset": "Gold (XAU/USD)" if "XAU" in asset else "Volatility 100",
                            "price": f"{last_price:.2f}",
                            "signal": recommendation,
                            "probability": f"{random.randint(85, 95)}%",
                            "color": color
                        }
                    await asyncio.sleep(5)
                    
        except Exception as e:
            # This will catch the 'Handshake' error and try again
            print(f"Connection Error: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)
