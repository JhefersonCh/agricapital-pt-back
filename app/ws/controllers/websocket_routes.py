from fastapi import APIRouter, WebSocket
from app.ws.websocket_manager import connect, disconnect

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        await disconnect(websocket, user_id)