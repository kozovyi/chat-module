import uuid
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from uuid import UUID, uuid4
from redis.asyncio import Redis 

from modules.chat.schema import MessageCreate
from modules import user
from modules.user.model import User
from modules.chat.manager import manager, redis_manager
from modules.user.fastapi_users import current_active_user
from modules.dependency import http_bearer
import logging

logger = logging.getLogger("app.routers.chat")

router = APIRouter()

@router.post("/ws-ticket", dependencies=[Depends(http_bearer)])
async def generate_ws_ticket(
    user: User = Depends(current_active_user),
    redis: Redis = Depends(redis_manager.get_client)
):
    ticket = str(uuid4())
    await redis.set(f"ws_ticket:{ticket}", str(user.id), ex=60)
    return {"ticket": ticket}


@router.websocket("/{room_id}")
async def websocket_chat(
    websocket: WebSocket,
    room_id: uuid.UUID,
    ticket: str = Query(...),
    redis: Redis = Depends(redis_manager.get_client)
):  
    user_id = await redis.get(f"ws_ticket:{ticket}")

    await redis.delete(f"ws_ticket:{ticket}")
    if not user_id:
        await websocket.close(code=1008)
        return
    
    room = str(room_id)
    
    await manager.add_user_to_room(room, user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await redis.publish(room, data)
    except WebSocketDisconnect:
        await manager.remove_user_from_room(room, user_id, websocket)    