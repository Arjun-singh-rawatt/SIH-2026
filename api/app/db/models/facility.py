"""Facility database model."""

import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.safety_report import SafetyReport
    from app.db.models.action_item import ActionItem


class Facility(Base, TimestampMixin):
    __tablename__ = "facilities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    facility_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    short_name: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(150), nullable=False)
    location_description: Mapped[str] = mapped_column(String(300), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    active_personnel: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    manager: Mapped[str] = mapped_column(String(100), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    reports: Mapped[List["SafetyReport"]] = relationship(
        "SafetyReport",
        back_populates="facility",
        foreign_keys="SafetyReport.facility_id",
    )
    actions: Mapped[List["ActionItem"]] = relationship(
        "ActionItem",
        back_populates="facility",
        foreign_keys="ActionItem.facility_id",
    )
