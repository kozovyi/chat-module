from sqlalchemy.ext.asyncio import AsyncSession
from typing import Generic, List, Optional, Dict
from datetime import timedelta, datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi_users.authentication.strategy.base import Strategy
from fastapi_users.authentication import JWTStrategy
from fastapi_users import models, exceptions
from fastapi_users.jwt import generate_jwt, SecretType, decode_jwt
from fastapi_users.manager import BaseUserManager
import jwt

from modules.user.dependencies import get_refresh_token_manager
from modules.user.repository import RefreshTokenRepo
from core.config import RefreshToken, settings


class RefreshJWTStrategy(JWTStrategy, Strategy[models.UP, models.ID], Generic[models.UP, models.ID]):
    def __init__(
        self,
        secret: SecretType,
        access_lifetime_seconds: int,
        refresh_lifetime_seconds: int,
        token_audience: List[str] = ["fastapi-users:auth"],
        algorithm: str = "HS256",
        public_key: Optional[SecretType] = None,
    ):
        self.secret = secret
        self.access_lifetime_seconds = access_lifetime_seconds
        self.refresh_lifetime_seconds = refresh_lifetime_seconds
        self.token_audience = token_audience
        self.algorithm = algorithm
        self.public_key = public_key
    
    async def write_token(self, user: models.UP, refresh_manager: RefreshTokenRepo) -> Dict[str, str]:
        access_data = {"sub": str(user.id), "aud": self.token_audience, "type": "access"}
        refresh_data = {"sub": str(user.id), "aud": self.token_audience, "type": "refresh"}

        access_token = generate_jwt(
            access_data, self.encode_key, self.access_lifetime_seconds, algorithm=self.algorithm
        )
        refresh_token = generate_jwt(
            refresh_data, self.encode_key, self.refresh_lifetime_seconds, algorithm=self.algorithm
        )

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.refresh_lifetime_seconds)
        await refresh_manager.create(user_id=user.id, raw_token=refresh_token, expires_at=expires_at)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def refresh_tokens(
        self, refresh_token: str, user_manager: BaseUserManager[models.UP, models.ID], refresh_manager: RefreshTokenRepo
    ) -> Dict[str, str]:
        user = await self.read_token(refresh_token, user_manager)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
        try:

            payload = decode_jwt(
                refresh_token, self.decode_key, self.token_audience, algorithms=[self.algorithm]
            )
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type (must be refresh)",
                )
            try:
                token = await refresh_manager.get(raw_token=refresh_token)
            except:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token not found",
                )
            if token.revoked:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired refresh token",
                )

            await refresh_manager.revoke(raw_token=refresh_token)
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        except Exception as e:
            raise e

        return await self.write_token(user, refresh_manager=refresh_manager)

    async def destroy_token(self, refresh_token: str, refresh_manager: RefreshTokenRepo):
        return await refresh_manager.revoke(raw_token=refresh_token)


def get_jwt_strategy() -> JWTStrategy:
    return RefreshJWTStrategy(secret=settings.access_token.verification_token_secret, access_lifetime_seconds=settings.access_token.lifetime_seconds, refresh_lifetime_seconds=settings.refresh_token.lifetime_seconds)