"""Tests for SIFT Annotation Batch Management & Lifecycle Transitions."""

import os
import tempfile
import pytest

from data_pipeline.batches import (
    BatchManager,
    BatchStatus,
    AnnotationBatchMetadata,
)


def test_batch_creation_and_persistence(tmp_path):
    """Verify creating an annotation batch persists metadata and tracks IDs."""
    batch_dir = tmp_path / "batches"
    mgr = BatchManager(batch_dir=str(batch_dir))

    report_ids = ["REP-001", "REP-002", "REP-003"]
    meta = mgr.create_batch(
        batch_id="BATCH-2026-001",
        source_id="SRC-OIL-01",
        report_ids=report_ids,
        annotator_ids=["HSE-ANN-01", "HSE-ANN-02"],
        notes="Q1 Near Miss Audit Batch",
    )

    assert meta.batch_id == "BATCH-2026-001"
    assert meta.record_count == 3
    assert meta.status == BatchStatus.CREATED

    # Reload
    reloaded = mgr.get_batch("BATCH-2026-001")
    assert reloaded is not None
    assert reloaded.record_count == 3
    assert len(reloaded.annotator_ids) == 2


def test_batch_status_lifecycle_updates(tmp_path):
    """Verify batch state transitions from CREATED to COMPLETED / ADJUDICATED."""
    batch_dir = tmp_path / "batches"
    mgr = BatchManager(batch_dir=str(batch_dir))

    mgr.create_batch(
        batch_id="BATCH-2026-002",
        source_id="SRC-OIL-01",
        report_ids=["REP-101", "REP-102"],
    )

    # Transition to EXPORTED
    m1 = mgr.update_status("BATCH-2026-002", BatchStatus.EXPORTED)
    assert m1.status == BatchStatus.EXPORTED

    # Transition to UNDER_REVIEW with discrepancy count
    m2 = mgr.update_status(
        "BATCH-2026-002",
        BatchStatus.UNDER_REVIEW,
        completed_submissions_count=2,
        discrepancy_count=1,
    )
    assert m2.status == BatchStatus.UNDER_REVIEW
    assert m2.discrepancy_count == 1

    batches = mgr.list_batches()
    assert len(batches) == 1
    assert batches[0].batch_id == "BATCH-2026-002"
