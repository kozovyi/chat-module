from fastapi import APIRouter

from modules.user.schemas import UserCreate, UserRead, UserUpdate
from core.auth.backend import auth_backend
from core.auth.router import fastapi_users

auth_users_router = APIRouter()
auth_jwt_router = APIRouter()

auth_jwt_router.include_router(fastapi_users.get_auth_router(auth_backend))
auth_users_router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
auth_users_router.include_router(fastapi_users.get_verify_router(UserRead))
auth_users_router.include_router(fastapi_users.get_reset_password_router())
auth_users_router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))