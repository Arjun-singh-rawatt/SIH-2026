"""Tests for SIFT Dataset Splitting, Event Grouping, and Temporal Leakage Prevention."""

from data_pipeline.splitting import DatasetSplitter, SplitConfig


def test_temporal_event_grouped_splitting():
    """Verify that records sharing event groups remain strictly in the same split with zero leakage."""
    records = [
        {"report_id": "REC-1", "event_id": "EVT-01", "created_at": "2026-01-01T10:00:00Z", "labels": {"sif_potential": "CRITICAL"}},
        {"report_id": "REC-2", "event_id": "EVT-01", "created_at": "2026-01-01T10:05:00Z", "labels": {"sif_potential": "CRITICAL"}},
        {"report_id": "REC-3", "event_id": "EVT-02", "created_at": "2026-02-01T10:00:00Z", "labels": {"sif_potential": "HIGH"}},
        {"report_id": "REC-4", "event_id": "EVT-03", "created_at": "2026-03-01T10:00:00Z", "labels": {"sif_potential": "LOW"}},
        {"report_id": "REC-5", "event_id": "EVT-04", "created_at": "2026-04-01T10:00:00Z", "labels": {"sif_potential": "NON-SIF"}},
    ]
    
    splitter = DatasetSplitter(SplitConfig(train_ratio=0.6, val_ratio=0.2, test_ratio=0.2, random_seed=42))
    res = splitter.split(records)
    
    assert res.leakage_passed is True
    
    # Check that REC-1 and REC-2 (EVT-01) are in the same split
    rec1_split = next(r["split"] for r in res.train_records + res.val_records + res.test_records if r["report_id"] == "REC-1")
    rec2_split = next(r["split"] for r in res.train_records + res.val_records + res.test_records if r["report_id"] == "REC-2")
    assert rec1_split == rec2_split


def test_deterministic_seed_reproducibility():
    """Verify that identical seed produces identical split assignments."""
    records = [
        {"report_id": f"REC-{i}", "created_at": "2026-01-01T10:00:00Z", "labels": {"sif_potential": "LOW"}}
        for i in range(20)
    ]
    
    splitter1 = DatasetSplitter(SplitConfig(random_seed=42))
    res1 = splitter1.split(records)
    
    splitter2 = DatasetSplitter(SplitConfig(random_seed=42))
    res2 = splitter2.split(records)
    
    train1_ids = [r["report_id"] for r in res1.train_records]
    train2_ids = [r["report_id"] for r in res2.train_records]
    assert train1_ids == train2_ids
