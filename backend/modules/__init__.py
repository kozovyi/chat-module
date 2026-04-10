from fastapi import APIRouter, Depends
from modules.user.router import user_router, auth_jwt_router
from modules.chat.router import router as chat_router
from modules.dependency import http_bearer

router = APIRouter(prefix="/v1")
router.include_router(user_router, prefix="/user", tags=["User"], dependencies=[Depends(http_bearer)])
router.include_router(auth_jwt_router, prefix="/auth/jwt", tags=["Auth"], dependencies=[Depends(http_bearer)])
router.include_router(chat_router, prefix="/chat", tags=["Chat"])
