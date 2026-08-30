"""Tests for SIFT Multi-Faceted Agreement: Cohen's Kappa, Multi-Label Jaccard & Span IoU."""

import pytest
from data_pipeline.annotations import (
    compute_cohens_kappa,
    compute_jaccard_similarity,
    compute_span_iou,
    AnnotationManager,
    AnnotationSubmission,
)


def test_jaccard_similarity_calculation():
    """Verify exact calculation of multi-label set similarity."""
    set_a = {"Energy Isolation", "Confined Space"}
    set_b = {"Energy Isolation", "Working at Height"}
    # Intersection: 1 ("Energy Isolation"), Union: 3 ("Energy Isolation", "Confined Space", "Working at Height")
    sim = compute_jaccard_similarity(set_a, set_b)
    assert pytest.approx(sim, 0.001) == 1.0 / 3.0

    # Both empty
    assert compute_jaccard_similarity(set(), set()) == 1.0


def test_span_character_iou():
    """Verify character-level Intersection over Union for evidence spans."""
    # Span A: [10:30] (length 20)
    spans_a = [{"text": "sample text phrase", "start_offset": 10, "end_offset": 30}]
    # Span B: [20:40] (length 20)
    spans_b = [{"text": "text phrase extra", "start_offset": 20, "end_offset": 40}]
    # Overlap: [20:30] (10 chars), Union: [10:40] (30 chars) -> IoU = 10/30 = 0.3333
    iou = compute_span_iou(spans_a, spans_b)
    assert pytest.approx(iou, 0.001) == 1.0 / 3.0

    # Exact match
    assert compute_span_iou(spans_a, spans_a) == 1.0


def test_inter_annotator_agreement_with_disagreements():
    """Verify full agreement audit catches discrepancies and generates field-level items."""
    sub_a = AnnotationSubmission(
        report_id="REP-DISC-01",
        annotator_id="ANN-A",
        raw_text="40 bar gas leak during valve overhaul.",
        labels={
            "sif_potential": "CRITICAL",
            "primary_precursor": "Energy Isolation",
            "primary_hazard": "Stored / Pressurized Hydrocarbon Energy",
            "life_saving_rule": "Energy Isolation",
            "evidence_spans": [{"text": "40 bar gas leak", "start_offset": 0, "end_offset": 15}],
        },
    )
    # Annotator B disagrees on SIF Potential and Life-Saving Rule
    sub_b = AnnotationSubmission(
        report_id="REP-DISC-01",
        annotator_id="ANN-B",
        raw_text="40 bar gas leak during valve overhaul.",
        labels={
            "sif_potential": "HIGH",
            "primary_precursor": "Energy Isolation",
            "primary_hazard": "Stored / Pressurized Hydrocarbon Energy",
            "life_saving_rule": "Work Authorization & PTW",
            "evidence_spans": [{"text": "40 bar gas leak", "start_offset": 0, "end_offset": 15}],
        },
    )

    mgr = AnnotationManager()
    rep, consensus = mgr.audit_inter_annotator_agreement([sub_a], [sub_b])

    assert rep.total_paired_records == 1
    assert rep.unanimous_consensus_count == 0
    assert rep.discrepancy_count == 1
    assert "REP-DISC-01" in rep.requires_adjudication_ids
    assert len(rep.disagreements) >= 2  # sif_potential and life_saving_rule
    assert any(d.field_name == "sif_potential" for d in rep.disagreements)
