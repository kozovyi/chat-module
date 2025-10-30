from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_db_helper
from core.models.base import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass

    @classmethod
    # фукнція повертає обєкт для роботи з певною таблицею в БД (user)
    async def get_db(cls, session: AsyncSession = Depends(async_db_helper.session_getter)):
        yield SQLAlchemyUserDatabase(session, cls)
