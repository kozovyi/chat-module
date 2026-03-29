

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase

from core.database import db_manager_async
from modules.user.model import AccessToken, RefreshToken, User
from modules.user.manager import UserManager
from modules.user.repository import RefreshTokenRepo

async def get_user_manager(session: AsyncSession=Depends(db_manager_async.session)):
    base_user_manager = SQLAlchemyUserDatabase(session, user_table=User)
    yield UserManager(base_user_manager)

async def get_access_token_manager(session: AsyncSession=Depends(db_manager_async.session)):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)

async def get_refresh_token_manager(session: AsyncSession = Depends(db_manager_async.session)):
    yield RefreshTokenRepo(session)