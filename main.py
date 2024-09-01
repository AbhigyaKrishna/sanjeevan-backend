from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from manager import ConnectionManager
from pydantic import BaseModel
import boto3
import os
from dotenv import load_dotenv
import string


load_dotenv()


app = FastAPI()

punctuation = set(string.punctuation)
s3 = boto3.resource(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
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
    tokens = ''.join(ch for ch in body.text if ch not in punctuation)
    tokens = tokens.lower().split(" ")
    tokens = [word if word in items else 'acting' for word in tokens]
    urls = {word: url + word + '.mp4' for word in tokens}
    return {
        'text': ' '.join(tokens),
        'urls': urls
    }

