import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
import redis.asyncio as redis

app = FastAPI()

# Redis configuration
redis_url = "redis://localhost:6379"
redis_channel = "chat"

# Maintain a set of active WebSocket connections
connections = set()

@app.on_event("startup")
async def startup():
    # Initialize the Redis client and start the background task to listen for messages
    app.state.redis = redis.from_url(redis_url)
    asyncio.create_task(redis_listener())

async def redis_listener():
    pubsub = app.state.redis.pubsub()
    await pubsub.subscribe(redis_channel)
    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
        if message:
            data = message["data"]
            # Decode bytes if needed
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            # Broadcast the received message to all connected clients
            await broadcast_message(data)
        await asyncio.sleep(0.01)

async def broadcast_message(message: str):
    # Remove any connection that fails to send the message
    to_remove = []
    for connection in connections:
        try:
            await connection.send_text(message)
        except Exception:
            to_remove.append(connection)
    for conn in to_remove:
        connections.remove(conn)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.add(websocket)
    try:
        while True:
            # Wait for a message from the client
            data = await websocket.receive_text()
            # Assume data is a JSON string with 'username' and 'message'
            # Publish the data to the Redis channel
            await app.state.redis.publish(redis_channel, data)
    except WebSocketDisconnect:
        connections.remove(websocket)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
