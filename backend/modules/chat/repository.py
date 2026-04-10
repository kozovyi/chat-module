from modules.repository import BaseRepository
from modules.chat.model import Room, RoomParticipant, Message
from modules.chat.schemas import (
    RoomCreate, RoomUpdate,
    RoomParticipantCreate, RoomParticipantUpdate,
    MessageCreate, MessageUpdate
)

class RoomRepository(BaseRepository[Room, RoomCreate, RoomUpdate]):
    pass

class RoomParticipantRepository(BaseRepository[RoomParticipant, RoomParticipantCreate, RoomParticipantUpdate]):
    pass

class MessageRepository(BaseRepository[Message, MessageCreate, MessageUpdate]):
    pass
