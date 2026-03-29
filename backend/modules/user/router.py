from sqlalchemy.ext.asyncio import AsyncSession
from typing import Generic, Tuple
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status, Body
from fastapi.security import OAuth2PasswordRequestForm

from fastapi_users import FastAPIUsers
from fastapi_users import models
from fastapi_users.authentication import AuthenticationBackend, Authenticator, Strategy
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorCode, ErrorModel

from modules.user.dependencies import get_refresh_token_manager, get_user_manager
from modules.user.model import User
from modules.user.manager import UserManager
from modules.user.backend import CustomAuthenticationBackend, auth_backend
from modules.user.repository import RefreshTokenRepo
from modules.user.strategy import RefreshJWTStrategy
from core.database import db_manager_async

from modules.user.schemas import UserCreate, UserRead, UserUpdate


def get_auth_router(
    backend: CustomAuthenticationBackend,
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    authenticator: Authenticator,
    requires_verification: bool = False,
) -> APIRouter:
    """Generate a router with login/logout routes for an authentication backend."""
    router = APIRouter()
    get_current_user_token = authenticator.current_user_token(
        active=True, verified=requires_verification
    )

    login_responses: OpenAPIResponseType = {
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.LOGIN_BAD_CREDENTIALS: {
                            "summary": "Bad credentials or the user is inactive.",
                            "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                        },
                        ErrorCode.LOGIN_USER_NOT_VERIFIED: {
                            "summary": "The user is not verified.",
                            "value": {"detail": ErrorCode.LOGIN_USER_NOT_VERIFIED},
                        },
                    }
                }
            },
        },
        **backend.transport.get_openapi_login_responses_success(),
    }

    @router.post("/login", name=f"auth:{backend.name}.login", responses=login_responses)
    async def login(
        request: Request,
        credentials: OAuth2PasswordRequestForm = Depends(),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        refresh_manager: RefreshTokenRepo = Depends(get_refresh_token_manager),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
        session: AsyncSession = Depends(db_manager_async.session)
    ):
        user = await user_manager.authenticate(credentials)

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )
        if requires_verification and not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_USER_NOT_VERIFIED,
            )
        response = await backend.login(strategy, user, session, refresh_manager)
        await user_manager.on_after_login(user, request, response)
        return response

    logout_responses: OpenAPIResponseType = {
        **{
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user."
            }
        },
        **backend.transport.get_openapi_logout_responses_success(),
    }

    @router.post("/logout", name=f"auth:{backend.name}.logout", responses=logout_responses)
    async def logout(
        refresh_token: str = Body(..., embed=True),
        strategy: RefreshJWTStrategy = Depends(backend.get_strategy),
        refresh_manager: RefreshTokenRepo = Depends(get_refresh_token_manager),
        session: AsyncSession = Depends(db_manager_async.session)
    ):
        return await backend.logout(strategy, refresh_token, session, refresh_manager)

    @router.post("/refresh")
    async def refresh_token(
        refresh_token: str = Body(..., embed=True),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        strategy: RefreshJWTStrategy = Depends(backend.get_strategy),
        refresh_manager: RefreshTokenRepo = Depends(get_refresh_token_manager),
        session: AsyncSession = Depends(db_manager_async.session)

    ):
        return await backend.refresh(refresh_token=refresh_token, strategy=strategy, session=session, user_manager=user_manager, refresh_manager=refresh_manager)

    return router

class FastAPIUsersRefresh(FastAPIUsers, Generic[models.UP, models.ID]):
    
    def get_auth_router(
        self, backend: CustomAuthenticationBackend, requires_verification: bool = False
    ) -> APIRouter:
        """
        Return an auth router for a given authentication backend.

        :param backend: The authentication backend instance.
        :param requires_verification: Whether the authentication
        require the user to be verified or not. Defaults to False.
        """
        return get_auth_router(
            backend,
            self.get_user_manager,
            self.authenticator,
            requires_verification,
        )

fastapi_users = FastAPIUsersRefresh[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)


user_router = APIRouter()
auth_jwt_router = APIRouter()

auth_jwt_router.include_router(fastapi_users.get_auth_router(auth_backend))
user_router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
user_router.include_router(fastapi_users.get_verify_router(UserRead))
user_router.include_router(fastapi_users.get_reset_password_router())
user_router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))