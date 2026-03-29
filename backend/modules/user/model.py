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
from sqlalchemy import String, select, update, LargeBinary

from fastadmin import SqlAlchemyModelAdmin, register, WidgetType, action

from core.models.base import Base, created_at, pk
from core.database import db_manager_async

import typing as tp
import uuid
import bcrypt
import os

from fastapi import Depends
from sqlalchemy import String, select, update

from core.config import settings

os.environ["ADMIN_USER_MODEL"] = settings.admin.user_model
os.environ["ADMIN_USER_MODEL_USERNAME_FIELD"] = settings.admin.username_field
os.environ["ADMIN_SECRET_KEY"] = settings.admin.secret_key

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from fastadmin import SqlAlchemyModelAdmin, register

from core.models.base import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")

class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):  
    pass

class RefreshToken(Base):

    id: Mapped[pk]
    created_at: Mapped[created_at]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(nullable=False)
    revoked: Mapped[bool] = mapped_column(default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship(
        back_populates="refresh_tokens",
    )
    def __str__(self):
        return f"Token {str(self.id)[:8]}"



@register(User, sqlalchemy_sessionmaker=db_manager_async.session)
class UserAdmin(SqlAlchemyModelAdmin):
    exclude = ("hashed_password",)
    list_display = ("id", "username", "is_superuser", "is_active")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser", "is_active")
    search_fields = ("username",)

    async def authenticate(self, username: str, password: str) -> uuid.UUID | int | None:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            query = select(self.model_cls).filter_by(username=username, is_superuser=True)
            result = await session.scalars(query)
            obj = result.first()
            if not obj:
                return None
            if bcrypt.checkpw(password.encode(), obj.hashed_password.encode()):
                return obj.id
            return None

    async def change_password(self, id: uuid.UUID | int, password: str) -> None:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            query = update(self.model_cls).where(User.id.in_([id])).values(hashed_password=hashed_password) #type: ignore
            await session.execute(query)
            await session.commit()

    async def orm_save_upload_field(self, obj: tp.Any, field: str, base64: str) -> None:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            # convert base64 to bytes, upload to s3/filestorage, get url and save or save base64 as is to db (don't recomment it)
            query = update(self.model_cls).where(User.id.in_([obj.id])).values(**{field: base64}) #type: ignore
            await session.execute(query)
            await session.commit()
            

@register(RefreshToken, sqlalchemy_sessionmaker=db_manager_async.session)
class RefreshTokenAdmin(SqlAlchemyModelAdmin):
    exclude = ("token", "user") 
    list_display = ("id", "user_id", "created_at", "expires_at", "revoked")
    list_display_links = ("id",)
    list_filter = ("revoked", "created_at")
    search_fields = ("id",)
