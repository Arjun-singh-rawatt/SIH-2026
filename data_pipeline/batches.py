"""SIFT Annotation Batch Lifecycle Management System.

Partitions normalized frontline safety observations into auditable annotation batches,
tracks dual-annotator assignment, monitors completion progress, and manages batch state transitions.
"""

from datetime import datetime, timezone
from enum import Enum
import json
import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BatchStatus(str, Enum):
    """Lifecycle states of an annotation batch."""
    CREATED = "CREATED"
    EXPORTED = "EXPORTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ADJUDICATED = "ADJUDICATED"
    RELEASED = "RELEASED"


class AnnotationBatchMetadata(BaseModel):
    """Metadata and audit trail for a discrete human annotation batch."""
    batch_id: str = Field(..., description="Unique batch ID, e.g. BATCH-2026-001")
    source_id: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    annotation_protocol_version: str = "1.0"
    taxonomy_version: str = "1.0"
    record_count: int = 0
    report_ids: List[str] = Field(default_factory=list)
    annotator_ids: List[str] = Field(default_factory=list)
    status: BatchStatus = BatchStatus.CREATED
    completed_submissions_count: int = 0
    discrepancy_count: int = 0
    adjudicated_count: int = 0
    notes: Optional[str] = None


class BatchManager:
    """Manages annotation batches and metadata persistence in data/metadata/annotation_batches/."""

    DEFAULT_BATCH_DIR = "data/metadata/annotation_batches"

    def __init__(self, batch_dir: str = DEFAULT_BATCH_DIR):
        self.batch_dir = batch_dir
        os.makedirs(self.batch_dir, exist_ok=True)

    def _get_batch_filepath(self, batch_id: str) -> str:
        return os.path.join(self.batch_dir, f"{batch_id}.json")

    def create_batch(
        self,
        batch_id: str,
        source_id: str,
        report_ids: List[str],
        annotator_ids: Optional[List[str]] = None,
        annotation_protocol_version: str = "1.0",
        taxonomy_version: str = "1.0",
        notes: Optional[str] = None,
    ) -> AnnotationBatchMetadata:
        """Create a new annotation batch and persist its metadata."""
        meta = AnnotationBatchMetadata(
            batch_id=batch_id,
            source_id=source_id,
            annotation_protocol_version=annotation_protocol_version,
            taxonomy_version=taxonomy_version,
            record_count=len(report_ids),
            report_ids=report_ids,
            annotator_ids=annotator_ids or ["HSE-ANN-01", "HSE-ANN-02"],
            status=BatchStatus.CREATED,
            notes=notes,
        )
        self.save_batch(meta)
        return meta

    def save_batch(self, meta: AnnotationBatchMetadata):
        """Persist batch metadata JSON to disk."""
        meta.updated_at = datetime.now(timezone.utc).isoformat()
        filepath = self._get_batch_filepath(meta.batch_id)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(meta.model_dump_json(indent=2))

    def get_batch(self, batch_id: str) -> Optional[AnnotationBatchMetadata]:
        """Load batch metadata from disk."""
        filepath = self._get_batch_filepath(batch_id)
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return AnnotationBatchMetadata(**data)

    def update_status(self, batch_id: str, status: BatchStatus, **kwargs) -> AnnotationBatchMetadata:
        """Update batch state and optional metrics."""
        meta = self.get_batch(batch_id)
        if not meta:
            raise FileNotFoundError(f"Batch metadata not found: {batch_id}")
        meta.status = status
        for k, v in kwargs.items():
            if hasattr(meta, k):
                setattr(meta, k, v)
        self.save_batch(meta)
        return meta

    def list_batches(self) -> List[AnnotationBatchMetadata]:
        """List all registered annotation batches."""
        batches = []
        if os.path.exists(self.batch_dir):
            for fname in sorted(os.listdir(self.batch_dir)):
                if fname.endswith(".json"):
                    b_id = fname[:-5]
                    b = self.get_batch(b_id)
                    if b:
                        batches.append(b)
        return batches
