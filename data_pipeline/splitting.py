"""SIFT Leakage-Safe Temporal & Event-Grouped Dataset Splitting.

Enforces strict temporal out-of-time evaluation, incident event grouping,
near-duplicate cluster isolation, and High-SIF representation auditing.
"""

from datetime import datetime
import math
import random
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field


class SplitConfig(BaseModel):
    """Configuration parameters for dataset splitting."""
    train_ratio: float = Field(default=0.70, gt=0.0, lt=1.0)
    val_ratio: float = Field(default=0.15, gt=0.0, lt=1.0)
    test_ratio: float = Field(default=0.15, gt=0.0, lt=1.0)
    train_end_date: Optional[str] = None
    val_end_date: Optional[str] = None
    random_seed: int = Field(default=42)
    min_high_sif_test_count: int = Field(default=3)


class SplitMetrics(BaseModel):
    """Distribution metrics per split."""
    total_records: int
    train_count: int
    val_count: int
    test_count: int
    train_high_sif_count: int
    val_high_sif_count: int
    test_high_sif_count: int
    high_sif_test_pct: float
    warnings: List[str] = Field(default_factory=list)


class SplitResult:
    """Outcome of dataset partitioning."""
    def __init__(
        self,
        train_records: List[Dict[str, Any]],
        val_records: List[Dict[str, Any]],
        test_records: List[Dict[str, Any]],
        metrics: SplitMetrics,
        leakage_passed: bool,
    ):
        self.train_records = train_records
        self.val_records = val_records
        self.test_records = test_records
        self.metrics = metrics
        self.leakage_passed = leakage_passed


class DatasetSplitter:
    """Partitions validated dataset records into Train, Validation, and Test splits."""

    def __init__(self, config: Optional[SplitConfig] = None):
        self.config = config or SplitConfig()

    def _extract_timestamp(self, record: Dict[str, Any]) -> datetime:
        """Extract a sorting timestamp from record metadata."""
        # Try annotated_at, created_at, timestamp, or fallback to epoch
        ann = record.get("annotation", {})
        ts_str = ann.get("annotated_at") or record.get("created_at") or record.get("timestamp")
        if ts_str:
            try:
                # Replace 'Z' with '+00:00' for ISO compatibility
                clean_ts = str(ts_str).replace("Z", "+00:00")
                return datetime.fromisoformat(clean_ts)
            except Exception:
                pass
        return datetime(2026, 1, 1)

    def _extract_event_group(self, record: Dict[str, Any], cluster_id: Optional[str] = None) -> str:
        """Extract or assign incident/event group identifier."""
        # 1. Check explicit event metadata
        event_id = (
            record.get("event_id")
            or record.get("incident_id")
            or record.get("investigation_id")
            or record.get("context", {}).get("event_id")
        )
        if event_id:
            return f"EVENT-{event_id}"
            
        # 2. Check cluster_id from near-duplicate detection
        if cluster_id:
            return f"CLUSTER-{cluster_id}"
            
        # 3. Fallback to report_id (unique group of 1)
        return f"REC-{record.get('report_id', 'UNKNOWN')}"

    def split(
        self,
        records: List[Dict[str, Any]],
        record_clusters: Optional[Dict[str, str]] = None,
    ) -> SplitResult:
        """Execute temporal, event-grouped splitting on validated records.
        
        Args:
            records: List of validated DatasetRecord dictionaries.
            record_clusters: Optional mapping of report_id -> cluster_id from duplicate detector.
            
        Returns:
            SplitResult containing partitioned records, split distribution metrics, and leakage status.
        """
        if not records:
            empty_metrics = SplitMetrics(
                total_records=0,
                train_count=0,
                val_count=0,
                test_count=0,
                train_high_sif_count=0,
                val_high_sif_count=0,
                test_high_sif_count=0,
                high_sif_test_pct=0.0,
            )
            return SplitResult([], [], [], empty_metrics, leakage_passed=True)

        record_clusters = record_clusters or {}

        # 1. Group records by event / cluster
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for r in records:
            r_id = r.get("report_id", "")
            c_id = record_clusters.get(r_id)
            grp_key = self._extract_event_group(r, c_id)
            if grp_key not in groups:
                groups[grp_key] = []
            groups[grp_key].append(r)

        # 2. Determine representative timestamp for each group (earliest timestamp in group)
        group_tuples: List[Tuple[datetime, str, List[Dict[str, Any]]]] = []
        for grp_key, grp_records in groups.items():
            earliest_ts = min(self._extract_timestamp(r) for r in grp_records)
            group_tuples.append((earliest_ts, grp_key, grp_records))

        # 3. Sort groups chronologically
        # Use deterministic random seed for tie-breaking on identical timestamps
        rng = random.Random(self.config.random_seed)
        # Add random float tie-breaker to ensure deterministic sort order
        decorated = [(ts, rng.random(), grp_key, recs) for ts, grp_key, recs in group_tuples]
        decorated.sort(key=lambda x: (x[0], x[1]))

        # 4. Partition groups into Train, Val, Test
        total_items = len(records)
        train_target = int(total_items * self.config.train_ratio)
        val_target = int(total_items * self.config.val_ratio)

        train_recs: List[Dict[str, Any]] = []
        val_recs: List[Dict[str, Any]] = []
        test_recs: List[Dict[str, Any]] = []

        train_groups: Set[str] = set()
        val_groups: Set[str] = set()
        test_groups: Set[str] = set()

        current_count = 0
        for ts, _, grp_key, grp_records in decorated:
            # Check if explicit date boundaries are configured
            if self.config.train_end_date and self.config.val_end_date:
                t_end = datetime.fromisoformat(self.config.train_end_date)
                v_end = datetime.fromisoformat(self.config.val_end_date)
                if ts <= t_end:
                    target_split = "TRAIN"
                elif ts <= v_end:
                    target_split = "VALIDATION"
                else:
                    target_split = "TEST"
            else:
                # Ratio-based temporal assignment
                if len(train_recs) < train_target or (len(val_recs) == 0 and len(test_recs) == 0 and len(train_recs) + len(grp_records) <= train_target):
                    target_split = "TRAIN"
                elif len(val_recs) < val_target:
                    target_split = "VALIDATION"
                else:
                    target_split = "TEST"

            # Assign split property on record copy
            for r in grp_records:
                r_copy = dict(r)
                r_copy["split"] = target_split
                if target_split == "TRAIN":
                    train_recs.append(r_copy)
                    train_groups.add(grp_key)
                elif target_split == "VALIDATION":
                    val_recs.append(r_copy)
                    val_groups.add(grp_key)
                else:
                    test_recs.append(r_copy)
                    test_groups.add(grp_key)

        # 5. Verify Zero Group / Cluster Leakage across splits
        overlap_train_val = train_groups.intersection(val_groups)
        overlap_train_test = train_groups.intersection(test_groups)
        overlap_val_test = val_groups.intersection(test_groups)
        
        leakage_passed = (
            len(overlap_train_val) == 0
            and len(overlap_train_test) == 0
            and len(overlap_val_test) == 0
        )

        # 6. Audit High-SIF representation
        def count_high_sif(recs: List[Dict[str, Any]]) -> int:
            return sum(
                1 for r in recs
                if str(r.get("labels", {}).get("sif_potential", "")).upper() in {"CRITICAL", "HIGH"}
            )

        train_high = count_high_sif(train_recs)
        val_high = count_high_sif(val_recs)
        test_high = count_high_sif(test_recs)

        warnings: List[str] = []
        if not leakage_passed:
            warnings.append(
                f"LEAKAGE DETECTED: Groups cross splits! Train-Val: {overlap_train_val}, Train-Test: {overlap_train_test}, Val-Test: {overlap_val_test}"
            )

        if len(test_recs) > 0 and test_high < self.config.min_high_sif_test_count:
            warnings.append(
                f"HIGH-SIF ALERT: Test split contains only {test_high} CRITICAL/HIGH observations (minimum target: {self.config.min_high_sif_test_count})"
            )

        test_high_pct = (test_high / len(test_recs) * 100) if len(test_recs) > 0 else 0.0

        metrics = SplitMetrics(
            total_records=total_items,
            train_count=len(train_recs),
            val_count=len(val_recs),
            test_count=len(test_recs),
            train_high_sif_count=train_high,
            val_high_sif_count=val_high,
            test_high_sif_count=test_high,
            high_sif_test_pct=round(test_high_pct, 2),
            warnings=warnings,
        )

        return SplitResult(
            train_records=train_recs,
            val_records=val_recs,
            test_records=test_recs,
            metrics=metrics,
            leakage_passed=leakage_passed,
        )
