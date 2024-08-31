from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from manager import ConnectionManager
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

manager = ConnectionManager()
clients = {}

@app.websocket("/video")
async def video_websocket(ws: WebSocket):
    await manager.connect(websocket)
    try:
        manager.process_video(ws)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

class Req(BaseModel):
    text: str

@app.post("/translate")
async def translate(body: Req):
    
