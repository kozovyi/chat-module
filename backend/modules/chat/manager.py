
from typing import Dict, TYPE_CHECKING
from uuid import UUID
from fastapi import WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger("app.modules.chat")


class ConnectionManager:
    def __init__(self):
        self.connections: dict[UUID, WebSocket] = {}

    async def connect(self, websocket: WebSocket,user_id: UUID, room_id: UUID):
        await websocket.accept()
        self.connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, client_id: UUID, room_id: UUID):
        pass

    async def broadcast(self, room_id: UUID,  message: str, client_id: UUID|None = None):
        pass

        
manager = ConnectionManager()