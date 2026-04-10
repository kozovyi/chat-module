from typing import Generic, TypeVar
from pydantic import BaseModel
from uuid import UUID
from core.models.base import Base
from modules.repository import BaseRepository

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, repository: BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]):
        self.repository = repository

    async def create(self, schema: CreateSchemaType) -> ModelType:
        return await self.repository.create(schema)

    async def get(self, doc_id: UUID) -> ModelType | None:
        return await self.repository.get(doc_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return await self.repository.get_all(skip, limit)

    async def update(self, doc_id: UUID, schema: UpdateSchemaType) -> ModelType | None:
        return await self.repository.update(doc_id, schema)

    async def delete(self, doc_id: UUID) -> bool:
        return await self.repository.delete(doc_id)
    
    async def exists(self, doc_id: UUID) -> bool:
        return await self.repository.exists(doc_id)
