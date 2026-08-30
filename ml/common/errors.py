"""SIFT False-Negative Extraction & Root-Cause Error Analyzer.

Isolates safety-critical False Negatives (actual High/Critical SIF misclassified as Low/Non-SIF)
and classifies probable root causes according to the SIFT evaluation protocol.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FalseNegativeRecord(BaseModel):
    """Details of a single safety-critical False Negative observation."""
    report_id: str
    actual_label: str
    predicted_label: str
    text_excerpt: str
    decision_score: Optional[float] = None
    predicted_scores: Dict[str, float] = Field(default_factory=dict)
    diagnostic_category: str = "UNKNOWN"
    notes: Optional[str] = None


class ErrorAnalysisReport(BaseModel):
    """Aggregate error analysis and false-negative audit report."""
    total_samples: int
    total_misclassifications: int
    total_high_sif_false_negatives: int
    high_sif_fn_breakdown: Dict[str, int] = Field(default_factory=dict)
    false_negative_records: List[FalseNegativeRecord] = Field(default_factory=list)


class FalseNegativeAnalyzer:
    """Extracts and categorizes safety-critical false negatives."""

    HIGH_SIF_CLASSES = {"CRITICAL", "HIGH"}
    LOW_SIF_CLASSES = {"MEDIUM", "LOW", "NON-SIF"}

    @classmethod
    def analyze(
        cls,
        report_ids: List[str],
        texts: List[str],
        y_true: List[str],
        y_pred: List[str],
        decision_scores: Optional[List[Dict[str, float]]] = None,
    ) -> ErrorAnalysisReport:
        """Analyze predictions to isolate and categorize High-SIF false negatives."""
        total = len(y_true)
        misclassified = 0
        fn_records: List[FalseNegativeRecord] = []
        fn_breakdown: Dict[str, int] = {}

        for i in range(total):
            actual = y_true[i].upper()
            pred = y_pred[i].upper()
            r_id = report_ids[i] if i < len(report_ids) else f"REC-{i}"
            raw = texts[i] if i < len(texts) else ""
            scores = decision_scores[i] if decision_scores and i < len(decision_scores) else {}

            if actual != pred:
                misclassified += 1

                # Check if this is a High-SIF False Negative
                if actual in cls.HIGH_SIF_CLASSES and pred in cls.LOW_SIF_CLASSES:
                    transition = f"{actual} -> {pred}"
                    fn_breakdown[transition] = fn_breakdown.get(transition, 0) + 1

                    # Diagnostic heuristic
                    diag = cls._diagnose_failure(raw, actual, pred)

                    # Text excerpt (first 120 chars)
                    excerpt = (raw[:120] + "...") if len(raw) > 120 else raw

                    fn_records.append(FalseNegativeRecord(
                        report_id=r_id,
                        actual_label=actual,
                        predicted_label=pred,
                        text_excerpt=excerpt,
                        decision_score=scores.get(pred),
                        predicted_scores=scores,
                        diagnostic_category=diag,
                    ))

        return ErrorAnalysisReport(
            total_samples=total,
            total_misclassifications=misclassified,
            total_high_sif_false_negatives=len(fn_records),
            high_sif_fn_breakdown=fn_breakdown,
            false_negative_records=fn_records,
        )

    @classmethod
    def _diagnose_failure(cls, text: str, actual: str, pred: str) -> str:
        """Assign diagnostic failure category based on text characteristics."""
        t_lower = text.lower()
        if len(text.split()) < 8:
            return "INSUFFICIENT_CONTEXT"
        if any(w in t_lower for w in ["near miss", "unbolted", "pressurized", "h2s", "snapped", "collapsed"]):
            return "CLASS_IMBALANCE_OR_WEAK_WEIGHT"
        if any(w in t_lower for w in ["routine", "clean", "inspected", "housekeeping"]):
            return "AMBIGUOUS_NARRATIVE"
        return "UNKNOWN"
