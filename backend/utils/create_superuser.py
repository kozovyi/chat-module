from pathlib import Path
import asyncio
import sys

from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

print(sys.path.append(str(Path(__file__).absolute().parent)))

from core.database import db_manager_async
from core.config import settings
from modules.user.manager import UserManager
from modules.user.model import User
from modules.user.schemas import UserCreate

async def create_superuser():

    user_create = UserCreate(
        email=settings.super_user.default_email,
        username=settings.super_user.default_username,
        password=settings.super_user.default_password,
        is_active=settings.super_user.default_is_active,
        is_superuser=settings.super_user.default_is_superuser,
        is_verified=settings.super_user.default_is_verified,
    )

    async with db_manager_async.session_factory() as session:
        base_manager = SQLAlchemyUserDatabase(session, User)
        user_manager = UserManager(base_manager)
        await user_manager.create(user_create, safe=False)

if __name__ == "__main__":
    asyncio.run(create_superuser())
