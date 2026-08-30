"""SIFT Machine Learning Dataset Split Loader.

Enforces strict Pydantic DatasetRecord schema compliance, extracts isolated raw_text
features and sif_potential target labels, and audits data contract invariants.
"""

from collections import Counter
import json
import os
import sys
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# Ensure api directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "api")))

from app.schemas.ai.dataset import DatasetRecord
from app.schemas.ai.taxonomy import SIFPotentialLevel


class LoadedDatasetSplit(BaseModel):
    """Container for an ingested and validated dataset split."""
    split_name: str
    filepath: str
    total_count: int
    texts: List[str]
    labels: List[str]
    report_ids: List[str]
    class_distribution: Dict[str, int]
    class_percentages: Dict[str, float]
    high_sif_count: int
    high_sif_percentage: float


class DatasetSplitLoader:
    """Loads and validates JSONL dataset split files for machine learning training."""

    VALID_SIF_LABELS = {e.value for e in SIFPotentialLevel}

    @classmethod
    def load_split(cls, filepath: str, split_name: str = "UNKNOWN") -> LoadedDatasetSplit:
        """Load and strictly validate a dataset split file.
        
        Args:
            filepath: Path to .jsonl split file.
            split_name: Name of partition (e.g. 'TRAIN', 'VALIDATION', 'TEST').
            
        Returns:
            LoadedDatasetSplit instance.
            
        Raises:
            FileNotFoundError: If filepath does not exist.
            ValueError: If schema, label, or text validation fails.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Dataset split file not found: {filepath}")

        texts: List[str] = []
        labels: List[str] = []
        report_ids: List[str] = []
        records_raw: List[Dict[str, Any]] = []

        with open(filepath, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except Exception as e:
                    raise ValueError(f"[{split_name}] Line {line_no}: Invalid JSON: {str(e)}")

                # Validate Pydantic schema
                try:
                    record = DatasetRecord(**data)
                except Exception as e:
                    r_id = data.get("report_id", f"LINE-{line_no}")
                    raise ValueError(f"[{split_name}] Record '{r_id}' failed DatasetRecord contract: {str(e)}")

                # Validate raw text
                raw_text = record.raw_text
                if not raw_text or not raw_text.strip():
                    raise ValueError(
                        f"[{split_name}] Record '{record.report_id}' has empty or whitespace-only raw_text"
                    )

                # Validate target label
                target_label = str(record.labels.sif_potential).upper()
                if target_label not in cls.VALID_SIF_LABELS:
                    raise ValueError(
                        f"[{split_name}] Record '{record.report_id}' has invalid sif_potential '{target_label}'. Must be one of {cls.VALID_SIF_LABELS}"
                    )

                texts.append(raw_text)
                labels.append(target_label)
                report_ids.append(record.report_id)
                records_raw.append(data)

        n = len(texts)
        dist = dict(Counter(labels).most_common())
        pcts = {k: round((v / n) * 100, 2) for k, v in dist.items()} if n > 0 else {}
        high_sif = dist.get("CRITICAL", 0) + dist.get("HIGH", 0)
        high_sif_pct = round((high_sif / n) * 100, 2) if n > 0 else 0.0

        return LoadedDatasetSplit(
            split_name=split_name,
            filepath=filepath,
            total_count=n,
            texts=texts,
            labels=labels,
            report_ids=report_ids,
            class_distribution=dist,
            class_percentages=pcts,
            high_sif_count=high_sif,
            high_sif_percentage=high_sif_pct,
        )
