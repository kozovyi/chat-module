
import asyncio
from typing import Dict, TYPE_CHECKING, Optional
from uuid import UUID
from fastapi import WebSocket, WebSocketDisconnect
import logging
import redis.asyncio as aioredis

from core.config import settings

logger = logging.getLogger("app.modules.chat")


class RedisManager:
    def __init__(self, host=settings.redis.HOST, port=settings.redis.PORT, passw=settings.redis.PASS):
        self.redis_url = f"redis://{host}:{port}"
        self.client: Optional[aioredis.Redis] = None
        self.password: str = passw

    async def connect(self):
        if not self.client:
            self.client = aioredis.from_url(self.redis_url, password=self.password, decode_responses=True)

    async def disconnect(self):
        if self.client:
            await self.client.close()

    async def get_client(self):
        if not self.client:
            await self.connect()
        yield self.client

    async def publish(self, room_id: str, message: str):
        if not self.client:
            await self.connect()
        await self.client.publish(room_id, message) # type: ignore

    async def subscribe(self, room_id: str):
        if not self.client:
            await self.connect()
        pubsub = self.client.pubsub() # type: ignore
        await pubsub.subscribe(room_id)
        return pubsub

redis_manager = RedisManager()

class WebSocketManager:
    def __init__(self):
        self.rooms: dict[str, dict[str, WebSocket]] = {} 
        self.redis_session = redis_manager
        self.room_tasks: dict[str, asyncio.Task] = {} 
        self.pubsubs: dict[str, aioredis.client.PubSub] = {} # type: ignore

    async def add_user_to_room(self, room_id: str, user_id: str,  websocket: WebSocket) -> None:
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
            await self.redis_session.connect()
            pubsub_subscriber = await self.redis_session.subscribe(room_id)
            self.pubsubs[room_id] = pubsub_subscriber
            
            task = asyncio.create_task(self._pubsub_data_reader(pubsub_subscriber, room_id))
            self.room_tasks[room_id] = task
            
        self.rooms[room_id][user_id] = websocket
        logger.info(f"User {user_id} joined room {room_id}")

    async def remove_user_from_room(self, room_id: str, user_id: str, websocket: WebSocket) -> None:
        if user_id in self.rooms.get(room_id, {}):
            del self.rooms[room_id][user_id]

            if len(self.rooms[room_id]) == 0:
                del self.rooms[room_id]
                
                if room_id in self.pubsubs:
                    await self.pubsubs[room_id].unsubscribe(room_id)
                    del self.pubsubs[room_id]
                
                if room_id in self.room_tasks:
                    self.room_tasks[room_id].cancel()
                    del self.room_tasks[room_id]

    async def _pubsub_data_reader(self, pubsub_subscriber, room_id: str):
            try:
                while True:
                    message = await pubsub_subscriber.get_message(ignore_subscribe_messages=True)
                    if message is not None:
                        data = message['data'] 
                        active_room = self.rooms.get(room_id, {})
                        for socket in list(active_room.values()):
                            try:
                                await socket.send_text(data)
                            except Exception:
                                continue
                    await asyncio.sleep(0.01)
            except asyncio.CancelledError:
                pass

manager = WebSocketManager()