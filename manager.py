from fastapi import WebSocket
from model import PredictionModel
from multiprocess import Pool

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[WebSocket, PredictionModel] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = PredictionModel()

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection, _ in self.active_connections:
            await connection.send_text(message)
    
    async def process_video(self, websocket: WebSocket):
        frames = []
        with Pool(3) as p:
            while True:
                data = await websocket.receive_text()
                frames.append(data)

                if len(frames) >= 30:
                    p.apply_async(self.__process_frames, (frames, websocket))
                    frames = []
    
    async def __process_frames(self, frames, websocket):
        text = self.active_connections[websocket].predictISL(frames)
        await websocket.send_text(text)