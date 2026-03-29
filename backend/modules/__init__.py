from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from modules.user.router import user_router, auth_jwt_router
from modules.chat.router import router as chat_router

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/v1", dependencies=[Depends(http_bearer)])
router.include_router(user_router, prefix="/user", tags=["User"])
router.include_router(auth_jwt_router, prefix="/auth/jwt", tags=["Auth"])
router.include_router(chat_router, prefix="/chat", tags=["Chat"])
