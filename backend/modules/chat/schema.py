from pydantic import BaseModel
from typing import Optional, Union
from uuid import UUID

class RoomCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_private: bool = False

class RoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_private: Optional[bool] = None

class RoomParticipantCreate(BaseModel):
    room_id: Union[UUID, int]
    user_id: Union[UUID, int]
    is_admin: bool = False

class RoomParticipantUpdate(BaseModel):
    is_admin: Optional[bool] = None

class MessageCreate(BaseModel):
    room_id: int
    content: str
    user_id: Optional[int] = None

class MessageUpdate(BaseModel):
    content: Optional[str] = None
