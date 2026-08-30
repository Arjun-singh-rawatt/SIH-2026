"""SafetyReport database model with dual AI prediction and Human review fields."""

from datetime import datetime
import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import (
    String,
    Text,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin
from app.utils.enums import ReportType, SIFPotential, SIFPrecursor, ReviewStatus, BarrierStatus

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.facility import Facility
    from app.db.models.barrier_assessment import BarrierAssessment
    from app.db.models.action_item import ActionItem
    from app.db.models.vector_reference import ReportVectorReference


class SafetyReport(Base, TimestampMixin):
    __tablename__ = "safety_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    # Ingestion & Context Metadata
    reporter_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.user_id"), index=True, nullable=False)
    facility_id: Mapped[str] = mapped_column(String(50), ForeignKey("facilities.facility_id"), index=True, nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    raw_report_text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(20), default="English", nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    activity: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    potential_consequence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # --------------------------------------------------------------------------
    # AI Predictions (Original AI-Generated Artifacts - Never Overwritten)
    # --------------------------------------------------------------------------
    ai_sif_potential: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    ai_sif_precursor: Mapped[str] = mapped_column(String(20), index=True, default=SIFPrecursor.YES.value, nullable=False)
    ai_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    ai_urgency_score: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    ai_primary_hazard: Mapped[str] = mapped_column(String(200), nullable=False)
    ai_precursor_category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    ai_life_saving_rule: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    ai_failed_barrier: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    ai_barrier_status: Mapped[str] = mapped_column(String(50), default=BarrierStatus.FAILED.value, nullable=False)
    ai_evidence_phrase: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # --------------------------------------------------------------------------
    # Human-in-the-Loop Review & Final Classification
    # --------------------------------------------------------------------------
    review_status: Mapped[str] = mapped_column(String(50), index=True, default=ReviewStatus.PENDING.value, nullable=False)
    reviewer_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("users.user_id"), nullable=True)
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    final_sif_potential: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    final_sif_precursor: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    final_life_saving_rule: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    final_failed_barrier: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    final_barrier_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # --------------------------------------------------------------------------
    # Relationships
    # --------------------------------------------------------------------------
    reporter: Mapped["User"] = relationship(
        "User",
        back_populates="reported_reports",
        foreign_keys=[reporter_id],
    )
    facility: Mapped["Facility"] = relationship(
        "Facility",
        back_populates="reports",
        foreign_keys=[facility_id],
    )
    barrier_assessments: Mapped[List["BarrierAssessment"]] = relationship(
        "BarrierAssessment",
        back_populates="report",
        cascade="all, delete-orphan",
    )
    actions: Mapped[List["ActionItem"]] = relationship(
        "ActionItem",
        back_populates="report",
        cascade="all, delete-orphan",
    )
    vector_reference: Mapped[Optional["ReportVectorReference"]] = relationship(
        "ReportVectorReference",
        back_populates="report",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # Properties to return operational values (human final if reviewed, else AI prediction)
    @property
    def effective_sif_potential(self) -> str:
        return self.final_sif_potential if self.final_sif_potential else self.ai_sif_potential

    @property
    def effective_sif_precursor(self) -> str:
        return self.final_sif_precursor if self.final_sif_precursor else self.ai_sif_precursor

    @property
    def effective_life_saving_rule(self) -> str:
        return self.final_life_saving_rule if self.final_life_saving_rule else self.ai_life_saving_rule

    @property
    def effective_failed_barrier(self) -> str:
        return self.final_failed_barrier if self.final_failed_barrier else (self.ai_failed_barrier or "Operational Barrier Integrity")

    @property
    def effective_barrier_status(self) -> str:
        return self.final_barrier_status if self.final_barrier_status else self.ai_barrier_status


# Compound indexes for fast multi-field filtering
Index("ix_reports_facility_potential", SafetyReport.facility_id, SafetyReport.ai_sif_potential)
Index("ix_reports_urgency_created", SafetyReport.ai_urgency_score.desc(), SafetyReport.created_at.desc())
