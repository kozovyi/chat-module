from fastapi import APIRouter
from api.routers.user import router as user_router
from api.routers.auth import router as auth_router

router = APIRouter(prefix="/v1")
router.include_router(user_router, prefix="/user", tags=["User"])
router.include_router(auth_router, prefix="/auth", tags=["Auth"])

