from fastapi import APIRouter

from api.routers.user import router
from modules.user.schemas import UserCreate, UserRead, UserUpdate
from core.auth.backend import auth_backend
from core.auth.router import fastapi_users

router = APIRouter()

router.include_router(fastapi_users.get_auth_router(auth_backend))
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
router.include_router(fastapi_users.get_verify_router(UserRead))
router.include_router(fastapi_users.get_reset_password_router())
router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))