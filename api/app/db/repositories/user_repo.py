"""User repository."""

from typing import Optional, Sequence
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.db.repositories.base_repo import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_user_id(self, user_id: str) -> Optional[User]:
        stmt = select(User).where(
            or_(
                User.user_id == user_id,
                User.id == user_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email.lower().strip())
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_all_active(self) -> Sequence[User]:
        stmt = select(User).where(User.active.is_(True)).order_by(User.user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
