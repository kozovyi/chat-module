from fastapi import Depends

from fastapi_users.authentication import JWTStrategy
from core.models.user import User
from core.models.token import AccessToken
from core.config import settings



def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.access_token.verification_token_secret, lifetime_seconds=3600)