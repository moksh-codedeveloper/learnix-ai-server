from fastapi import FastAPI 
from dotenv import load_dotenv
import uvicorn
import os
load_dotenv()
app = FastAPI()
@app.get("/")
def read_root():
    return {
        "message": "AI server is up"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
    read_root()