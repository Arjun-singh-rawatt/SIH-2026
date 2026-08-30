"""Tests for SIFT Lead Expert Adjudication & Ground-Truth Verification."""

from datetime import datetime, timezone
import pytest

from data_pipeline.annotations import (
    AnnotationManager,
    AdjudicationRecord,
)
from data_pipeline.validation import DatasetValidator


def test_expert_adjudication_resolution():
    """Verify lead expert adjudication produces canonical DatasetRecord in ADJUDICATED review_status."""
    base_record = {
        "report_id": "REP-DISC-01",
        "raw_text": "High pressure natural gas line vibrating heavily at 45 bar.",
        "report_type": "Unsafe Condition",
        "context": {"facility_id": "FAC-DUL-01", "activity": "Maintenance"},
    }

    adjudication = AdjudicationRecord(
        report_id="REP-DISC-01",
        adjudicator_id="HSE-LEAD-01",
        disagreement_notes="High pressure vibration without dampener represents high energy precursor.",
        resolved_labels={
            "sif_potential": "CRITICAL",
            "sif_precursor": "YES",
            "primary_precursor": "Energy Isolation",
            "secondary_precursors": [],
            "primary_hazard": "Stored / Pressurized Hydrocarbon Energy",
            "secondary_hazards": [],
            "life_saving_rule": "Energy Isolation",
            "barriers": [],
            "evidence_spans": [{"text": "vibrating heavily at 45 bar", "start_offset": 31, "end_offset": 58}],
            "urgency_score": 95,
        },
    )

    mgr = AnnotationManager()
    resolved = mgr.apply_adjudication(base_record, adjudication)

    assert resolved["report_id"] == "REP-DISC-01"
    assert resolved["annotation"]["review_status"] == "ADJUDICATED"
    assert resolved["annotation"]["adjudicator_id"] == "HSE-LEAD-01"
    assert resolved["labels"]["sif_potential"] == "CRITICAL"

    # Validate against canonical DatasetRecord validator
    validator = DatasetValidator()
    res = validator.validate_record(resolved)
    assert res.is_valid is True, f"Adjudicated record failed schema validation: {[e.message for e in res.errors]}"
