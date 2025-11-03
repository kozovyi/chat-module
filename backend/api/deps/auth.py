from core.database import get_db
from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

async def get_user_db(session=Depends(get_db)):
    from core.models.user import User
    yield SQLAlchemyUserDatabase(session, User)

async def get_user_manager(user_db=Depends(get_user_db)):
    from core.auth.manager import UserManager
    yield UserManager(user_db)
