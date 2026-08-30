"""Tests for SIFT Validation Engine (Schema, Taxonomy, Evidence Spans, Governance)."""

import pytest
from data_pipeline.validation import DatasetValidator


@pytest.fixture
def valid_record_dict():
    return {
        "schema_version": "1.0",
        "report_id": "SIF-2026-00001",
        "raw_text": "While tripping 5-inch drill pipes on Rig-42, the auxiliary air hoist wire rope snapped near the thimble clamp under a 3.2-ton shock load.",
        "report_type": "Near Miss",
        "context": {
            "facility_id": "FAC-NHK-06",
            "facility_name": "Naharkatiya Deep Drilling Hub",
            "region": "Assam Shelf",
            "location": "Rig Floor",
            "activity": "Drilling Operations",
        },
        "labels": {
            "sif_potential": "CRITICAL",
            "sif_precursor": "YES",
            "primary_precursor": "Lifting Operations",
            "secondary_precursors": ["Line of Fire"],
            "primary_hazard": "Dropped Heavy Object / Line of Fire",
            "secondary_hazards": [],
            "life_saving_rule": "Safe Mechanical Lifting",
            "barriers": [
                {
                    "barrier_name": "Rigging Hoist Clamp",
                    "status": "FAILED",
                    "barrier_type": "Engineering / Physical Barrier",
                }
            ],
            "evidence_spans": [
                {
                    "text": "auxiliary air hoist wire rope snapped near the thimble clamp under a 3.2-ton shock load",
                    "start_offset": 49,
                    "end_offset": 136,
                }
            ],
            "urgency_score": 98,
            "potential_consequence": "Fatal impact",
        },
        "annotation": {
            "annotator_id": "HSE-EXP-01",
            "adjudicator_id": "HSE-LEAD-01",
            "review_status": "ADJUDICATED",
            "taxonomy_version": "1.0",
        },
    }


def test_valid_record_passes_validation(valid_record_dict):
    """Verify that a compliant canonical record passes validation without errors."""
    validator = DatasetValidator(strict_taxonomy=True)
    res = validator.validate_record_dict(valid_record_dict)
    assert res.is_valid is True
    assert len(res.errors) == 0


def test_invalid_evidence_span_offset_fails(valid_record_dict):
    """Verify that offset mismatch between raw_text and span text is caught as a validation error."""
    valid_record_dict["labels"]["evidence_spans"][0]["start_offset"] = 0
    valid_record_dict["labels"]["evidence_spans"][0]["end_offset"] = 20
    
    validator = DatasetValidator()
    res = validator.validate_record_dict(valid_record_dict)
    assert res.is_valid is False
    assert any("Exact text mismatch" in e.message or "Span text mismatch" in e.message for e in res.errors)


def test_invalid_taxonomy_enum_fails(valid_record_dict):
    """Verify that unmapped / arbitrary taxonomy strings fail validation."""
    valid_record_dict["labels"]["primary_precursor"] = "Arbitrary Invented Category"
    validator = DatasetValidator(strict_taxonomy=True)
    res = validator.validate_record_dict(valid_record_dict)
    assert res.is_valid is False
    assert len(res.errors) > 0


def test_unresolved_annotation_state_fails(valid_record_dict):
    """Verify that unannotated or disputed records are rejected from dataset validation."""
    valid_record_dict["annotation"]["review_status"] = "ADJUDICATION_REQUIRED"
    validator = DatasetValidator()
    res = validator.validate_record_dict(valid_record_dict)
    assert res.is_valid is False
    assert any("unresolved or incomplete annotation state" in e.message for e in res.errors)
