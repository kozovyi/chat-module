import uuid
import typing as tp


import bcrypt
from fastapi import Depends
from sqlalchemy import update
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
    SQLAlchemyBaseAccessTokenTableUUID,
)
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import String, select, update

from fastadmin import SqlAlchemyModelAdmin, register, WidgetType, action

from core.models.base import Base, created_at, pk
from core.models.user import User
from core.database import get_db
from core.database import async_db_helper


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):  
    pass

    @classmethod
    # фукнція повертає обєкт для роботи з певною таблицею в БД (user)
    async def get_db(
        cls, session: AsyncSession = Depends(get_db),
    ):  
        yield SQLAlchemyAccessTokenDatabase(session, cls)


class RefreshToken(Base):

    id: Mapped[pk]
    created_at: Mapped[created_at]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    hashed_token: Mapped[bytes] = mapped_column(nullable=False)
    revoked: Mapped[bool] = mapped_column(default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship(
        back_populates="refresh_tokens",
    )
    def __str__(self):
        return f"Token {str(self.id)[:8]}"


@register(RefreshToken, sqlalchemy_sessionmaker=async_db_helper.session_factory)
class RefreshTokenAdmin(SqlAlchemyModelAdmin):
    exclude = ("hashed_token", "user") 
    list_display = ("id", "user_id", "created_at", "expires_at", "revoked")
    list_display_links = ("id",)
    list_filter = ("revoked", "created_at")
    search_fields = ("id",)
