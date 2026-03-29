import bcrypt
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timezone
from modules.user.model import RefreshToken

class RefreshTokenRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_valid_token(self, raw_token: str) -> RefreshToken | None:
            stmt = select(RefreshToken).where(
                RefreshToken.token == raw_token,
                RefreshToken.revoked == False
            )
            return await self.session.scalar(stmt)

    async def create(self, user_id: UUID, expires_at: datetime, raw_token: str) -> RefreshToken:
        token = RefreshToken(
            user_id=user_id,
            token=raw_token, 
            expires_at=expires_at,
        )
        self.session.add(token)
        try:
            await self.session.commit()
            await self.session.refresh(token)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e
        return token

    async def get(self, raw_token: str) -> RefreshToken:
        stmt = select(RefreshToken).where(
            RefreshToken.token == raw_token,
            RefreshToken.revoked == False
        )
        token = await self.session.scalar(stmt)
        
        if token:
            if token.expires_at < datetime.utcnow():
                token.revoked = True
                await self.session.commit()
                await self.session.refresh(token)
                raise ValueError("Token expired")
            return token
        raise ValueError("Token not found")

    async def revoke(self, raw_token: str) -> bool:
            token = await self.get_valid_token(raw_token)
            if token:
                token.revoked = True
                await self.session.commit()
                return True
            return False

    async def is_expired(self, token: RefreshToken) -> bool:
            return token.expires_at < datetime.now(timezone.utc)

    async def remove(self, raw_token: str):
        stmt = select(RefreshToken).where(RefreshToken.token == raw_token)
        token = await self.session.scalar(stmt)
        
        if token:
            await self.session.delete(token)
            await self.session.commit()
            return

        raise ValueError("Token not found")