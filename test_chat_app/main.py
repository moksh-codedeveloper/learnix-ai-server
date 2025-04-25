import os
import uuid
import requests
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import uvicorn 
app = FastAPI()
load_dotenv()
TOGETHER_API_KEY = os.getenv("YOUR_API_KEY")

# Add CORS middleware for WebSocket support
origins = [
    "http://localhost",  # Allow localhost
    "http://localhost:3000",  # Allow your frontend port if you're running it separately
    "*",  # Allow any origin (you can limit this for more security)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of origins that can access the server
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods, including WebSocket
    allow_headers=["*"],  # Allow any headers
)

# ✅ Request models
class ChatRequest(BaseModel):
    message: str

class SummarizationRequest(BaseModel):
    text: str

# ✅ Common AI Call Function
def call_together_ai(message: str):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {"Authorization": f"Bearer {TOGETHER_API_KEY}", "Content-Type": "application/json"}
    payload = {
        # meta-llama/Llama-3.3-70B-Instruct-Turbo-Free
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 500,
        "temperature": 0.2
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    print("Together AI Response:", data)  # Debugging

    if "choices" in data and len(data["choices"]) > 0:
        return data["choices"][0].get("message", {}).get("content", "No response")
    else:
        return "Error: No valid response from AI"

# ✅ Chatbot Endpoint (Regular POST)
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response_text = call_together_ai(request.message)
        print("Final Response:", response_text)  # Debugging
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ WebSocket Endpoint
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept WebSocket connection
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            print(f"Received from client: {data}")

            # Call Together AI
            response_text = call_together_ai(data)
            print("Final Response:", response_text)  # Debugging

            # Send response back to client via WebSocket
            await websocket.send_text(response_text)

    except WebSocketDisconnect:
        print("Client disconnected")
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
