import bcrypt
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime
from core.models.token import RefreshToken

class RefreshTokenRepo:
    @staticmethod
    async def create(user_id: UUID, expires_at: datetime, raw_token: str, session: AsyncSession) -> RefreshToken:
        token = RefreshToken(
            user_id=user_id,
            token=raw_token, 
            expires_at=expires_at,
        )
        session.add(token)
        try:
            await session.commit()
            await session.refresh(token)
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        return token

    @staticmethod
    async def get(raw_token: str, session: AsyncSession) -> RefreshToken:
        stmt = select(RefreshToken).where(
            RefreshToken.token == raw_token,
            RefreshToken.revoked == False
        )
        token = await session.scalar(stmt)
        
        if token:
            if token.expires_at < datetime.utcnow():
                token.revoked = True
                await session.commit()
                await session.refresh(token)
                raise ValueError("Token expired")
            return token
        raise ValueError("Token not found")

    @staticmethod
    async def revoke(raw_token: str, session: AsyncSession) -> RefreshToken:
        try:
            stmt = select(RefreshToken).where(
                RefreshToken.token == raw_token,
                RefreshToken.revoked == False
            )
            token = await session.scalar(stmt)
            
            if token:
                token.revoked = True
                await session.commit()
                await session.refresh(token)
                return token

            raise ValueError("Token not found or already revoked")

        except SQLAlchemyError as e:
            await session.rollback()
            raise e

    @staticmethod
    async def remove(raw_token: str, session: AsyncSession):
        stmt = select(RefreshToken).where(RefreshToken.token == raw_token)
        token = await session.scalar(stmt)
        
        if token:
            await session.delete(token)
            await session.commit()
            return

        raise ValueError("Token not found")