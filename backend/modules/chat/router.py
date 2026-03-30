from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from uuid import UUID, uuid4
from redis.asyncio import Redis 

from modules.user.model import User
from modules.chat.manager import manager, redis_manager
from modules.user.fastapi_users import current_active_user
import logging

logger = logging.getLogger("app.routers.chat")

router = APIRouter()

@router.post("/ws-ticket")
async def generate_ws_ticket(
    user: User = Depends(current_active_user),
    redis: Redis = Depends(redis_manager.get_client)
):
    ticket = str(uuid4())
    await redis.set(f"ws_ticket:{ticket}", str(user.id), ex=60)
    return {"ticket": ticket}


@router.websocket("/chat/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    room_id: UUID, 
    ticket: str,
    redis: Redis = Depends(redis_manager.get_client)
):  
    
    user_id = await redis.get(f"ws_ticket:{ticket}")
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await redis.delete(f"ws_ticket:{ticket}")
    room_str = str(room_id)
    await manager.add_user_to_room(room_str, user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.remove_user_from_room(room_str, user_id, websocket)