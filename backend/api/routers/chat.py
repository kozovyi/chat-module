from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect

from chat.manager import manager


router = APIRouter()

@router.websocket("/{room_id}/{user_id}")
async def websocket_connect(websocket: WebSocket, room_id: int, user_id: int, username: str):
    await manager.connect(websocket, room_id, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{username}: {data}", room_id, user_id)
    except WebSocketDisconnect:
        manager.disconnect(room_id, user_id)
