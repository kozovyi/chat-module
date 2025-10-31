from fastapi import APIRouter
from api.routers.user import router as user_router
from api.routers.auth import router as auth_router
from api.routers.chat import router as chat_router

router = APIRouter(prefix="/v1")
router.include_router(user_router, prefix="/user", tags=["User"])
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(chat_router, prefix="/chat", tags=["Chat"])
