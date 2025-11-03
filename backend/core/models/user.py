import typing as tp
import uuid
import bcrypt
import os

from fastapi import Depends
from sqlalchemy import String, select, update
from sqlalchemy.orm import Mapped, mapped_column

from core.config import settings

os.environ["ADMIN_USER_MODEL"] = settings.admin.user_model
os.environ["ADMIN_USER_MODEL_USERNAME_FIELD"] = settings.admin.username_field
os.environ["ADMIN_SECRET_KEY"] = settings.admin.secret_key

from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from fastadmin import SqlAlchemyModelAdmin, register

from core.models.base import Base
from core.database import async_db_helper, get_db


class User(SQLAlchemyBaseUserTableUUID, Base):
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


@register(User, sqlalchemy_sessionmaker=async_db_helper.session_factory)
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