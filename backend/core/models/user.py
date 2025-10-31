from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.base import Base
from core.database import get_db


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass

    @classmethod
    # фукнція повертає обєкт для роботи з певною таблицею в БД (user)
    async def get_db(cls, session: AsyncSession = Depends(get_db)):
        yield SQLAlchemyUserDatabase(session, cls)
