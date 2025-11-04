from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from api.routers.user import router as user_router
from api.routers.chat import router as chat_router
from api.routers.auth import auth_jwt_router, auth_users_router


http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/v1", dependencies=[Depends(http_bearer)])
router.include_router(user_router, prefix="/user", tags=["User"])
router.include_router(auth_jwt_router, prefix="/auth/jwt", tags=["JWT"])
router.include_router(auth_users_router, prefix="/auth", tags=["Auth"])
router.include_router(chat_router, prefix="/chat", tags=["Chat"])
