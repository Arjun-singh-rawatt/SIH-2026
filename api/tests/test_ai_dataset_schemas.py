"""Tests for SIFT AI Dataset & Taxonomy Pydantic Schemas."""

import pytest
from pydantic import ValidationError
from app.schemas.ai.taxonomy import (
    SIFPotentialLevel,
    SIFPrecursorFlag,
    PrecursorCategory,
    PrimaryHazardType,
    BarrierStatusLevel,
    SafetyBarrierCategory,
)
from app.schemas.ai.dataset import (
    DatasetRecord,
    DatasetContext,
    DatasetLabels,
    DatasetAnnotationMetadata,
    DatasetEvidenceSpan,
    DatasetBarrierAssessment,
)
from app.schemas.ai.contract import (
    ModelInferenceRequest,
    ModelInferenceResult,
    ModelConfidenceBreakdown,
    UrgencyScoreBreakdown,
)


def test_dataset_record_valid_serialization():
    """Verify that a valid DatasetRecord serializes and deserializes with exact offset verification."""
    raw_text = (
        "Technician started loosening bolts on the compressor header without proper isolation. "
        "The line was still pressurized with 35 bar natural gas."
    )
    
    # "without proper isolation" starts at index 57, ends at 81
    start_1 = raw_text.index("without proper isolation")
    end_1 = start_1 + len("without proper isolation")

    # "still pressurized with 35 bar natural gas" starts at index 96
    start_2 = raw_text.index("still pressurized with 35 bar natural gas")
    end_2 = start_2 + len("still pressurized with 35 bar natural gas")

    record_data = {
        "schema_version": "1.0",
        "report_id": "SIF-2026-00124",
        "split": "TRAIN",
        "raw_text": raw_text,
        "report_type": "Near Miss",
        "context": {
            "facility_id": "FAC-DIG-02",
            "facility_name": "Digboi Field Complex",
            "region": "Upper Assam Basin",
            "location": "Compressor Area, Train-2",
            "activity": "Maintenance",
        },
        "labels": {
            "sif_potential": SIFPotentialLevel.CRITICAL.value,
            "sif_precursor": SIFPrecursorFlag.YES.value,
            "primary_precursor": PrecursorCategory.ENERGY_ISOLATION.value,
            "secondary_precursors": [PrecursorCategory.PROCESS_SAFETY.value],
            "primary_hazard": PrimaryHazardType.STORED_HYDROCARBON_PRESSURE.value,
            "secondary_hazards": [],
            "life_saving_rule": "Energy Isolation",
            "barriers": [
                {
                    "barrier_name": "Zero Energy Verification & Isolation Certificate",
                    "status": BarrierStatusLevel.FAILED.value,
                    "barrier_type": SafetyBarrierCategory.ENGINEERING.value,
                    "description": "Loosened bolts on pressurized 35 bar line without LOTO",
                }
            ],
            "evidence_spans": [
                {
                    "text": "without proper isolation",
                    "start_offset": start_1,
                    "end_offset": end_1,
                },
                {
                    "text": "still pressurized with 35 bar natural gas",
                    "start_offset": start_2,
                    "end_offset": end_2,
                },
            ],
            "urgency_score": 96,
            "potential_consequence": "High-pressure gas explosion and fatal shrapnel impact.",
            "ai_explanation": "Flange unbolted without positive isolation on active 35 bar hydrocarbon header.",
        },
        "annotation": {
            "annotator_id": "HSE-EXP-01",
            "adjudicator_id": "HSE-LEAD-01",
            "review_status": "ADJUDICATED",
            "taxonomy_version": "1.0",
        },
    }

    record = DatasetRecord(**record_data)
    assert record.report_id == "SIF-2026-00124"
    assert record.labels.sif_potential == SIFPotentialLevel.CRITICAL
    assert len(record.labels.evidence_spans) == 2
    assert record.labels.evidence_spans[0].text == "without proper isolation"

    # Test JSON round-trip
    json_str = record.model_dump_json()
    reloaded = DatasetRecord.model_validate_json(json_str)
    assert reloaded.report_id == record.report_id


def test_dataset_record_invalid_span_offset_raises_error():
    """Verify that a span text mismatch or offset out-of-bounds raises a ValidationError."""
    raw_text = "Valve was leaking 10 bar gas into the compressor room."
    
    with pytest.raises(ValidationError) as excinfo:
        DatasetRecord(
            schema_version="1.0",
            report_id="SIF-2026-00999",
            raw_text=raw_text,
            report_type="Unsafe Condition",
            context={
                "facility_id": "FAC-DIG-02",
                "activity": "Maintenance",
            },
            labels={
                "sif_potential": "HIGH",
                "sif_precursor": "YES",
                "primary_precursor": "Energy Isolation",
                "primary_hazard": "Stored / Pressurized Hydrocarbon Energy",
                "life_saving_rule": "Energy Isolation",
                "evidence_spans": [
                    {
                        "text": "incorrect span text",
                        "start_offset": 0,
                        "end_offset": 10,
                    }
                ],
                "urgency_score": 85,
            },
            annotation={
                "annotator_id": "HSE-EXP-01",
            },
        )
    assert "Span text mismatch" in str(excinfo.value)


def test_model_inference_contract():
    """Verify that ModelInferenceRequest and ModelInferenceResult instantiate properly."""
    req = ModelInferenceRequest(
        report_text="Wire rope on hoist snapped under load.",
        report_type="Near Miss",
        facility_id="FAC-NHK-06",
    )
    assert req.facility_id == "FAC-NHK-06"

    res = ModelInferenceResult(
        model_version="sift-deberta-v1.0",
        sif_potential=SIFPotentialLevel.CRITICAL,
        sif_precursor=SIFPrecursorFlag.YES,
        primary_precursor=PrecursorCategory.LIFTING_OPERATIONS,
        primary_hazard="Dropped Heavy Object / Line of Fire",
        activity="Drilling Operations",
        life_saving_rule="Safe Mechanical Lifting",
        barriers=[],
        evidence_spans=[],
        primary_evidence_phrase="Wire rope snapped",
        ai_explanation="Mechanical rigging failure during lifting operations.",
        confidence=96.0,
        urgency_score=95,
    )
    assert res.sif_potential == SIFPotentialLevel.CRITICAL
    assert res.confidence == 96.0
