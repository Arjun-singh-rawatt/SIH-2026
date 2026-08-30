"""ActionItem database model for CAPA tracking."""

from datetime import datetime
import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin
from app.utils.enums import ActionStatus, ActionPriority

if TYPE_CHECKING:
    from app.db.models.safety_report import SafetyReport
    from app.db.models.user import User
    from app.db.models.facility import Facility


class ActionItem(Base, TimestampMixin):
    __tablename__ = "action_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    report_id: Mapped[str] = mapped_column(String(50), ForeignKey("safety_reports.report_id", ondelete="CASCADE"), index=True, nullable=False)
    assigned_to: Mapped[str] = mapped_column(String(50), ForeignKey("users.user_id"), index=True, nullable=False)
    facility_id: Mapped[str] = mapped_column(String(50), ForeignKey("facilities.facility_id"), index=True, nullable=False)
    
    action_type: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default=ActionPriority.HIGH.value, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=ActionStatus.OPEN.value, index=True, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    report: Mapped["SafetyReport"] = relationship(
        "SafetyReport",
        back_populates="actions",
    )
    assignee: Mapped["User"] = relationship(
        "User",
        back_populates="assigned_actions",
        foreign_keys=[assigned_to],
    )
    facility: Mapped["Facility"] = relationship(
        "Facility",
        back_populates="actions",
        foreign_keys=[facility_id],
    )


Index("ix_actions_status_due", ActionItem.status, ActionItem.due_date)
