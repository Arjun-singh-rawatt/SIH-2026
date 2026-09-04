"""Tests for SIFT Double-Blind Annotation Lifecycle, Inter-Annotator Agreement, and Adjudication."""

import os
from data_pipeline.annotations import (
    AnnotationManager,
    AnnotationSubmission,
    AdjudicationRecord,
    compute_cohens_kappa,
)


def test_double_blind_export_strips_ai_predictions():
    """Verify that export for human annotation strictly removes AI predictions and confidence."""
    raw_reports = [
        {
            "report_id": "SIF-2026-00001",
            "raw_report_text": "High pressure gas leak detected.",
            "report_type": "Near Miss",
            "facility_id": "FAC-DUL-01",
            "activity": "Maintenance",
            "ai_sif_potential": "CRITICAL",
            "ai_confidence": 98.4,
            "ai_explanation": "Severe gas leak.",
        }
    ]
    
    mgr = AnnotationManager()
    tasks = mgr.export_double_blind_batch(raw_reports)
    
    assert len(tasks) == 1
    task = tasks[0]
    assert task["report_id"] == "SIF-2026-00001"
    assert "raw_text" in task
    # Ensure zero AI prediction fields leak
    for k in task.keys():
        assert not k.startswith("ai_")


def test_inter_annotator_agreement_and_kappa():
    """Verify calculation of Cohen's Kappa and discrepancy isolation."""
    subs_a = [
        AnnotationSubmission(
            report_id="REC-01",
            annotator_id="HSE-A",
            raw_text="Text 1",
            report_type="Near Miss",
            context={},
            labels={"sif_potential": "CRITICAL", "primary_precursor": "Energy Isolation", "life_saving_rule": "Energy Isolation"},
        ),
        AnnotationSubmission(
            report_id="REC-02",
            annotator_id="HSE-A",
            raw_text="Text 2",
            report_type="Unsafe Condition",
            context={},
            labels={"sif_potential": "LOW", "primary_precursor": "Procedural Safety", "life_saving_rule": "Work Authorization & PTW"},
        ),
    ]
    
    subs_b = [
        AnnotationSubmission(
            report_id="REC-01",
            annotator_id="HSE-B",
            raw_text="Text 1",
            report_type="Near Miss",
            context={},
            labels={"sif_potential": "CRITICAL", "primary_precursor": "Energy Isolation", "life_saving_rule": "Energy Isolation"},
        ),
        AnnotationSubmission(
            report_id="REC-02",
            annotator_id="HSE-B",
            raw_text="Text 2",
            report_type="Unsafe Condition",
            context={},
            labels={"sif_potential": "HIGH", "primary_precursor": "Procedural Safety", "life_saving_rule": "Work Authorization & PTW"},
        ),
    ]
    
    mgr = AnnotationManager()
    report, consensus = mgr.audit_inter_annotator_agreement(subs_a, subs_b)
    
    assert report.total_paired_records == 2
    assert report.unanimous_consensus_count == 1
    assert report.discrepancy_count == 1
    assert report.requires_adjudication_ids == ["REC-02"]
    assert len(consensus) == 1
    assert consensus[0]["report_id"] == "REC-01"


def test_adjudication_resolution():
    """Verify expert adjudication creates validated record with authoritative metadata."""
    mgr = AnnotationManager()
    base_record = {
        "report_id": "REC-02",
        "raw_text": "Sample observation text",
        "report_type": "Near Miss",
    }
    adjudication = AdjudicationRecord(
        report_id="REC-02",
        adjudicator_id="HSE-LEAD-01",
        resolved_labels={"sif_potential": "HIGH", "primary_precursor": "Procedural Safety"},
        disagreement_notes="Resolved in favor of HIGH due to secondary energy hazard.",
    )
    
    adj_record = mgr.apply_adjudication(base_record, adjudication)
    assert adj_record["annotation"]["review_status"] == "ADJUDICATED"
    assert adj_record["annotation"]["adjudicator_id"] == "HSE-LEAD-01"
    assert adj_record["labels"]["sif_potential"] == "HIGH"
