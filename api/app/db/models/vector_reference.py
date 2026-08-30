"""ReportVectorReference database model to link Postgres to Pinecone vector index."""

from datetime import datetime, timezone
import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, utc_now

if TYPE_CHECKING:
    from app.db.models.safety_report import SafetyReport


class ReportVectorReference(Base, TimestampMixin):
    __tablename__ = "report_vector_references"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id: Mapped[str] = mapped_column(String(50), ForeignKey("safety_reports.report_id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    vector_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(100), default="text-embedding-3-small", nullable=False)
    dimension: Mapped[int] = mapped_column(Integer, default=1536, nullable=False)
    indexed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    metadata_version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)

    # Relationships
    report: Mapped["SafetyReport"] = relationship(
        "SafetyReport",
        back_populates="vector_reference",
    )
