from datetime import datetime, timezone
from uuid import UUID
from typing import Optional, List
from sqlalchemy import ForeignKey, Text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base
from modules.user.model import User

class Room(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    is_private: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

    messages: Mapped[List["Message"]] = relationship(
        back_populates="room",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __str__(self) -> str:
        return f"<Room id={self.id} name={self.name}>"
    
class RoomParticipant(Base):

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[UUID] = mapped_column(ForeignKey("room.id", ondelete="CASCADE"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    joined_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    is_admin: Mapped[bool] = mapped_column(default=False)

    room: Mapped["Room"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship()

class Message(Base):

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("room.id", ondelete="CASCADE"))
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    is_edited: Mapped[bool] = mapped_column(default=False)
    is_deleted: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship(back_populates="messages")
    room: Mapped["Room"] = relationship(back_populates="messages")

    def __str__(self) -> str:
        return f"<Message id={self.id} room={self.room_id} user={self.user_id}>"

