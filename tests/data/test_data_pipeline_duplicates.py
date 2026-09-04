"""Tests for SIFT Exact Deduplication & Near-Duplicate Cluster Detection."""

from data_pipeline.duplicates import DuplicateDetector, DuplicateType


def test_exact_duplicate_detection():
    """Verify SHA-256 content hashing detects exact duplicates."""
    records = [
        {"report_id": "REC-01", "raw_text": "While tripping drill pipes on Rig-42, wire rope snapped."},
        {"report_id": "REC-02", "raw_text": "While tripping drill pipes on Rig-42, wire rope snapped."},
        {"report_id": "REC-03", "raw_text": "Routine inspection completed at gas compressor skid."},
    ]
    
    detector = DuplicateDetector()
    results, matches = detector.process_corpus(records)
    
    assert results["REC-01"].duplicate_type == DuplicateType.UNIQUE
    assert results["REC-02"].duplicate_type == DuplicateType.EXACT_DUPLICATE
    assert results["REC-02"].exact_duplicate_of == "REC-01"
    assert results["REC-01"].cluster_id == results["REC-02"].cluster_id
    assert results["REC-03"].duplicate_type == DuplicateType.UNIQUE


def test_near_duplicate_detection():
    """Verify Jaccard n-gram token similarity catches templated variations."""
    records = [
        {"report_id": "REC-A", "raw_text": "Contract worker noticed scaffold handrail missing at elevation 4.5m on tank roof."},
        {"report_id": "REC-B", "raw_text": "Contract painter noticed scaffold handrail missing at elevation 4.5m on tank roof."},
        {"report_id": "REC-C", "raw_text": "Driver observed uninspected bowser truck operating near flare stack."},
    ]
    
    detector = DuplicateDetector(near_duplicate_threshold=0.75)
    results, matches = detector.process_corpus(records)
    
    assert len(matches) >= 1
    match = matches[0]
    assert match.record_id_a == "REC-A"
    assert match.record_id_b == "REC-B"
    assert match.similarity_score >= 0.75
    # Near duplicates share same cluster ID for leakage prevention
    assert results["REC-A"].cluster_id == results["REC-B"].cluster_id
