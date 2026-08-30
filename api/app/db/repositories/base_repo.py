"""Base generic repository for CRUD database operations."""

from typing import Generic, Type, TypeVar, Optional, List, Any, Sequence
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(self, model: Type[ModelT], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: Any) -> Optional[ModelT]:
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelT]:
        result = await self.db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def count(self) -> int:
        result = await self.db.execute(select(func.count(self.model.id)))
        return result.scalar_one()

    async def create(self, obj_in: ModelT) -> ModelT:
        self.db.add(obj_in)
        await self.db.commit()
        await self.db.refresh(obj_in)
        return obj_in

    async def update(self, db_obj: ModelT) -> ModelT:
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: ModelT) -> None:
        await self.db.delete(db_obj)
        await self.db.commit()
