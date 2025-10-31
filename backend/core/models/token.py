
from fastapi import Depends
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
    SQLAlchemyBaseAccessTokenTableUUID,
)
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.base import Base
from core.database import get_db


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):  
    pass

    @classmethod
    # фукнція повертає обєкт для роботи з певною таблицею в БД (user)
    async def get_db(
        cls, session: AsyncSession = Depends(get_db),
    ):  
        yield SQLAlchemyAccessTokenDatabase(session, cls)