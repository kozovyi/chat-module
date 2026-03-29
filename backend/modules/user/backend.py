from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users.authentication import AuthenticationBackend
from typing import Generic

from fastapi import Response, status

from fastapi_users import BaseUserManager, models
from fastapi_users.authentication.strategy import (
    Strategy,
    StrategyDestroyNotSupportedError,
)
from fastapi_users.authentication.transport import (
    Transport,
    TransportLogoutNotSupportedError,
)
from fastapi_users.types import DependencyCallable


from modules.user.transport import BearerTransport, bearer_transport
from modules.user.strategy import RefreshJWTStrategy, get_jwt_strategy
from core.config import RefreshToken
from modules.user.repository import RefreshTokenRepo

class CustomAuthenticationBackend(AuthenticationBackend, Generic[models.UP, models.ID]):
    """
    Combination of an authentication transport and strategy.

    Together, they provide a full authentication method logic.

    :param name: Name of the backend.
    :param transport: Authentication transport instance.
    :param get_strategy: Dependency callable returning
    an authentication strategy instance.
    """

    name: str
    transport: BearerTransport

    def __init__(
        self,
        name: str,
        transport: BearerTransport,
        get_strategy: DependencyCallable[Strategy[models.UP, models.ID]],
    ):
        self.name = name
        self.transport = transport
        self.get_strategy = get_strategy

    async def login(
        self, strategy: Strategy[models.UP, models.ID], user: models.UP, session: AsyncSession, refresh_manager: RefreshTokenRepo
    ) -> Response:
        tokens = await strategy.write_token(user, refresh_manager=refresh_manager)#type: ignore
        return await self.transport.get_login_response(tokens["access_token"], tokens["refresh_token"]) #type: ignore

    async def logout(
        self, strategy:  RefreshJWTStrategy, refresh_token: str, session: AsyncSession, refresh_manager: RefreshTokenRepo
    ) -> Response:
        try:
            await strategy.destroy_token(refresh_token, refresh_manager=refresh_manager)
        except StrategyDestroyNotSupportedError:
            pass

        try:
            response = await self.transport.get_logout_response()
        except TransportLogoutNotSupportedError:
            response = Response(status_code=status.HTTP_204_NO_CONTENT)

        return response
    
    async def refresh(
        self, refresh_token, strategy: RefreshJWTStrategy[models.UP, models.ID], session: AsyncSession, user_manager: BaseUserManager[models.UP, models.ID], refresh_manager: RefreshTokenRepo
    )-> Response:
        try:
            tokens = await strategy.refresh_tokens(refresh_token=refresh_token, user_manager=user_manager, refresh_manager=refresh_manager)
            return await self.transport.get_refresh_response(access_token=tokens["access_token"], refresh_token=tokens["refresh_token"])
        except Exception as e:
            raise e

auth_backend = CustomAuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
