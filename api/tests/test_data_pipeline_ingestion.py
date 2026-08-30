"""Tests for SIFT Data Ingestion Engine (JSON, JSONL, CSV, Database Export)."""

import os
import tempfile
import pytest
from data_pipeline.ingestion import DataIngester, DatabaseExporter


def test_ingest_jsonl_fixture():
    """Verify ingestion of standard JSONL fixture file."""
    fixture_path = os.path.abspath("data/fixtures/sample_raw_reports.jsonl")
    ingester = DataIngester()
    records = ingester.ingest_file(fixture_path)
    
    assert len(records) == 5
    assert all(r.is_eligible for r in records)
    assert records[0].source_record_id == "SIF-2026-00001"
    assert "drill pipes" in records[0].raw_data["raw_text"]


def test_ingest_csv_fixture():
    """Verify ingestion and column mapping of CSV fixture file."""
    fixture_path = os.path.abspath("data/fixtures/sample_raw_reports.csv")
    ingester = DataIngester()
    records = ingester.ingest_file(fixture_path)
    
    assert len(records) == 2
    assert records[0].source_record_id == "SIF-2026-00010"
    assert records[0].raw_data["context"]["facility_id"] == "FAC-DUL-01"
    assert records[0].raw_data["labels"]["sif_potential"] == "CRITICAL"
    # Check evidence span auto-offset calculation from CSV
    spans = records[0].raw_data["labels"]["evidence_spans"]
    assert len(spans) == 1
    assert spans[0]["text"] == "35 bar gas pressure had not been isolated or bled down"


def test_ingest_invalid_format_raises(tmp_path):
    """Verify unsupported file extension raises ValueError."""
    dummy_file = tmp_path / "test.xyz"
    dummy_file.write_text("sample content")
    
    ingester = DataIngester()
    with pytest.raises(ValueError, match="Unsupported file format"):
        ingester.ingest_file(str(dummy_file))


def test_database_exporter_eligibility():
    """Verify eligibility filter accepts adjudicated records and rejects unreviewed ones."""
    eligible_rep = {
        "report_id": "SIF-2026-00099",
        "raw_report_text": "High pressure gas leak detected at flange #4.",
        "review_status": "ADJUDICATED",
        "final_sif_potential": "CRITICAL",
        "final_life_saving_rule": "Energy Isolation",
    }
    is_el, reason = DatabaseExporter.evaluate_training_eligibility(eligible_rep)
    assert is_el is True
    assert reason is None

    ineligible_rep = {
        "report_id": "SIF-2026-00100",
        "raw_report_text": "Minor housekeeping observation.",
        "review_status": "PENDING",
        "final_sif_potential": None,
    }
    is_el2, reason2 = DatabaseExporter.evaluate_training_eligibility(ineligible_rep)
    assert is_el2 is False
    assert "Human specialist sign-off is required" in reason2
