"""User management service."""

from typing import List
from app.db.repositories.user_repo import UserRepository
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.db.models.user import User
from app.core.errors import UserNotFoundException


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.repo = user_repo

    async def list_users(self) -> List[UserRead]:
        users = await self.repo.get_all_active()
        return [UserRead.model_validate(u) for u in users]

    async def get_user_by_id(self, identifier: str) -> UserRead:
        user = await self.repo.get_by_user_id(identifier)
        if not user:
            raise UserNotFoundException(identifier)
        return UserRead.model_validate(user)

    async def create_user(self, payload: UserCreate) -> UserRead:
        user = User(
            user_id=payload.user_id,
            name=payload.name,
            email=payload.email,
            role=payload.role,
            title=payload.title,
            facility_id=payload.facility_id,
            contact_number=payload.contact_number,
            avatar=payload.avatar,
            active=payload.active,
        )
        created = await self.repo.create(user)
        return UserRead.model_validate(created)
