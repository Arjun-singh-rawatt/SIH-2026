"""SIFT Annotation Workbench Database Models.

Defines relational entities for double-blind human annotation, dual assignments,
independent submissions, field-level disagreements, and expert adjudication.
"""

from datetime import datetime
import uuid
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import (
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.safety_report import SafetyReport


class AnnotationBatch(Base, TimestampMixin):
    """Discrete partition of safety reports assigned for dual human annotation."""
    __tablename__ = "annotation_batches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    source_id: Mapped[str] = mapped_column(String(50), nullable=False, default="SRC-SIM-01")
    status: Mapped[str] = mapped_column(String(50), default="CREATED", nullable=False, index=True)
    annotation_protocol_version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
    taxonomy_version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
    record_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.user_id"), nullable=False)

    # Relationships
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    tasks: Mapped[List["AnnotationTask"]] = relationship(
        "AnnotationTask",
        back_populates="batch",
        cascade="all, delete-orphan",
        order_by="AnnotationTask.order_index",
    )


class AnnotationTask(Base, TimestampMixin):
    """A single safety observation narrative scheduled for dual human annotation."""
    __tablename__ = "annotation_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id: Mapped[str] = mapped_column(String(36), ForeignKey("annotation_batches.id", ondelete="CASCADE"), nullable=False, index=True)
    report_id: Mapped[str] = mapped_column(String(50), ForeignKey("safety_reports.report_id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    batch: Mapped["AnnotationBatch"] = relationship("AnnotationBatch", back_populates="tasks")
    report: Mapped["SafetyReport"] = relationship("SafetyReport")
    assignments: Mapped[List["AnnotationAssignment"]] = relationship(
        "AnnotationAssignment",
        back_populates="task",
        cascade="all, delete-orphan",
    )
    disagreements: Mapped[List["DisagreementRecord"]] = relationship(
        "DisagreementRecord",
        back_populates="task",
        cascade="all, delete-orphan",
    )
    adjudication: Mapped[Optional["AdjudicationRecord"]] = relationship(
        "AdjudicationRecord",
        back_populates="task",
        uselist=False,
        cascade="all, delete-orphan",
    )


class AnnotationAssignment(Base, TimestampMixin):
    """Assignment slot mapping an individual annotator to an annotation task."""
    __tablename__ = "annotation_assignments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("annotation_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    annotator_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    role_slot: Mapped[str] = mapped_column(String(20), nullable=False)  # ANNOTATOR_A, ANNOTATOR_B
    status: Mapped[str] = mapped_column(String(50), default="ASSIGNED", nullable=False)  # ASSIGNED, DRAFT, SUBMITTED

    # Relationships
    task: Mapped["AnnotationTask"] = relationship("AnnotationTask", back_populates="assignments")
    annotator: Mapped["User"] = relationship("User", foreign_keys=[annotator_id])
    submission: Mapped[Optional["AnnotationSubmissionRecord"]] = relationship(
        "AnnotationSubmissionRecord",
        back_populates="assignment",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("task_id", "annotator_id", name="uq_task_annotator"),
        UniqueConstraint("task_id", "role_slot", name="uq_task_role_slot"),
    )


class AnnotationSubmissionRecord(Base, TimestampMixin):
    """Independent annotation record (saved draft or finalized ground-truth candidate)."""
    __tablename__ = "annotation_submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assignment_id: Mapped[str] = mapped_column(String(36), ForeignKey("annotation_assignments.id", ondelete="CASCADE"), unique=True, nullable=False)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("annotation_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    annotator_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    is_draft: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Core Annotated Categoricals
    sif_potential: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sif_precursor: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    primary_hazard: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    secondary_hazards: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    activity: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    primary_precursor: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    precursor_categories: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    life_saving_rule: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    life_saving_rules: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Rich Complex Types (Validated against SIFT JSON schemas)
    barriers: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    evidence_spans: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    urgency_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    potential_consequence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    assignment: Mapped["AnnotationAssignment"] = relationship("AnnotationAssignment", back_populates="submission")
    task: Mapped["AnnotationTask"] = relationship("AnnotationTask")
    annotator: Mapped["User"] = relationship("User", foreign_keys=[annotator_id])


class DisagreementRecord(Base, TimestampMixin):
    """Specific field divergence between paired independent human annotations."""
    __tablename__ = "disagreement_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("annotation_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    annotator_a_id: Mapped[str] = mapped_column(String(50), nullable=False)
    annotator_b_id: Mapped[str] = mapped_column(String(50), nullable=False)
    annotator_a_value: Mapped[Any] = mapped_column(JSON, nullable=True)
    annotator_b_value: Mapped[Any] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING_ADJUDICATION", nullable=False, index=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    task: Mapped["AnnotationTask"] = relationship("AnnotationTask", back_populates="disagreements")


class AdjudicationRecord(Base, TimestampMixin):
    """Formal resolution by Lead HSE Expert resolving annotator divergence."""
    __tablename__ = "adjudication_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("annotation_tasks.id", ondelete="CASCADE"), unique=True, nullable=False)
    adjudicator_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.user_id"), nullable=False)

    resolved_sif_potential: Mapped[str] = mapped_column(String(50), nullable=False)
    resolved_sif_precursor: Mapped[str] = mapped_column(String(20), nullable=False)
    resolved_primary_hazard: Mapped[str] = mapped_column(String(200), nullable=False)
    resolved_secondary_hazards: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    resolved_activity: Mapped[str] = mapped_column(String(150), nullable=False)
    resolved_primary_precursor: Mapped[str] = mapped_column(String(100), nullable=False)
    resolved_precursor_categories: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    resolved_life_saving_rule: Mapped[str] = mapped_column(String(150), nullable=False)
    resolved_life_saving_rules: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    resolved_barriers: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    resolved_evidence_spans: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    adjudication_notes: Mapped[str] = mapped_column(Text, nullable=False)
    adjudicated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    task: Mapped["AnnotationTask"] = relationship("AnnotationTask", back_populates="adjudication")
    adjudicator: Mapped["User"] = relationship("User", foreign_keys=[adjudicator_id])
