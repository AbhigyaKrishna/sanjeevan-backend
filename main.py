from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from manager import ConnectionManager
from pydantic import BaseModel
import boto3
from dotenv import load_dotenv


load_dotenv()


app = FastAPI()
s3 = boto3.resource('s3')
bucket = s3.Bucket('voicevideo')
items = [item.key.split('.')[0] for item in bucket.objects.all()]
url = os.getenv('AWS_BUCKET_URL')


@app.get("/")
async def root():
    return {"message": "Hello World"}

manager = ConnectionManager()


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
    tokens = body.text.split(" ")
    tokens = [word if word in items else 'acting' for word in tokens]
    urls = {word: url + word + '.mp4' for word in tokens}
    return {
        'text': ' '.join(tokens),
        'urls': urls
    }

