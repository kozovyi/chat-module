from fastapi import Depends

from fastapi_users.authentication.strategy.db import AccessTokenDatabase, DatabaseStrategy

from core.models.user import User
from core.models.token import AccessToken
from core.config import settings


def get_database_strategy(
    access_token_manager  : AccessTokenDatabase[AccessToken] = Depends(AccessToken.get_db),
) -> DatabaseStrategy:
    return DatabaseStrategy(
        access_token_manager,
        lifetime_seconds=settings.access_token.lifetime_seconds
    ) 