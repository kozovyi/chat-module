from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from uuid import UUID

from core.models.user import User
from  modules.chat.manager import manager
from core.auth.router import fastapi_users

current_active_user = fastapi_users.current_user(active=True)
 
router = APIRouter()

@router.websocket("/{room_id}")
async def websocket_connect(websocket: WebSocket, room_id: UUID, user: User = Depends(current_active_user)):
    await manager.connect(websocket, room_id, user.id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{user.username}: {data}", room_id, user.id)
    except WebSocketDisconnect:
        manager.disconnect(room_id, user.id)
