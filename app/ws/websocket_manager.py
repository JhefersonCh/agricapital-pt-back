from fastapi import WebSocket
from typing import Dict, List

active_connections: Dict[str, List[WebSocket]] = {}

async def connect(websocket: WebSocket, user_id: str):
    await websocket.accept()
    if user_id not in active_connections:
        active_connections[user_id] = []
    active_connections[user_id].append(websocket)

async def disconnect(websocket: WebSocket, user_id: str):
    if user_id in active_connections:
        active_connections[user_id].remove(websocket)
        if not active_connections[user_id]:
            del active_connections[user_id]

async def send_notification(user_id: str, message: dict):
    if user_id in active_connections:
        for connection in active_connections[user_id]:
            await connection.send_json(message)
