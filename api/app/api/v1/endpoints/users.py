"""User management endpoints."""

from typing import List
from fastapi import APIRouter, Depends, status
from app.api.deps import get_user_service
from app.services.user_service import UserService
from app.schemas.user import UserRead, UserCreate

router = APIRouter(prefix="/users", tags=["Users & Safety Officers"])


@router.get(
    "",
    response_model=List[UserRead],
    summary="List Active Users",
)
async def list_users(
    service: UserService = Depends(get_user_service),
) -> List[UserRead]:
    """Retrieve list of registered safety officers, investigators, and managers."""
    return await service.list_users()


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get User Profile",
)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    """Retrieve user profile information."""
    return await service.get_user_by_id(user_id)


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create User Profile",
)
async def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    """Register a new HSE user or investigator profile."""
    return await service.create_user(payload)
