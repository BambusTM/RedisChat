import asyncio
import redis.asyncio as redis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

app = FastAPI()
redis_url = "redis://redis:6379"
redis_channel = "chat"
connections = set()

@app.on_event("startup")
async def startup():
    app.state.redis = redis.from_url(redis_url)
    asyncio.create_task(redis_listener())

async def redis_listener():
    pubsub = app.state.redis.pubsub()
    await pubsub.subscribe(redis_channel)
    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
        if message:
            await broadcast_message(message["data"].decode("utf-8"))

async def broadcast_message(message: str):
    for connection in connections:
        try:
            await connection.send_text(message)
        except:
            connections.remove(connection)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await app.state.redis.publish(redis_channel, data)
    except WebSocketDisconnect:
        connections.remove(websocket)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
