from typing import Generic, TypeVar
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from core.models.base import Base
from uuid import UUID

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, session: AsyncSession, model: type[ModelType]):
        self.session = session
        self.model = model

    async def create(self, schema: CreateSchemaType) -> ModelType:
        instance = self.model(**schema.model_dump())
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get(self, doc_id: UUID|int) -> ModelType | None:
        return await self.session.get(self.model, doc_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, doc_id, schema:UpdateSchemaType) -> ModelType | None:
        update_data = schema.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get(doc_id)
        query = (
            update(self.model) # type: ignore
            .where(self.model.id == doc_id) # type: ignore
            .values(**update_data)
            .returning(self.model)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, doc_id: UUID) -> bool:
        query = delete(self.model).where(self.model.id == doc_id) # type: ignore
        result = await self.session.execute(query)
        return getattr(result, 'rowcount', 0) > 0

    async def exists(self, doc_id: UUID) -> bool:
        query = select(self.model).where(self.model.id == doc_id).exists() # type: ignore
        result = await self.session.execute(select(query))
        return result.scalar() # type: ignore
