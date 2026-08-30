"""BarrierAssessment database model."""

import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin
from app.utils.enums import BarrierStatus

if TYPE_CHECKING:
    from app.db.models.safety_report import SafetyReport


class BarrierAssessment(Base, TimestampMixin):
    __tablename__ = "barrier_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id: Mapped[str] = mapped_column(String(50), ForeignKey("safety_reports.report_id", ondelete="CASCADE"), index=True, nullable=False)
    failed_barrier: Mapped[str] = mapped_column(String(200), nullable=False)
    barrier_status: Mapped[str] = mapped_column(String(50), default=BarrierStatus.FAILED.value, nullable=False)
    barrier_type: Mapped[str] = mapped_column(String(100), default="Physical / Procedural", nullable=False)
    life_saving_rule: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    report: Mapped["SafetyReport"] = relationship(
        "SafetyReport",
        back_populates="barrier_assessments",
    )
