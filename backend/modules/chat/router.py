from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from uuid import UUID
import json
from datetime import datetime

from modules.user.model import User
from modules.chat.manager import manager
from modules.user.router import fastapi_users
import logging

current_active_user = fastapi_users.current_user(active=True)

logger = logging.getLogger("app.routers.chat")

router = APIRouter()


@router.websocket("/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: UUID, client: User = Depends(current_active_user)):
    await manager.connect(websocket, client.id, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            ...


            
    except WebSocketDisconnect:
        manager.disconnect(websocket, client.id, room_id)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, client.id, room_id)
