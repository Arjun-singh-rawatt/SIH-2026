"""Tests for SIFT Dataset Release Gates & Pre-Flight Checklist Auditor."""

import pytest
from data_pipeline.release_gate import ReleaseGateAuditor


def test_release_gate_approves_compliant_records():
    """Verify release gate approves verified, PII-clean, consensus records."""
    valid_record = {
        "schema_version": "1.0",
        "report_id": "REL-001",
        "raw_text": "Pressure gauge damaged during routine pipeline inspection.",
        "report_type": "Unsafe Condition",
        "context": {"facility_id": "FAC-DUL-01", "activity": "Maintenance"},
        "labels": {
            "sif_potential": "LOW",
            "sif_precursor": "NO",
            "primary_precursor": "Procedural Safety",
            "secondary_precursors": [],
            "primary_hazard": "Operational Hazard Exposure",
            "secondary_hazards": [],
            "life_saving_rule": "Work Authorization & PTW",
            "barriers": [],
            "evidence_spans": [{"text": "Pressure gauge damaged", "start_offset": 0, "end_offset": 22}],
            "urgency_score": 15,
        },
        "annotation": {
            "annotator_id": "HSE-DUAL",
            "review_status": "CONSENSUS_ACCEPTED",
            "taxonomy_version": "1.0",
        },
    }

    auditor = ReleaseGateAuditor()
    report = auditor.audit_dataset_release(
        dataset_id="sift_dataset_test",
        version="1.0.0",
        validated_records=[valid_record],
        train_records=[valid_record],
        val_records=[],
        test_records=[],
    )

    assert report.is_release_approved is True
    assert report.critical_failures == 0
    assert report.total_records == 1


def test_release_gate_rejects_unresolved_annotation():
    """Verify release gate rejects datasets containing unadjudicated records."""
    pending_record = {
        "schema_version": "1.0",
        "report_id": "REL-PEND-01",
        "raw_text": "Sample text for pending review observation.",
        "report_type": "Unsafe Condition",
        "context": {"facility_id": "FAC-DUL-01", "activity": "Maintenance"},
        "labels": {
            "sif_potential": "LOW",
            "sif_precursor": "NO",
            "primary_precursor": "Procedural Safety",
            "secondary_precursors": [],
            "primary_hazard": "Operational Hazard Exposure",
            "secondary_hazards": [],
            "life_saving_rule": "Work Authorization & PTW",
            "barriers": [],
            "evidence_spans": [],
            "urgency_score": 15,
        },
        "annotation": {
            "annotator_id": "HSE-01",
            "review_status": "ADJUDICATION_REQUIRED",  # Not ready!
            "taxonomy_version": "1.0",
        },
    }

    auditor = ReleaseGateAuditor()
    report = auditor.audit_dataset_release(
        dataset_id="sift_dataset_test",
        version="1.0.0",
        validated_records=[pending_record],
    )

    assert report.is_release_approved is False
    assert report.critical_failures >= 1
    assert any(c.gate_name == "ANNOTATION_RESOLUTION" and not c.passed for c in report.gate_checks)
