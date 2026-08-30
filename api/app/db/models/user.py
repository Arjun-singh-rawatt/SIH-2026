"""User database model."""

import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin
from app.utils.enums import UserRole

if TYPE_CHECKING:
    from app.db.models.safety_report import SafetyReport
    from app.db.models.action_item import ActionItem
    from app.db.models.facility import Facility


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), default=UserRole.SAFETY_OFFICER.value, nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=True)
    facility_id: Mapped[str] = mapped_column(String(50), nullable=True)
    contact_number: Mapped[str] = mapped_column(String(50), nullable=True)
    avatar: Mapped[str] = mapped_column(String(500), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    reported_reports: Mapped[List["SafetyReport"]] = relationship(
        "SafetyReport",
        back_populates="reporter",
        foreign_keys="SafetyReport.reporter_id",
    )
    assigned_actions: Mapped[List["ActionItem"]] = relationship(
        "ActionItem",
        back_populates="assignee",
        foreign_keys="ActionItem.assigned_to",
    )
