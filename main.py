from fastapi import FastAPI
from dotenv import load_dotenv
import uvicorn
import os
import asyncio
import websockets

load_dotenv()
app = FastAPI()

# 📡 WebSocket auto-reconnect loop to Node.js
async def connect_to_node_ws():
    uri = "ws://localhost:5000"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print("✅ Connected to Node.js WebSocket server")

                await websocket.send("Hello from FastAPI 🐍")

                while True:
                    message = await websocket.recv()
                    print("📨 Received from Node.js:", message)
        except Exception as e:
            print("❌ Failed to connect to Node.js WebSocket:", e)
            await asyncio.sleep(5)  # Retry every 5 seconds

# 🚀 FastAPI startup event
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(connect_to_node_ws())

# ✅ Root route
@app.get("/")
def read_root():
    return { "message": "AI server is up" }

# 🔥 Run server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
