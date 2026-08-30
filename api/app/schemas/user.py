"""User Pydantic schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.utils.enums import UserRole


class UserBase(BaseModel):
    user_id: str = Field(..., description="Unique User ID (e.g. USR-001)")
    name: str = Field(..., description="Full Name")
    email: EmailStr = Field(..., description="Corporate Email")
    role: str = Field(default=UserRole.SAFETY_OFFICER.value)
    title: Optional[str] = None
    facility_id: Optional[str] = None
    contact_number: Optional[str] = None
    avatar: Optional[str] = None
    active: bool = True


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    title: Optional[str] = None
    facility_id: Optional[str] = None
    contact_number: Optional[str] = None
    avatar: Optional[str] = None
    active: Optional[bool] = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
