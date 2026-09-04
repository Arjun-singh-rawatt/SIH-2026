"""Tests for SIFT ML Dataset Loader (Contract Validation, Label Checks, Text Invariants)."""

import os
import pytest
from ml.common.dataset_loader import DatasetSplitLoader


def test_dataset_loader_valid_split():
    """Verify loading of compliant JSONL dataset split."""
    fixture_path = os.path.abspath("data/fixtures/sample_ml_train.jsonl")
    split = DatasetSplitLoader.load_split(fixture_path, "TRAIN")
    
    assert split.split_name == "TRAIN"
    assert split.total_count == 6
    assert len(split.texts) == 6
    assert len(split.labels) == 6
    assert split.high_sif_count >= 3
    assert "CRITICAL" in split.class_distribution


def test_dataset_loader_nonexistent_file_raises():
    """Verify loading non-existent path raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        DatasetSplitLoader.load_split("non_existent_file.jsonl", "TEST")


def test_dataset_loader_rejects_empty_text(tmp_path):
    """Verify records with empty text are strictly rejected."""
    bad_file = tmp_path / "bad_text.jsonl"
    bad_line = (
        '{"schema_version": "1.0", "report_id": "SIF-2026-99999", "raw_text": "   ", '
        '"report_type": "Near Miss", "context": {"facility_id": "F1", "activity": "Maintenance"}, '
        '"labels": {"sif_potential": "CRITICAL", "sif_precursor": "YES", "primary_precursor": "Energy Isolation", '
        '"primary_hazard": "Stored / Pressurized Hydrocarbon Energy", "life_saving_rule": "Energy Isolation", '
        '"barriers": [], "evidence_spans": [], "urgency_score": 90}, '
        '"annotation": {"annotator_id": "HSE-1", "review_status": "ADJUDICATED", "taxonomy_version": "1.0"}}'
    )
    bad_file.write_text(bad_line)

    with pytest.raises(ValueError, match="empty or whitespace-only raw_text|String should have at least 5 characters"):
        DatasetSplitLoader.load_split(str(bad_file), "TRAIN")


def test_dataset_loader_rejects_invalid_label(tmp_path):
    """Verify records with unknown SIF potential labels fail validation."""
    bad_file = tmp_path / "bad_label.jsonl"
    bad_line = (
        '{"schema_version": "1.0", "report_id": "SIF-2026-99998", "raw_text": "Valid safety narrative here.", '
        '"report_type": "Near Miss", "context": {"facility_id": "F1", "activity": "Maintenance"}, '
        '"labels": {"sif_potential": "UNKNOWN_SEVERITY", "sif_precursor": "YES", "primary_precursor": "Energy Isolation", '
        '"primary_hazard": "Stored / Pressurized Hydrocarbon Energy", "life_saving_rule": "Energy Isolation", '
        '"barriers": [], "evidence_spans": [], "urgency_score": 90}, '
        '"annotation": {"annotator_id": "HSE-1", "review_status": "ADJUDICATED", "taxonomy_version": "1.0"}}'
    )
    bad_file.write_text(bad_line)

    with pytest.raises(ValueError):
        DatasetSplitLoader.load_split(str(bad_file), "TRAIN")
