"""SIFT Dataset Metrics, Distributions & Quality Analytics.

Computes multi-label precursor frequencies, categorical class distributions,
evidence span coverage statistics, and data quality indicators.
"""

from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DatasetStatistics(BaseModel):
    """Aggregate statistics and multidimensional label distributions."""
    total_records: int = 0
    sif_potential_distribution: Dict[str, int] = Field(default_factory=dict)
    sif_potential_pct: Dict[str, float] = Field(default_factory=dict)
    sif_precursor_distribution: Dict[str, int] = Field(default_factory=dict)
    precursor_categories_distribution: Dict[str, int] = Field(default_factory=dict)
    primary_hazards_distribution: Dict[str, int] = Field(default_factory=dict)
    life_saving_rules_distribution: Dict[str, int] = Field(default_factory=dict)
    activities_distribution: Dict[str, int] = Field(default_factory=dict)
    barrier_statuses_distribution: Dict[str, int] = Field(default_factory=dict)
    report_types_distribution: Dict[str, int] = Field(default_factory=dict)
    facilities_distribution: Dict[str, int] = Field(default_factory=dict)
    
    # Evidence Span Stats
    total_evidence_spans: int = 0
    avg_spans_per_record: float = 0.0
    records_with_zero_spans: int = 0
    avg_span_length_chars: float = 0.0


class DatasetMetricsCalculator:
    """Calculates comprehensive dataset statistics and class distribution breakdowns."""

    @staticmethod
    def calculate(records: List[Dict[str, Any]]) -> DatasetStatistics:
        """Calculate complete statistics over a list of DatasetRecord dicts."""
        n = len(records)
        if n == 0:
            return DatasetStatistics()

        sif_counts = Counter()
        sif_prec_counts = Counter()
        prec_counts = Counter()
        hazard_counts = Counter()
        lsr_counts = Counter()
        activity_counts = Counter()
        barrier_counts = Counter()
        type_counts = Counter()
        facility_counts = Counter()

        total_spans = 0
        zero_span_count = 0
        total_span_chars = 0

        for r in records:
            # Report Type
            r_type = r.get("report_type", "Unknown")
            type_counts[r_type] += 1

            # Context
            ctx = r.get("context", {})
            fac = ctx.get("facility_id", "Unknown")
            facility_counts[fac] += 1
            act = ctx.get("activity", "Unknown")
            activity_counts[act] += 1

            # Labels
            labels = r.get("labels", {})
            
            sif = str(labels.get("sif_potential", "Unknown")).upper()
            sif_counts[sif] += 1

            sif_p = str(labels.get("sif_precursor", "Unknown")).upper()
            sif_prec_counts[sif_p] += 1

            # Multi-label precursors (primary + secondary)
            prim_prec = labels.get("primary_precursor")
            if prim_prec:
                prec_counts[str(prim_prec)] += 1
            for sec_p in labels.get("secondary_precursors", []):
                prec_counts[str(sec_p)] += 1

            # Hazards
            haz = labels.get("primary_hazard")
            if haz:
                hazard_counts[str(haz)] += 1

            # Life Saving Rules
            lsr = labels.get("life_saving_rule")
            if lsr:
                lsr_counts[str(lsr)] += 1

            # Barriers
            for b in labels.get("barriers", []):
                st = str(b.get("status", "UNKNOWN")).upper()
                barrier_counts[st] += 1

            # Spans
            spans = labels.get("evidence_spans", [])
            span_len = len(spans)
            total_spans += span_len
            if span_len == 0:
                zero_span_count += 1
            for sp in spans:
                txt = sp.get("text", "")
                total_span_chars += len(txt)

        sif_pct = {k: round((v / n) * 100, 2) for k, v in sif_counts.items()}
        avg_spans = round(total_spans / n, 2)
        avg_span_len = round(total_span_chars / total_spans, 2) if total_spans > 0 else 0.0

        return DatasetStatistics(
            total_records=n,
            sif_potential_distribution=dict(sif_counts.most_common()),
            sif_potential_pct=sif_pct,
            sif_precursor_distribution=dict(sif_prec_counts.most_common()),
            precursor_categories_distribution=dict(prec_counts.most_common()),
            primary_hazards_distribution=dict(hazard_counts.most_common()),
            life_saving_rules_distribution=dict(lsr_counts.most_common()),
            activities_distribution=dict(activity_counts.most_common()),
            barrier_statuses_distribution=dict(barrier_counts.most_common()),
            report_types_distribution=dict(type_counts.most_common()),
            facilities_distribution=dict(facility_counts.most_common()),
            total_evidence_spans=total_spans,
            avg_spans_per_record=avg_spans,
            records_with_zero_spans=zero_span_count,
            avg_span_length_chars=avg_span_len,
        )
