from modules.service import BaseService
from modules.chat.model import Room, RoomParticipant, Message
from modules.chat.schema import (
    RoomCreate, RoomUpdate,
    RoomParticipantCreate, RoomParticipantUpdate,
    MessageCreate, MessageUpdate
)
from modules.chat.repository import RoomRepository, RoomParticipantRepository, MessageRepository

class RoomService(BaseService[Room, RoomCreate, RoomUpdate]):
    def __init__(self, repository: RoomRepository):
        super().__init__(repository)

class RoomParticipantService(BaseService[RoomParticipant, RoomParticipantCreate, RoomParticipantUpdate]):
    def __init__(self, repository: RoomParticipantRepository):
        super().__init__(repository)

class MessageService(BaseService[Message, MessageCreate, MessageUpdate]):
    def __init__(self, repository: MessageRepository):
        super().__init__(repository)
