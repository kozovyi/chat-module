# import asyncio
# import contextlib
# from pydantic import EmailStr
# from typing import Optional
# from pathlib import Path
# import sys

# sys.path.append(str(Path(__file__).absolute().parent))

# from api.api_v1.dependencies.user import get_user_db, get_user_manager
# from schemas.user import UserCreate
# from core.database import async_db_helper
# from core.authentication.user_maneger import UserManager
# from core.models.user import Users
# from core.config import settings

# get_user_db_context = contextlib.asynccontextmanager(get_user_db)
# get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


# default_email = settings.super_user.default_email
# default_password = settings.super_user.default_password
# default_is_active = settings.super_user.default_is_active
# default_is_superuser = settings.super_user.default_is_superuser
# default_is_verified = settings.super_user.default_is_verified


# async def create_user(user_manager: UserManager, user_create: UserCreate) -> Users:
#     user = await user_manager.create(user_create=user_create, safe=False)
#     return user


# async def create_superuser(
#     email: EmailStr = default_email,
#     password: str = default_password,
#     is_active: Optional[bool] = default_is_active,
#     is_superuser: Optional[bool] = default_is_superuser,
#     is_verified: Optional[bool] = default_is_verified,
# ):
#     user_create = UserCreate(
#         email=email,
#         password=password,
#         is_active=is_active,
#         is_superuser=is_superuser,
#         is_verified=is_verified,
#     )

#     async with async_db_helper.session_factory() as session:
#         async with get_user_db_context(session) as user_db:
#             async with get_user_manager_context(user_db) as user_manager:
#                 return await create_user(
#                     user_manager=user_manager, user_create=user_create
#                 )


# if __name__ == "__main__":
#     asyncio.run(create_superuser())
